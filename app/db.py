import time
import mysql.connector
from mysql.connector import Error
from app.config import Config


def get_db_connection(retries=10, delay=2):
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
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
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            command VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50),
            example TEXT,
            tags VARCHAR(500)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("Database initialized successfully")
