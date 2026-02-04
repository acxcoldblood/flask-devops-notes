import time
import mysql.connector
from mysql.connector import Error
from app.config import Config


def get_db_connection(retries=10, delay=2):
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
            )
            return conn
        except Error as e:
            print(f"DB not ready ({attempt + 1}/{retries}): {e}")
            time.sleep(delay)

    raise Exception("Database connection failed after retries")


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            email VARCHAR(120) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            api_token VARCHAR(64),
            bio VARCHAR(300),
            profile_picture VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(80) NOT NULL,
            color VARCHAR(20) DEFAULT '#3b82f6',
            is_system BOOLEAN DEFAULT FALSE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            command VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50),
            example TEXT,
            tags VARCHAR(500),
            user_id INT,
            is_public BOOLEAN DEFAULT FALSE,
            public_id VARCHAR(36),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ensure expected columns exist for existing tables (non-destructive)
    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'notes'
    """)
    existing_notes_cols = {row[0] for row in cursor.fetchall()}
    if "user_id" not in existing_notes_cols:
        cursor.execute("ALTER TABLE notes ADD COLUMN IF NOT EXISTS user_id INT")
    if "is_public" not in existing_notes_cols:
        cursor.execute("ALTER TABLE notes ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE")
    if "public_id" not in existing_notes_cols:
        cursor.execute("ALTER TABLE notes ADD COLUMN IF NOT EXISTS public_id VARCHAR(36)")
    if "created_at" not in existing_notes_cols:
        cursor.execute("ALTER TABLE notes ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users'
    """)
    existing_user_cols = {row[0] for row in cursor.fetchall()}
    if "role" not in existing_user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user'")
    if "api_token" not in existing_user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS api_token VARCHAR(64)")
    if "bio" not in existing_user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio VARCHAR(300)")
    if "profile_picture" not in existing_user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(255)")
    if "created_at" not in existing_user_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # Ensure unique constraints for users
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'email' AND NON_UNIQUE = 0
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE UNIQUE INDEX ux_users_email ON users (email)")
    except mysql.connector.Error as err:
        if err.errno == 1061:  # Duplicate key name
            pass
        else:
            raise

    try:
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' AND COLUMN_NAME = 'username' AND NON_UNIQUE = 0
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE UNIQUE INDEX ux_users_username ON users (username)")
    except mysql.connector.Error as err:
        if err.errno == 1061:  # Duplicate key name
            pass
        else:
            raise

    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'categories'
    """)
    existing_category_cols = {row[0] for row in cursor.fetchall()}
    if "color" not in existing_category_cols:
        cursor.execute("ALTER TABLE categories ADD COLUMN IF NOT EXISTS color VARCHAR(20) DEFAULT '#3b82f6'")
    if "is_system" not in existing_category_cols:
        cursor.execute("ALTER TABLE categories ADD COLUMN IF NOT EXISTS is_system BOOLEAN DEFAULT FALSE")

    cursor.execute("SELECT name FROM categories")
    existing_category_names = {row[0].strip().lower() for row in cursor.fetchall() if row[0]}

    default_categories = [
        ("Docker", "#3b82f6"),
        ("Kubernetes", "#6366f1"),
        ("Linux", "#22c55e"),
        ("CI/CD", "#f59e0b"),
        ("AWS", "#f97316"),
        ("Monitoring", "#a855f7"),
        ("Other", "#64748b"),
    ]

    for name, color in default_categories:
        if name.lower() not in existing_category_names:
            cursor.execute("INSERT INTO categories (name, color, is_system) VALUES (%s, %s, TRUE)", (name, color))

    conn.commit()
    cursor.close()
    conn.close()

    print("Database initialized successfully")
