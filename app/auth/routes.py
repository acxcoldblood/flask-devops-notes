from flask import Blueprint, render_template, request, url_for, redirect, flash, abort, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.user import User
import secrets
import os
from werkzeug.utils import secure_filename
from app.db import get_db_connection
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import smtplib
from email.message import EmailMessage

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file_obj):
    file_obj.stream.seek(0, os.SEEK_END)
    size = file_obj.stream.tell()
    file_obj.stream.seek(0)
    return size

def is_valid_upload(file_obj):
    if not file_obj or not file_obj.filename:
        return False
    if not allowed_file(file_obj.filename):
        return False
    if file_obj.mimetype not in ALLOWED_MIME_TYPES:
        return False
    max_bytes = current_app.config.get('MAX_CONTENT_LENGTH', 2 * 1024 * 1024)
    return get_file_size(file_obj) <= max_bytes

def _get_mail_config():
    return {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", "587")),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASSWORD", ""),
        "sender": os.environ.get("SMTP_SENDER", ""),
        "use_tls": os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes", "on"),
    }

def _get_reset_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

def generate_reset_token(email):
    serializer = _get_reset_serializer()
    return serializer.dumps(email, salt="password-reset")

def verify_reset_token(token, max_age_seconds):
    serializer = _get_reset_serializer()
    try:
        return serializer.loads(token, salt="password-reset", max_age=max_age_seconds)
    except (SignatureExpired, BadSignature):
        return None

def send_reset_email(to_email, reset_url):
    cfg = _get_mail_config()
    if not cfg["sender"]:
        cfg["sender"] = cfg["user"]

    msg = EmailMessage()
    msg["Subject"] = "Reset your DevNotes password"
    msg["From"] = cfg["sender"]
    msg["To"] = to_email
    msg.set_content(
        "You requested a password reset for DevNotes.\n\n"
        f"Reset your password using this link:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    with smtplib.SMTP(cfg["host"], cfg["port"]) as smtp:
        if cfg["use_tls"]:
            smtp.starttls()
        if cfg["user"] and cfg["password"]:
            smtp.login(cfg["user"], cfg["password"])
        smtp.send_message(msg)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        bio = request.form.get('bio', '').strip()
        profile_pic = request.files.get('profile_picture')
        
        # Validate display_name
        if not display_name:
            flash('Display name cannot be empty.', 'danger')
            cursor.execute("SELECT * FROM categories ORDER BY is_system DESC, name ASC")
            categories = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('settings.html', categories=categories)
        
        # Handle profile picture upload
        new_profile_pic = current_user.profile_picture  # Keep existing if no new upload
        if profile_pic and profile_pic.filename:
            if is_valid_upload(profile_pic):
                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Generate unique filename
                ext = profile_pic.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"user_{current_user.id}.{ext}")
                filepath = os.path.join(upload_folder, filename)
                
                # Delete old profile picture if it exists and is different
                if current_user.profile_picture:
                    old_path = os.path.join(upload_folder, current_user.profile_picture)
                    if os.path.exists(old_path) and current_user.profile_picture != filename:
                        os.remove(old_path)
                
                # Save new picture
                profile_pic.save(filepath)
                new_profile_pic = filename
            else:
                flash('Invalid file. Use PNG/JPG/GIF under the upload size limit.', 'danger')
        
        # Update database
        cursor.execute("""
            UPDATE users 
            SET username = %s, bio = %s, profile_picture = %s 
            WHERE id = %s
        """, (display_name, bio, new_profile_pic, current_user.id))
        conn.commit()
        
        flash('Profile updated successfully!', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('auth.settings'))
    
    # GET request
    cursor.execute("SELECT * FROM categories ORDER BY is_system DESC, name ASC")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('settings.html', categories=categories)

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return redirect(url_for('auth.settings'))

@auth.route('/regenerate_token')
@login_required
def regenerate_token():
    token = secrets.token_hex(16)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET api_token = %s WHERE id = %s", (token, current_user.id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('New API Token generated!', 'success')
    return redirect(url_for('auth.settings'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.get_by_email(form.email.data):
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', title='Register', form=form)
            
        if User.create(form.username.data, form.email.data, form.password.data):
            flash('Your account has been created! You can now are able to log in', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('An error occurred. Please try again.', 'danger')
            
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        # Always show success to avoid account enumeration
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            try:
                send_reset_email(user.email, reset_url)
            except Exception as e:
                current_app.logger.error(f"Password reset email failed: {e}")

        flash('If that email is registered, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    max_age = int(os.environ.get('RESET_TOKEN_MAX_AGE', '3600'))
    email = verify_reset_token(token, max_age)
    if not email:
        flash('That reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        cursor = conn.cursor()
        password_hash = generate_password_hash(form.password.data)
        cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (password_hash, email))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Your password has been updated. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
