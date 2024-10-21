from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from auth import auth_bp
import secrets

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_data'
app.secret_key = secrets.token_hex(16)

mysql = MySQL(app)

app.register_blueprint(auth_bp)

@app.route('/')
def home():
    msg = request.args.get('msg')
    return render_template("index.htm", msg=msg)

@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template("login.htm", msg=msg)

@app.route('/register')
def register():
    return render_template("register.htm")

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

if __name__ == '__main__':
    app.run(debug=True)
