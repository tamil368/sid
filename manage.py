from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import secrets
from auth import auth_bp

app = Flask(__name__)

# MySQL database configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_data'
app.secret_key = secrets.token_hex(16)

mysql = MySQL(app)
app.config['MYSQL'] = mysql  # Make MySQL instance accessible to the blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    msg = request.args.get('msg')
    return render_template("index.htm", msg=msg)

@app.route('/user_page')
def user_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, phone, role FROM users_role")
    users = cur.fetchall()
    cur.close()
    return render_template("user.htm", users=users)

@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE users_role
            SET name = %s, email = %s, phone = %s, role = %s
            WHERE id = %s
        """, (name, email, phone, role, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('user_page'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, phone, role FROM users_role WHERE id = %s", (id,))
    user = cur.fetchone()
    cur.close()
    return render_template("update_user.htm", user=user)

@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template("login.htm", msg=msg)

@app.route('/register')
def register():
    return render_template("register.htm")

@app.route('/add_user')
def add_user():
    return render_template("add_user.htm")

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
# @app.route('/user')
# def user_management():

if __name__ == '__main__':
    app.run(debug=True)
