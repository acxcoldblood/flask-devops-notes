from flask import Blueprint, render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from app.db import get_db_connection
import bleach
import uuid

main = Blueprint("main", __name__)

# Allowed HTML tags and attributes for rich text content
ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "ul", "ol", "li", 
    "code", "pre", "a", "h1", "h2", "h3", "h4", "h5", "h6"
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target"],
    "code": ["class"],
    "pre": ["class"]
}

def sanitize_html(html_content):
    """Sanitize HTML content to prevent XSS attacks"""
    if not html_content:
        return ""
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


@main.route("/")
def index():
    """Landing page for guests, redirect to dashboard for authenticated users"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return render_template("landing.html")


@main.route("/dashboard", methods=["GET", "POST"])
@login_required
def home():

    # CREATE
    if request.method == "POST":
        command = request.form.get("command")
        description = request.form.get("description")
        category = request.form.get("category")
        example = request.form.get("example")
        tags = request.form.get("tags")

        # Sanitize HTML content
        description = sanitize_html(description)
        example = sanitize_html(example) if example else ""

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO notes (command, description, category, example, tags, user_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (command, description, category, example, tags, current_user.id)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("main.home"))

    # READ
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes WHERE user_id = %s ORDER BY id DESC", (current_user.id,))
    notes = cursor.fetchall()

    # Fetch categories for filters/dropdowns
    cursor.execute("SELECT * FROM categories ORDER BY is_system DESC, name ASC")
    categories = cursor.fetchall()

    # Calculate statistics
    total_notes = len(notes)
    
    # Category distribution
    category_counts = {}
    all_tags = []
    recent_notes = notes[:5] if notes else []
    
    for note in notes:
        category = note.get('category') or 'other'
        category_counts[category] = category_counts.get(category, 0) + 1
        
        if note.get('tags'):
            tags = [tag.strip() for tag in note['tags'].split(',') if tag.strip()]
            all_tags.extend(tags)
    
    # Tag frequency
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Sort tags by frequency
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    cursor.close()
    conn.close()

    return render_template(
        "index.html", 
        notes=notes,
        total_notes=total_notes,
        category_counts=category_counts,
        popular_tags=popular_tags,
        recent_notes=recent_notes,
        categories=categories
    )


@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/docs")
def docs():
    return render_template("docs.html")


@main.route("/note/<int:note_id>/toggle_public", methods=["POST"])
@login_required
def toggle_public(note_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verify ownership
    cursor.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
    note = cursor.fetchone()
    
    if not note or note["user_id"] != current_user.id:
        cursor.close()
        conn.close()
        abort(403)
        
    new_status = not note["is_public"]
    public_id = note["public_id"]
    
    if new_status and not public_id:
        public_id = str(uuid.uuid4())
        
    cursor.execute(
        "UPDATE notes SET is_public = %s, public_id = %s WHERE id = %s",
        (new_status, public_id, note_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    status_msg = "Note is now public!" if new_status else "Note is now private."
    flash(status_msg, "success")
    return redirect(url_for("main.home"))


@main.route("/s/<public_id>")
def public_note(public_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT n.*, u.username, u.profile_picture 
        FROM notes n 
        JOIN users u ON n.user_id = u.id 
        WHERE n.public_id = %s AND n.is_public = TRUE
    """, (public_id,))
    
    note = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not note:
        abort(404)
        
    return render_template("public_note.html", note=note)


@main.route("/delete/<int:id>")
@login_required
def delete_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check ownership
    cursor.execute("SELECT user_id FROM notes WHERE id = %s", (id,))
    note = cursor.fetchone()
    
    if not note:
        cursor.close()
        conn.close()
        return redirect(url_for('main.home'))
        
    if note[0] != current_user.id:
        cursor.close()
        conn.close()
        abort(403)

    cursor.execute("DELETE FROM notes WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("main.home"))


@main.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_note(id):

    if request.method == "GET":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM notes WHERE id = %s", (id,))
        note = cursor.fetchone()

        cursor.execute("SELECT * FROM categories ORDER BY is_system DESC, name ASC")
        categories = cursor.fetchall()

        cursor.close()
        conn.close()
        
        if not note:
             return redirect(url_for('main.home'))
             
        if note['user_id'] != current_user.id:
            abort(403)

        return render_template("edit.html", note=note, id=id, categories=categories)

    # POST
    command = request.form.get("command")
    description = request.form.get("description")
    category = request.form.get("category")
    example = request.form.get("example")
    tags = request.form.get("tags")

    if command and description:
        # Check ownership again before update
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM notes WHERE id = %s", (id,))
        check_note = cursor.fetchone()
        
        if not check_note or check_note[0] != current_user.id:
             cursor.close()
             conn.close()
             abort(403)
             
        # Sanitize HTML content
        description = sanitize_html(description)
        example = sanitize_html(example) if example else ""

        cursor.execute(
            "UPDATE notes SET command = %s, description = %s, category = %s, example = %s, tags = %s WHERE id = %s",
            (command, description, category, example, tags, id)
        )

        conn.commit()
        cursor.close()
        conn.close()

    return redirect(url_for("main.home"))


@main.route("/health")
def health():
    return "OK", 200


@main.route("/category/add", methods=["POST"])
@login_required
def add_category():
    name = request.form.get("name")
    color = request.form.get("color")
    
    if name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name, color, is_system) VALUES (%s, %s, FALSE)", (name, color))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Category added!", "success")
        
    return redirect(url_for('auth.settings'))


@main.route("/category/delete/<int:id>")
@login_required
def delete_category(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only delete if not system category
    cursor.execute("DELETE FROM categories WHERE id = %s AND is_system = FALSE", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Category deleted!", "success")
    return redirect(url_for('auth.settings'))