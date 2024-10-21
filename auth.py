from flask import Blueprint, render_template, request, redirect, flash
from flask_mysqldb import MySQLdb
from manage import app  # Import the app to access its configuration if necessary

# Create a blueprint
auth_bp = Blueprint('auth', __name__)

# Route for registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from manage import mysql  # Import 'mysql' inside the route to avoid circular import
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')  # Error message for password mismatch
            return redirect('/register')

        # Insert data into the database
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)", 
                        (name, email, phone, password))
            mysql.connection.commit()
            cur.close()
            flash('Registration successful!', 'success')  # Success message
            return redirect('/register')  # Redirect to the same page or you can specify a different one
        except MySQLdb.OperationalError as e:
            flash(f'Database error: {e}', 'danger')
            return redirect('/register')
        except Exception as e:
            flash(f'Error storing data: {e}', 'danger')
            return redirect('/register')

    return render_template('register.htm')  # Render the signup form

# Route for login
@auth_bp.route('/login')
def login():
    return render_template('login.htm')  # Placeholder for login page
