from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

auth_bp = Blueprint('auth', __name__)

def log_action(user_id, action, details):
    cur = current_app.pgdb.connection.cursor()
    cur.execute('''
        INSERT INTO logs (user_id, action, details)
        VALUES (%s, %s, %s)
    ''', (user_id, action, details))
    current_app.pgdb.connection.commit()
    cur.close()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['user_type']
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(password)
        try:
            cur = current_app.pgdb.connection.cursor()
            cur.execute("INSERT INTO users (name, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, phone, hashed_password, user_type))
            current_app.pgdb.connection.commit()  # Commit the transaction
            user_id = cur.lastrowid
            cur.close()
            log_action(user_id, 'REGISTER', 'User registered successfully')
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
        except psycopg2.IntegrityError as e:
            flash(f'Error: Email already registered! {str(e)}', 'danger')
            log_action(0, 'REGISTER_FAILED', 'Email already registered')
            return redirect(url_for('auth.register'))
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
        user_type = request.form['user_type']
        cur = current_app.pgdb.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND user_type = %s", (email, user_type))
        user = cur.fetchone()
        if user and check_password_hash(user[4], password):
            log_action(user[0], 'LOGIN_SUCCESS', 'Login successful')
            if user_type == 'User':
                return redirect(url_for('user_page'))
            elif user_type == 'Admin':
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
            cur = current_app.pgdb.connection.cursor()
            cur.execute("INSERT INTO users_role (name, email, phone, role) VALUES (%s, %s, %s, %s)",
                        (name, email, phone, role))
            current_app.pgdb.connection.commit()
            cur.close()
            log_action(user_id, 'ADD_USER', f'Added user {name}')
            flash('Stored successfully!', 'success')
            return redirect(url_for('auth.add_user'))
        except Exception as e:
            flash(f'Error storing data: {str(e)}', 'danger')
            log_action(user_id, 'ADD_USER_FAILED', f'Error storing user {name}')
            return redirect(url_for('auth.add_user'))
    return render_template('add_user.html')
