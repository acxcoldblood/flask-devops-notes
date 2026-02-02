import mysql.connector
import os
import time

def get_db_connection():
    host = os.environ.get('DB_HOST', 'mysql')
    port = os.environ.get('DB_PORT', '3306')
    user = os.environ.get('DB_USER', 'devops')
    password = os.environ.get('DB_PASSWORD', 'devops123')
    database = os.environ.get('DB_NAME', 'devops_notes')

    print(f"Connecting to {host}:{port} as {user}...")
    
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    return conn

def migrate():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Checking if columns exist...")
        
        # Check is_public
        try:
            cursor.execute("SELECT is_public FROM notes LIMIT 1")
            cursor.fetchone() # Consume result
            print("Column 'is_public' already exists.")
        except:
            print("Column 'is_public' missing. Adding...")
            cursor.execute("ALTER TABLE notes ADD COLUMN is_public BOOLEAN DEFAULT FALSE")
            print("Added 'is_public'.")

        # Check public_id
        try:
            cursor.execute("SELECT public_id FROM notes LIMIT 1")
            cursor.fetchone() # Consume result
            print("Column 'public_id' already exists.")
        except:
            print("Column 'public_id' missing. Adding...")
            cursor.execute("ALTER TABLE notes ADD COLUMN public_id VARCHAR(36) UNIQUE")
            print("Added 'public_id'.")

        conn.commit()
        cursor.close()
        conn.close()
        print("Migration complete!")
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
