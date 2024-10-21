from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_mysqldb import MySQLdb

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from manage import mysql
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect('/register')
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
                        (name, email, phone, password))
            mysql.connection.commit()
            cur.close()
            flash('Registration successful!', 'success')
            return redirect('/register')
        except MySQLdb.OperationalError as e:
            flash(f'Database error: {e}', 'danger')
            return redirect('/register')
        except Exception as e:
            flash(f'Error storing data: {e}', 'danger')
            return redirect('/register')
    return render_template('register.htm')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from manage import mysql
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        
        if user:
            flash('Login successfully', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect('/login')
    return render_template('login.htm')
