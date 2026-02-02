from flask import Blueprint, render_template, request, url_for, redirect, flash, abort, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm
from app.user import User
import secrets
import os
from werkzeug.utils import secure_filename
from app.db import get_db_connection

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            if allowed_file(profile_pic.filename):
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
                flash('Invalid file type. Please upload PNG, JPG, or GIF.', 'danger')
        
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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        bio = request.form.get('bio', '').strip()
        profile_pic = request.files.get('profile_picture')
        
        if not display_name:
            flash('Display name cannot be empty.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('auth.profile'))
        
        # Handle profile picture upload
        new_profile_pic = current_user.profile_picture
        if profile_pic and profile_pic.filename:
            if allowed_file(profile_pic.filename):
                upload_folder = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                ext = profile_pic.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"user_{current_user.id}.{ext}")
                filepath = os.path.join(upload_folder, filename)
                
                if current_user.profile_picture:
                    old_path = os.path.join(upload_folder, current_user.profile_picture)
                    if os.path.exists(old_path) and current_user.profile_picture != filename:
                        os.remove(old_path)
                
                profile_pic.save(filepath)
                new_profile_pic = filename
            else:
                flash('Invalid file type. Please upload PNG, JPG, or GIF.', 'danger')
        
        cursor.execute("""
            UPDATE users 
            SET username = %s, bio = %s, profile_picture = %s 
            WHERE id = %s
        """, (display_name, bio, new_profile_pic, current_user.id))
        conn.commit()
        
        flash('Profile updated successfully!', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('auth.profile'))
    
    cursor.close()
    conn.close()
    return render_template('profile.html')

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

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
