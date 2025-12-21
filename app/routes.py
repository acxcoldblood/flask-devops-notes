from flask import Blueprint, render_template, request, url_for, redirect
from app.db import get_db_connection

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def home():

    # CREATE
    if request.method == "POST":
        command = request.form.get("command")
        description = request.form.get("description")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO notes (command, description) VALUES (%s, %s)",
            (command, description)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("main.home"))

    # READ
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM notes")
    notes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", notes=notes)


@main.route("/about")
def about():
    return render_template("about.html")


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

    return redirect(url_for("main.home"))
