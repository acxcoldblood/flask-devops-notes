from flask import Flask
from app.routes import main
import os
from app.db import init_db


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static")
    )

    app.register_blueprint(main)
   

    # Initialize the database
    init_db()
    return app