import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import secrets
from datetime import datetime
import auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:fpEi3c9mmznahGcr5th58vKaLTQyy5tl@dpg-cse7i1dsvqrc73etobg0-a/employee_data_thu5'
app.secret_key = secrets.token_hex(16)
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.register_blueprint(auth_bp)

# Define your models
class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    role = db.Column(db.String(20))
    password = db.Column(db.String(255))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_role.id'))
    action = db.Column(db.String(50))
    details = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Function to log user actions
def log_action(user_id, action, details):
    log = Log(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

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
    users = UserRole.query.order_by(UserRole.id.asc()).all()
    return render_template("user.html", users=users)

# Admin page route
@app.route('/admin_page')
def admin_page():
    users = UserRole.query.order_by(UserRole.id.asc()).all()
    logs = Log.query.join(UserRole, Log.user_id == UserRole.id).order_by(Log.timestamp.desc()).all()
    return render_template("admin.html", users=users, logs=logs)

# Update user route for users
@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user_id = 1  # Replace with dynamic logged-in user ID
    user = UserRole.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.role = request.form['role']
        db.session.commit()
        log_action(user_id, 'UPDATE', f'Updated user {id}')
        return redirect(url_for('user_page'))
    return render_template("update_user.html", user=user)

# Update user route for admins
@app.route('/update_user_admin/<int:id>', methods=['GET', 'POST'])
def update_user_admin(id):
    user_id = 1  # Replace with dynamic logged-in user ID
    user = UserRole.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.role = request.form['role']
        db.session.commit()
        log_action(user_id, 'UPDATE', f'Updated user {id}')
        return redirect(url_for('admin_page'))
    return render_template("update_user_admin.html", user=user)

# Delete user route
@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    user_id = 1  # Replace with dynamic logged-in user ID
    user = UserRole.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    log_action(user_id, 'DELETE', f'Deleted user {id}')
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
        db.session.execute('SELECT 1')
        return "Connected to PostgreSQL database."
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
    for index, row in df.iterrows():
        user = UserRole(name=row['name'], email=row['email'], phone=row['phone'], role=row['role'])
        db.session.add(user)
    db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5432)))
