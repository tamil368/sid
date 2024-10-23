from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb
import mysql.connector

auth_bp = Blueprint('auth', __name__)

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
            cur = current_app.config['MYSQL'].connection.cursor()
            cur.execute("INSERT INTO users (name, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, phone, hashed_password, user_type))
            current_app.config['MYSQL'].connection.commit()  # Commit the transaction
            cur.close()
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
        except MySQLdb.IntegrityError as e:
            flash(f'Error: Email already registered! {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
        except Exception as e:
            flash(f'Error storing data: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
    return render_template('register.htm')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        cur = current_app.config['MYSQL'].connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND user_type = %s", (email, user_type))
        user = cur.fetchone()

        if user and check_password_hash(user[4], password):
            flash('Login successful!', 'success')
            if user_type == 'User':
                return redirect(url_for('user_page'))
            elif user_type == 'Admin':
                return redirect(url_for('admin_page'))
            else:
                flash('Invalid user type', 'danger')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid email, password, or user type', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('login.htm')

@auth_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        try:
            cur = current_app.config['MYSQL'].connection.cursor()
            cur.execute("INSERT INTO users_role (name, email, phone, role) VALUES (%s, %s, %s, %s)",
                        (name, email, phone, role))
            current_app.config['MYSQL'].connection.commit()
            cur.close()
            flash('Stored successfully!', 'success')
            return redirect(url_for('auth.add_user'))
        except Exception as e:
            flash(f'Error storing data: {str(e)}', 'danger')
            return redirect(url_for('auth.add_user'))
    return render_template('add_user.htm')

