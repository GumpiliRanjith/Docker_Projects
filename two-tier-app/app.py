from flask import Flask, request, redirect
import mysql.connector
import os

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


@app.route('/')
def home():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()

    cursor.close()
    connection.close()

    html = """
    <h1>Employee Management App</h1>

    <form action="/add" method="POST">
        <input type="text" name="name" placeholder="Enter employee name" required>
        <button type="submit">Add Employee</button>
    </form>

    <h2>Employees</h2>
    <ul>
    """

    for employee in employees:
        html += f"<li>{employee[0]} - {employee[1]}</li>"

    html += """
    </ul>
    """

    return html


@app.route('/add', methods=['POST'])
def add_employee():
    name = request.form['name']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO employees (name) VALUES (%s)",
        (name,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/')


if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=5000)
