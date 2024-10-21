from flask import Flask
from flask_mysqldb import MySQL
import secrets

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Set your MySQL password here
app.config['MYSQL_DB'] = 'employee_data'

# Set a secret key for sessions
app.secret_key = secrets.token_hex(16)

# Initialize MySQL
mysql = MySQL(app)

# Import and register routes (delayed import to avoid circular import)
from auth import auth_bp
app.register_blueprint(auth_bp)

# Check MySQL connection
@app.route('/check_db')
def check_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT VERSION()')  # Simple query to check if the DB is responding
        db_version = cur.fetchone()
        cur.close()
        return f"Connected to MySQL database. Version: {db_version[0]}"
    except Exception as e:
        return f"Error connecting to the database: {e}"

if __name__ == '__main__':
    app.run(debug=True)
