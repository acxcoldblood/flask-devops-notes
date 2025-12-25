import time
import mysql.connector
from mysql.connector import Error
from app.config import Config


def get_db_connection():
    try:
        return mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
        )
    except Error as e:
        print(f"Database connection error: {e}")
        return None


def init_db(retries=10, delay=2):
    """
    Try to connect to DB and create tables.
    Retry because MySQL may not be ready yet.
    """
    for attempt in range(retries):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    command VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    category VARCHAR(50),
                    example TEXT,
                    tags VARCHAR(500)
                )
            """)
            
            # Add new columns if they don't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE notes ADD COLUMN category VARCHAR(50)")
            except:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE notes ADD COLUMN example TEXT")
            except:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE notes ADD COLUMN tags VARCHAR(500)")
            except:
                pass  # Column already exists
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully")
            return

        print(f"Waiting for database... ({attempt + 1}/{retries})")
        time.sleep(delay)

    print("Database not ready after retries")
