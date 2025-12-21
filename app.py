# Flask core imports
from flask import Flask, jsonify, render_template, request, url_for, redirect

# MySQL connector to communicate with MySQL database
import mysql.connector


# --------------------------------------------------
# Database connection helper
# --------------------------------------------------
def get_db_connection():
    """
    Creates and returns a new connection to the MySQL database.
    This function is called every time the app needs DB access.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Agarwals",   # MySQL root password
        database="devops_notes"
    )


# --------------------------------------------------
# Flask application instance
# --------------------------------------------------
app = Flask(__name__)


# --------------------------------------------------
# HOME ROUTE
# Handles:
#   - GET  → Read notes from database
#   - POST → Create a new note
# --------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def home():

    # -----------------------------
    # CREATE (POST)
    # -----------------------------
    if request.method == 'POST':
        # Read form data
        command = request.form.get('command')
        description = request.form.get('description')

        # Insert note into database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO notes (command, description) VALUES (%s, %s)",
            (command, description)
        )

        # Commit is REQUIRED for INSERT
        conn.commit()

        # Clean up DB resources
        cursor.close()
        conn.close()

        # Redirect to avoid duplicate form submission
        return redirect(url_for('home'))

    # -----------------------------
    # READ (GET)
    # -----------------------------
    conn = get_db_connection()

    # dictionary=True allows access like note.command in templates
    cursor = conn.cursor(dictionary=True)

    # Fetch all notes
    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()

    # Clean up
    cursor.close()
    conn.close()

    # Render notes on homepage
    return render_template('index.html', notes=notes)


# --------------------------------------------------
# ABOUT PAGE (Static)
# --------------------------------------------------
@app.route('/about')
def about():
    return render_template('about.html')


# --------------------------------------------------
# DELETE NOTE
# Deletes a note using its database ID
# --------------------------------------------------
@app.route('/delete/<int:id>')
def delete_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete note by primary key
    cursor.execute(
        "DELETE FROM notes WHERE id = %s",
        (id,)
    )

    # Commit is REQUIRED for DELETE
    conn.commit()

    # Clean up
    cursor.close()
    conn.close()

    # Redirect back to homepage
    return redirect(url_for('home'))


# --------------------------------------------------
# EDIT NOTE
#   - GET  → Fetch note & show edit form
#   - POST → Update note in database
# --------------------------------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_note(id):

    # -----------------------------
    # GET: Show edit form
    # -----------------------------
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM notes WHERE id = %s",
            (id,)
        )

        note = cursor.fetchone()

        cursor.close()
        conn.close()

        return render_template('edit.html', note=note, id=id)

    # -----------------------------
    # POST: Update note
    # -----------------------------
    else:
        command = request.form.get('command')
        description = request.form.get('description')

        if command and description:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE notes SET command = %s, description = %s WHERE id = %s",
                (command, description, id)
            )

            conn.commit()
            cursor.close()
            conn.close()

        return redirect(url_for('home'))

# --------------------------------------------------
# Run Flask application
# --------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
