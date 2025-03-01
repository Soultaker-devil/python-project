from flask import Flask, render_template, request, redirect, url_for, session, flash  # Importing necessary modules

import sqlite3

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Create (or connect to) SQLite database for users
conn = sqlite3.connect('SneaKpEEk.db', check_same_thread=False)
cursor = conn.cursor()

# Create User table if it does not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS User
               (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)''')

conn.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM User WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("No account found. Please sign up.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Debugging: Check if username or email already exists
        cursor.execute('SELECT * FROM User WHERE username = ? OR email = ?', (username, email))
        existing_user = cursor.fetchone()
        print(f"Existing user check: {existing_user}")  # Debugging statement
        
        if existing_user:
            flash("Username or email already exists. Please log in.")
            return redirect(url_for('login'))
        
        if password == confirm_password:
            cursor.execute('INSERT INTO User (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
            session['username'] = username
            flash("Account created successfully")
            return redirect(url_for('home'))
        else:
            flash("Passwords do not match.")
            return redirect(url_for('signup'))
    return render_template('signup.html')
        
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
