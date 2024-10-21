from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
mysql = MySQL(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_data'
app.secret_key = 'your_secret_key'

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
            return redirect('/register')

        hashed_password = generate_password_hash(password)

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s)",
                        (name, email, phone, hashed_password, user_type))
            mysql.connection.commit()
            cur.close()
            flash('Registration successful!', 'success')
            return redirect(url_for('auth.login'))
        except MySQLdb.IntegrityError:
            flash('Error: Email already registered!', 'danger')
            return redirect('/register')
        except Exception as e:
            flash(f'Error storing data: {e}', 'danger')
            return redirect('/register')

    return render_template('register.htm')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND user_type = %s", (email, user_type))
        user = cur.fetchone()

        if user and check_password_hash(user[4], password):
            if user_type == 'User':
                return redirect(url_for('add_user'))
            elif user_type == 'Admin':
                return redirect(url_for('admin_page'))
            else:
                flash('Invalid user type', 'danger')
                return redirect('/login')
        else:
            flash('Invalid email, password, or user type', 'danger')
            return redirect('/login')

    return render_template('login.htm')

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    cursor.close()
    
    return render_template('index.html', roles=roles)

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role_id = request.form['role_id']

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users_role (name, email, phone, role_id) VALUES (%s, %s, %s, %s)", 
                        (name, email, phone, role_id))
            mysql.connection.commit()
            flash('User added successfully!', 'success')
            return redirect('/home')  # Redirect to index.htm after successful insertion
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error occurred: {str(e)}', 'danger')
        finally:
            cursor.close()

        return redirect('/home')

if __name__ == '__main__':
    app.run(debug=True)
