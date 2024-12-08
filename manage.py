import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_mysqldb import MySQL
import secrets
from auth import auth_bp

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_data'
app.secret_key = secrets.token_hex(16)
mysql = MySQL(app)
app.mysql = mysql  # Set the MySQL instance in the app context

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.register_blueprint(auth_bp)

# Function to log user actions
def log_action(user_id, action, details):
    cur = mysql.connection.cursor()
    cur.execute('''
        INSERT INTO logs (user_id, action, details)
        VALUES (%s, %s, %s)
    ''', (user_id, action, details))
    mysql.connection.commit()
    cur.close()

# Home page route
@app.route('/')
def home():
    msg = request.args.get('msg')
    return render_template("index.html", msg=msg)

# Upload page route
@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')

# User page route
@app.route('/user_page')
def user_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, phone, role FROM users_role ORDER BY id ASC")
    users = cur.fetchall()
    cur.close()
    return render_template("user.html", users=users)

# Admin page route
@app.route('/admin_page')
def admin_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, phone, role FROM users_role ORDER BY id ASC")
    users = cur.fetchall()
    cur.execute('''
        SELECT logs.id, users.name, logs.action, logs.timestamp, logs.details
        FROM logs
        JOIN users ON logs.user_id = users.id
        ORDER BY logs.timestamp DESC
    ''')
    logs = cur.fetchall()
    cur.close()
    return render_template("admin.html", users=users, logs=logs)

# Update user route for users
@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user_id = 1  # Replace with dynamic logged-in user ID
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users_role SET name = %s, email = %s, phone = %s, role = %s WHERE id = %s", 
                    (name, email, phone, role, id))
        mysql.connection.commit()
        log_action(user_id, 'UPDATE', f'Updated user {id}')
        cur.close()
        return redirect(url_for('user_page'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, phone, role FROM users_role WHERE id = %s", (id,))
    user = cur.fetchone()
    cur.close()
    return render_template("update_user.html", user=user)

# Update user route for admins
@app.route('/update_user_admin/<int:id>', methods=['GET', 'POST'])
def update_user_admin(id):
    user_id = 1  # Replace with dynamic logged-in user ID
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users_role SET name = %s, email = %s, phone = %s, role = %s WHERE id = %s", 
                    (name, email, phone, role, id))
        mysql.connection.commit()
        log_action(user_id, 'UPDATE', f'Updated user {id}')
        cur.close()
        return redirect(url_for('admin_page'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, phone, role FROM users_role WHERE id = %s", (id,))
    user = cur.fetchone()
    cur.close()
    return render_template("update_user_admin.html", user=user)

# Delete user route
@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user_id = 1  # Replace with dynamic logged-in user ID
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users_role WHERE id = %s", (id,))
    mysql.connection.commit()
    log_action(user_id, 'DELETE', f'Deleted user {id}')
    cur.close()
    return redirect(url_for('admin_page'))

# Login page route
@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template("login.html", msg=msg)

# Register page route
@app.route('/register')
def register():
    return render_template("register.html")

# Add user route
@app.route('/add_user')
def add_user():
    return render_template("add_user.html")

# Route to check database connection
@app.route('/check_db')
def check_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT VERSION()')
        db_version = cur.fetchone()
        cur.close()
        return f"Connected to MySQL database. Version: {db_version[0]}"
    except Exception as e:
        return f"Error connecting to the database: {e}"

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('upload_page'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('upload_page'))
    # Supported file extensions
    allowed_extensions = ('.xls', '.xlsx', '.xlsm', '.xltx', '.xltm', '.csv')
    # Check if the file has one of the allowed extensions
    if file and file.filename.endswith(allowed_extensions):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)  # Save the file to the uploads folder
        try:
            import_file_to_db(file_path)
            flash("File successfully uploaded and data imported into the database!", "success")
            return redirect(url_for('upload_page'))
        except Exception as e:
            flash("Duplicated data not Allowed", 'error')
            return redirect(url_for('upload_page'))
    else:
        flash('Invalid file type. Please upload a valid Excel file or CSV.', 'error')
        return redirect(url_for('upload_page'))

# Function to import file data into the database
def import_file_to_db(file_path):
    if file_path.endswith(('.xls', '.xlsx', '.xlsm', '.xltx', '.xltm')):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    cur = mysql.connection.cursor()
    # Iterate over each row in the file and insert into users_role table
    for index, row in df.iterrows():
        cur.execute('''
            INSERT INTO users_role (name, email, phone, role)
            VALUES (%s, %s, %s, %s)
        ''', (row['name'], row['email'], row['phone'], row['role']))
        mysql.connection.commit()
    cur.close()

if __name__ == '__main__':
    app.run(debug=True)