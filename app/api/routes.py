from flask import jsonify, request, abort, current_app
from app.api import api
from app.user import User
from app.db import get_db_connection
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Look for token in header
        token = request.headers.get('X-API-Token')
        if not token:
            return jsonify({"error": "Missing X-API-Token header"}), 401
            
        user = User.get_by_token(token)
        if not user:
            return jsonify({"error": "Invalid API Token"}), 401
            
        # Add user to request context for use in route
        request.user = user
        return f(*args, **kwargs)
    return decorated_function

@api.route('/notes', methods=['GET'])
@require_api_key
def get_notes():
    """Get all notes for the authenticated user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Optional filtering
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = "SELECT * FROM notes WHERE user_id = %s"
    params = [request.user.id]

    if category:
        query += " AND category = %s"
        params.append(category)
        
    if search:
        query += " AND (command LIKE %s OR description LIKE %s OR tags LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
        
    query += " ORDER BY id DESC"
    
    cursor.execute(query, tuple(params))
    notes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "count": len(notes),
        "notes": notes
    })

@api.route('/notes/<int:id>', methods=['GET'])
@require_api_key
def get_note(id):
    """Get a specific note"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM notes WHERE id = %s AND user_id = %s", (id, request.user.id))
    note = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not note:
        return jsonify({"error": "Note not found"}), 404
        
    return jsonify(note)

@api.route('/notes', methods=['POST'])
@require_api_key
def create_note():
    """Create a new note"""
    data = request.get_json()
    
    if not data or not data.get('command') or not data.get('description'):
        return jsonify({"error": "Missing required fields: command, description"}), 400
        
    command = data.get('command')
    description = data.get('description')
    category = data.get('category', 'Uncategorized')
    example = data.get('example', '')
    tags = data.get('tags', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO notes (command, description, category, example, tags, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (command, description, category, example, tags, request.user.id)
        )
        conn.commit()
        note_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
    return jsonify({
        "message": "Note created successfully",
        "id": note_id,
        "location": f"/api/notes/{note_id}"
    }), 201

@api.route('/categories', methods=['GET'])
@require_api_key
def get_categories():
    """Get all unique categories for the user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM notes WHERE user_id = %s", (request.user.id,))
    categories = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return jsonify({"categories": categories})

@api.route('/health', methods=['GET'])
def health_check():
    """Public health check endpoint"""
    return jsonify({"status": "ok", "service": "DevOps Notes Manager API"})
