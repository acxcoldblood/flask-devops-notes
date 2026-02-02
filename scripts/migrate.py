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
                username VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                bio TEXT,
                profile_picture VARCHAR(255),
                api_token VARCHAR(64),
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
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")

        # Add profile_picture column if it doesn't exist
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'users') AND (COLUMN_NAME = 'profile_picture')
        """, (Config.DB_NAME,))
        
        if cursor.fetchone()[0] == 0:
            print("Adding profile_picture column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255)")

        # 2. Create Categories Table
        print("Migrating 'categories' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                color VARCHAR(20) DEFAULT '#64748b',
                is_system BOOLEAN DEFAULT FALSE
            )
        """)

        # 3. Insert Default Categories (Idempotent)
        default_cats = [
            ('Docker', '#007bff', True),
            ('Kubernetes', '#326ce5', True),
            ('Linux', '#fcc624', True),
            ('CI/CD', '#10b981', True),
            ('AWS', '#ff9900', True),
            ('Monitoring', '#9333ea', True),
            ('Other', '#64748b', True)
        ]
        
        for name, color, is_sys in default_cats:
            # Check if exists
            cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO categories (name, color, is_system) VALUES (%s, %s, %s)", 
                    (name, color, is_sys)
                )

        # 4. Update Notes Table (Add user_id and foreign keys)
        print("Migrating 'notes' table schema...")
        
        # Check if user_id column exists
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'user_id')
        """, (Config.DB_NAME,))
        
        if cursor.fetchone()[0] == 0:
            print("Adding user_id column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN user_id INT")
            cursor.execute("ALTER TABLE notes ADD CONSTRAINT fk_notes_users FOREIGN KEY (user_id) REFERENCES users(id)")
        
        # Check if is_public column exists
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'notes') AND (COLUMN_NAME = 'is_public')
        """, (Config.DB_NAME,))

        if cursor.fetchone()[0] == 0:
            print("Adding is_public column to notes...")
            cursor.execute("ALTER TABLE notes ADD COLUMN is_public BOOLEAN DEFAULT FALSE")

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
