from flask_login import UserMixin
from app.db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, role='user', api_token=None, bio=None, profile_picture=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.api_token = api_token
        self.bio = bio
        self.profile_picture = profile_picture

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data['role'],
                api_token=user_data.get('api_token'),
                bio=user_data.get('bio'),
                profile_picture=user_data.get('profile_picture')
            )
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data['role'],
                api_token=user_data.get('api_token'),
                bio=user_data.get('bio'),
                profile_picture=user_data.get('profile_picture')
            )
        return None

    @staticmethod
    def get_by_token(token):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE api_token = %s", (token,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                role=user_data['role'],
                api_token=user_data.get('api_token'),
                bio=user_data.get('bio'),
                profile_picture=user_data.get('profile_picture')
            )
        return None
    
    @staticmethod
    def create(username, email, password):
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
