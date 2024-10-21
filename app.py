from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_data'
app.secret_key = 'your_secret_key'  # Required for flashing messages

mysql = MySQL(app)

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

@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def index():
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
        except Exception as e:
            flash(f'Error storing data: {e}', 'danger')
            return redirect('/register')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    cur.close()
    return render_template('register.htm', data=data)

@app.route('/login')
def login():
    return render_template('login.htm')  # Placeholder for login page

if __name__ == '__main__':
    app.run(debug=True)
