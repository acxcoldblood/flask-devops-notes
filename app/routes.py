from flask import Blueprint, render_template, request, url_for, redirect
from app.db import get_db_connection
import bleach

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


@main.route("/", methods=["GET", "POST"])
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
            "INSERT INTO notes (command, description, category, example, tags) VALUES (%s, %s, %s, %s, %s)",
            (command, description, category, example, tags)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("main.home"))

    # READ
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes ORDER BY id DESC")
    notes = cursor.fetchall()

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
        recent_notes=recent_notes
    )


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/docs")
def docs():
    return render_template("docs.html")


@main.route("/delete/<int:id>")
def delete_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("main.home"))


@main.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_note(id):

    if request.method == "GET":
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM notes WHERE id = %s", (id,))
        note = cursor.fetchone()

        cursor.close()
        conn.close()

        return render_template("edit.html", note=note, id=id)

    # POST
    command = request.form.get("command")
    description = request.form.get("description")
    category = request.form.get("category")
    example = request.form.get("example")
    tags = request.form.get("tags")

    if command and description:
        # Sanitize HTML content
        description = sanitize_html(description)
        example = sanitize_html(example) if example else ""

        conn = get_db_connection()
        cursor = conn.cursor()

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