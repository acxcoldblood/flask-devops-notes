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

    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY is required. Set it in the environment before starting the app.")
    app.config['SECRET_KEY'] = secret_key

    def _get_bool_env(name, default=False):
        val = os.environ.get(name)
        if val is None:
            return default
        return val.strip().lower() in ("1", "true", "yes", "on")

    # Session Security Config
    app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config['SESSION_COOKIE_SECURE'] = _get_bool_env('SESSION_COOKIE_SECURE', False)
    app.config['REMEMBER_COOKIE_SECURE'] = _get_bool_env('REMEMBER_COOKIE_SECURE', False)
    app.config['REMEMBER_COOKIE_SAMESITE'] = os.environ.get('REMEMBER_COOKIE_SAMESITE', 'Lax')

    # Upload size limit (default: 2MB)
    max_upload_mb = int(os.environ.get('UPLOAD_MAX_MB', '2'))
    app.config['MAX_CONTENT_LENGTH'] = max_upload_mb * 1024 * 1024

    # Initialize Flask-Login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = None
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.user import User
        return User.get(int(user_id))

    app.register_blueprint(main)
    
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
   

    # Initialize the database
    # Initialize the database
    init_db()
    return app
