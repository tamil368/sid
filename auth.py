from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from manage import db, UserRole, Log

auth_bp = Blueprint('auth', __name__)

def log_action(user_id, action, details):
    log = Log(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(password)
        try:
            user = UserRole(name=name, email=email, phone=phone, role=role)
            user.password = hashed_password  # Add a password attribute to your model if it doesn't already exist
            db.session.add(user)
            db.session.commit()
            log_action(user.id, 'REGISTER', 'User registered successfully')
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error storing data: {str(e)}', 'danger')
            log_action(0, 'REGISTER_FAILED', 'Error storing data')
            return redirect(url_for('auth.register'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = UserRole.query.filter_by(email=email, role=role).first()
        if user and check_password_hash(user.password, password):
            log_action(user.id, 'LOGIN_SUCCESS', 'Login successful')
            if role == 'User':
                return redirect(url_for('user_page'))
            elif role == 'Admin':
                return redirect(url_for('admin_page'))
            else:
                flash('Invalid user type', 'danger')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid email, password, or user type', 'danger')
            log_action(0, 'LOGIN_FAILED', 'Invalid credentials or user type')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    user_id = 1  # This should be dynamic based on logged-in user
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        try:
            user = UserRole(name=name, email=email, phone=phone, role=role)
            db.session.add(user)
            db.session.commit()
            log_action(user_id, 'ADD_USER', f'Added user {name}')
            flash('Stored successfully!', 'success')
            return redirect(url_for('auth.add_user'))
        except Exception as e:
            flash(f'Error storing data: {str(e)}', 'danger')
            log_action(user_id, 'ADD_USER_FAILED', f'Error storing user {name}')
            return redirect(url_for('auth.add_user'))
    return render_template('add_user.html')
