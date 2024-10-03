from flask import Flask, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)

# Configure the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/employeedb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Employee model
class Employee(db.Model):
    __tablename__ = 'employees'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    contact = db.Column(db.String(100))

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to export data to Excel
@app.route('/export')
def export_to_excel():
    employees = Employee.query.all()
    data = {
        'ID': [],
        'Name': [],
        'Position': [],
        'Department': [],
        'Contact': []
    }

    for emp in employees:
        data['ID'].append(emp.id)
        data['Name'].append(emp.name)
        data['Position'].append(emp.position)
        data['Department'].append(emp.department)
        data['Contact'].append(emp.contact)

    df = pd.DataFrame(data)
    file_path = 'employees.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
