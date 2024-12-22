from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_session import Session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Add a secret key for session management
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
Session(app)

DATABASE = 'trash.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            hint TEXT,
            secret_question TEXT,
            secret_answer TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            username TEXT NOT NULL,
            location TEXT NOT NULL,
            photo TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drop_offs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            photo TEXT,
            post_id INTEGER,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
    ''')
    conn.commit()
    conn.close()

# Call init_db() to initialize the database
init_db()

@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY date DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/historical_posts')
def historical_posts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY date DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template('historical_posts.html', historical_posts=posts)

@app.route('/drop_off', methods=['GET', 'POST'])
def drop_off():
    if 'user_id' not in session:
        flash('You need to be logged in to drop off an item.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        item = request.form['item']
        location = request.form['location']
        date = request.form['date']
        user_id = session['user_id']
        agreement = request.form.get('agreement')

        if not agreement:
            flash('You must agree to the terms and conditions.')
            return redirect(url_for('drop_off'))

        # Retrieve the username from the database using the user_id
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        username = user['username']

        file = request.files['file']

        if file and allowed_file(file.filename):
            extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{username}_{date}_{uuid.uuid4().hex}.{extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Ensure the upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(file_path)
            photo_path = os.path.join('uploads', unique_filename).replace('\\', '/')
        else:
            photo_path = None

        cursor.execute("INSERT INTO posts (title, date, username, location, photo) VALUES (?, ?, ?, ?, ?)", (item, date, username, location, photo_path))
        post_id = cursor.lastrowid
        cursor.execute("INSERT INTO drop_offs (item, location, date, photo, post_id) VALUES (?, ?, ?, ?, ?)", (item, location, date, photo_path, post_id))
        conn.commit()
        conn.close()

        flash('Drop off recorded successfully.')
        return redirect(url_for('home'))

    return render_template('drop_off.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hint = request.form['hint']
        secret_question = request.form['secret_question']
        secret_answer = request.form['secret_answer']

        # Check if the username already exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists. Please choose a different username or <a href="' + url_for('reset_password') + '">reset your password</a>.')
            return redirect(url_for('register'))

        # Hash the password, secret question, and secret answer before storing them
        hashed_password = generate_password_hash(password, method='scrypt', salt_length=16)
        hashed_secret_question = generate_password_hash(secret_question, method='scrypt', salt_length=16)
        hashed_secret_answer = generate_password_hash(secret_answer, method='scrypt', salt_length=16)

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password, hint, secret_question, secret_answer) VALUES (?, ?, ?, ?, ?)",
                       (username, hashed_password, hint, hashed_secret_question, hashed_secret_answer))
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        hint = request.form['hint']
        secret_question = request.form['secret_question']
        secret_answer = request.form['secret_answer']

        # Verify user information
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['hint'], hint) and check_password_hash(user['secret_question'], secret_question) and check_password_hash(user['secret_answer'], secret_answer):
            # Redirect to the page to enter a new password
            session['reset_username'] = username
            return redirect(url_for('set_new_password'))
        else:
            flash('Invalid information provided. Please try again.')
            conn.close()

    return render_template('reset_password.html')

@app.route('/set_new_password', methods=['GET', 'POST'])
def set_new_password():
    if 'reset_username' not in session:
        flash('Unauthorized access. Please start the password reset process again.')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        username = session['reset_username']

        # Hash the new password before storing it
        hashed_password = generate_password_hash(new_password, method='scrypt', salt_length=16)

        # Update the user's password in the database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()
        conn.close()

        session.pop('reset_username', None)
        flash('Password reset successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('set_new_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Handle login logic here
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            if check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = username  # Store the username in the session
                return jsonify(success=True)
            else:
                return jsonify(success=False, message='Invalid password. Would you like to reset your password?')
        else:
            return jsonify(success=False, message='Username does not exist. Would you like to register?')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)