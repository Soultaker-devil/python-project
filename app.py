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

# Create Product table if it does not exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Product
               (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL, image_url TEXT, is_new INTEGER)''')

# Check if products already exist before inserting
cursor.execute('SELECT COUNT(*) FROM Product')
product_count = cursor.fetchone()[0]

if product_count == 0:
    # Add new products to the Product table
    products = [
        ("Air Max 90", "Classic Nike Air Max 90", 120.00, "air_max_90.jpg", 0),
        ("Yeezy Boost 350", "Adidas Yeezy Boost 350", 220.00, "yeezy_boost_350.jpg", 1),
        ("Jordan 1 Retro", "Air Jordan 1 Retro High OG", 170.00, "jordan_1_retro.jpg", 0),
        ("UltraBoost", "Adidas UltraBoost", 180.00, "ultraboost.jpg", 1),
        ("Chuck Taylor", "Converse Chuck Taylor All Star", 60.00, "chuck_taylor.jpg", 0),
        ("Vans Old Skool", "Vans Old Skool", 70.00, "vans_old_skool.jpg", 0),
        ("Puma Suede", "Puma Suede Classic", 65.00, "puma_suede.jpg", 0),
        ("New Balance 574", "New Balance 574", 80.00, "new_balance_574.jpg", 1)
    ]

    cursor.executemany('INSERT INTO Product (name, description, price, image_url, is_new) VALUES (?, ?, ?, ?, ?)', products)
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

@app.route('/shop')
def shop():
    cursor.execute('SELECT * FROM Product')
    products = cursor.fetchall()
    return render_template('shop.html', products=products)

@app.route('/new_arrivals')
def new_arrivals():
    cursor.execute('SELECT * FROM Product WHERE is_new = 1')
    products = cursor.fetchall()
    return render_template('new_arrivals.html', products=products)

@app.route('/buy_product/<int:product_id>')
def buy_product(product_id):
    cursor.execute('SELECT * FROM Product WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    if product:
        # Implement the logic for buying the product
        flash(f"You have bought {product[1]} for ${product[3]}")
        return redirect(url_for('shop'))
    else:
        flash("Product not found.")
        return redirect(url_for('shop'))

@app.route('/profile')
def profile():
    if 'username' in session:
        cursor.execute('SELECT * FROM User WHERE username = ?', (session['username'],))
        user = cursor.fetchone()
        return render_template('profile.html', user=user)
    else:
        flash("You need to log in to view your profile.")
        return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' in session:
        if request.method == 'POST':
            new_username = request.form['username']
            new_email = request.form['email']
            cursor.execute('UPDATE User SET username = ?, email = ? WHERE username = ?', (new_username, new_email, session['username']))
            conn.commit()
            session['username'] = new_username
            flash("Profile updated successfully")
            return redirect(url_for('profile'))
        cursor.execute('SELECT * FROM User WHERE username = ?', (session['username'],))
        user = cursor.fetchone()
        return render_template('edit_profile.html', user=user)
    else:
        flash("You need to log in to edit your profile.")
        return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/verify')
def verify():
    return render_template('verify.html')

@app.route('/orders')
def orders():
    if 'username' in session:
        cursor.execute('SELECT * FROM Orders WHERE user_id = (SELECT id FROM User WHERE username = ?)', (session['username'],))
        orders = cursor.fetchall()
        return render_template('orders.html', orders=orders)
    else:
        flash("You need to log in to view your orders.")
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
