from flask import Flask, request, redirect, session, url_for
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Used to securely sign session cookies
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")


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
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


# ---------------- SIGN UP ----------------

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password before saving it
        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            connection.commit()

        except mysql.connector.IntegrityError:
            cursor.close()
            connection.close()

            return """
                <h3>Username already exists!</h3>
                <a href="/signup">Try again</a>
            """

        cursor.close()
        connection.close()

        return redirect('/login')

    return """
        <h1>Create Account</h1>

        <form method="POST">
            <input type="text" name="username"
                   placeholder="Enter username" required>
            <br><br>

            <input type="password" name="password"
                   placeholder="Enter password" required>
            <br><br>

            <button type="submit">Sign Up</button>
        </form>

        <p>Already have an account?
        <a href="/login">Sign In</a></p>
    """


# ---------------- SIGN IN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = %s",
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        # Check user exists AND password matches hash
        if user and check_password_hash(user[2], password):

            # Create session
            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect('/dashboard')

        return """
            <h3>Invalid username or password!</h3>
            <a href="/login">Try again</a>
        """

    return """
        <h1>Sign In</h1>

        <form method="POST">
            <input type="text" name="username"
                   placeholder="Enter username" required>
            <br><br>

            <input type="password" name="password"
                   placeholder="Enter password" required>
            <br><br>

            <button type="submit">Sign In</button>
        </form>

        <p>Don't have an account?
        <a href="/signup">Sign Up</a></p>
    """


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    # Protect this page
    if 'user_id' not in session:
        return redirect('/login')

    return f"""
        <h1>Welcome, {session['username']}! 🎉</h1>

        <p>You are successfully logged in.</p>

        <a href="/logout">Logout</a>
    """


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():

    # Remove all session data
    session.clear()

    return redirect('/login')


if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=5000)
