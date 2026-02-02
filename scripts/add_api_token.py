import mysql.connector
from mysql.connector import Error
import os
import sys

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import Config

def run_migration():
    print("Migrating schema to add api_token...")
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        cursor = conn.cursor()
        
        # Check if api_token column exists
        cursor.execute("""
            SELECT count(*) FROM information_schema.COLUMNS 
            WHERE (TABLE_SCHEMA = %s) AND (TABLE_NAME = 'users') AND (COLUMN_NAME = 'api_token')
        """, (Config.DB_NAME,))
        
        if cursor.fetchone()[0] == 0:
            print("Adding api_token column to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN api_token VARCHAR(64) UNIQUE")
        else:
            print("phew! api_token column already exists.")

        conn.commit()
        print("Migration complete! ✅")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    run_migration()
