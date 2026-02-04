import mysql.connector
from mysql.connector import Error
import os
import sys

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import Config

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        return conn
    except Error as e:
        print(f"Error connecting to DB: {e}")
        sys.exit(1)

def run_migration():
    print("Starting database migration...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Create Users Table
        print("Migrating 'users' table...")
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

        # Add bio column if it doesn't exist
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'users') AND (COLUMN_NAME = 'bio')
        """, (Config.DB_NAME,))
        
        if cursor.fetchone()[0] == 0:
            print("Adding bio column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN bio VARCHAR(300)")

        # Add profile_picture column if it doesn't exist
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'users') AND (COLUMN_NAME = 'profile_picture')
        """, (Config.DB_NAME,))
        
        if cursor.fetchone()[0] == 0:
            print("Adding profile_picture column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255)")

        # Add api_token column if it doesn't exist
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'users') AND (COLUMN_NAME = 'api_token')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding api_token column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN api_token VARCHAR(64)")

        # Add role column if it doesn't exist
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'users') AND (COLUMN_NAME = 'role')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding role column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")

        # Add created_at column if it doesn't exist
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'users') AND (COLUMN_NAME = 'created_at')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding created_at column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        # Ensure unique indexes for email and username
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'email' AND NON_UNIQUE = 0
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE UNIQUE INDEX ux_users_email ON users (email)")

        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'username' AND NON_UNIQUE = 0
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("CREATE UNIQUE INDEX ux_users_username ON users (username)")

        # 2. Create Categories Table
        print("Migrating 'categories' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(80) NOT NULL,
                color VARCHAR(20) DEFAULT '#3b82f6',
                is_system BOOLEAN DEFAULT FALSE
            )
        """)

        # Ensure category columns exist (non-destructive)
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'categories') AND (COLUMN_NAME = 'color')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding color column to categories...")
            cursor.execute("ALTER TABLE categories ADD COLUMN color VARCHAR(20) DEFAULT '#3b82f6'")

        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'categories') AND (COLUMN_NAME = 'is_system')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding is_system column to categories...")
            cursor.execute("ALTER TABLE categories ADD COLUMN is_system BOOLEAN DEFAULT FALSE")

        # 3. Insert Default Categories (Idempotent)
        cursor.execute("SELECT name FROM categories")
        existing_category_names = {row[0].strip().lower() for row in cursor.fetchall() if row[0]}

        default_cats = [
            ("Docker", "#3b82f6"),
            ("Kubernetes", "#6366f1"),
            ("Linux", "#22c55e"),
            ("CI/CD", "#f59e0b"),
            ("AWS", "#f97316"),
            ("Monitoring", "#a855f7"),
            ("Other", "#64748b")
        ]

        for name, color in default_cats:
            if name.lower() not in existing_category_names:
                cursor.execute(
                    "INSERT INTO categories (name, color, is_system) VALUES (%s, %s, TRUE)",
                    (name, color)
                )

        # 4. Update Notes Table (Add missing columns)
        print("Migrating 'notes' table schema...")

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

        # Add user_id column if missing
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'user_id')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding user_id column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN user_id INT")

        # Add is_public column if missing
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'is_public')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding is_public column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN is_public BOOLEAN DEFAULT FALSE")

        # Add public_id column if missing
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'public_id')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding public_id column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN public_id VARCHAR(36)")

        # Add created_at column if missing
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'created_at')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding created_at column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        # Add example column if missing
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'example')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding example column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN example TEXT")

        # Add tags column if missing
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'tags')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding tags column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN tags VARCHAR(500)")

        # Add category column if missing
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'category')
        """, (Config.DB_NAME,))
        if cursor.fetchone()[0] == 0:
            print("Adding category column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN category VARCHAR(50)")

        # Ensure foreign key exists (best-effort)
        cursor.execute("""
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'notes'
              AND COLUMN_NAME = 'user_id' AND REFERENCED_TABLE_NAME = 'users'
        """, (Config.DB_NAME,))
        if cursor.fetchone() is None:
            try:
                cursor.execute("ALTER TABLE notes ADD CONSTRAINT fk_notes_users FOREIGN KEY (user_id) REFERENCES users(id)")
            except Error:
                # Ignore if constraint already exists with a different name or if data is inconsistent
                pass

        conn.commit()
        print("Migration completed successfully! ✅")

    except Error as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()
