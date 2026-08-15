import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_super_secret_session_encryption_key'
DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and adds the role column."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        ''')
        conn.commit()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        
        with get_db_connection() as conn:
            # Check if this is the very first user in the system
            user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            # Automatically make the first user an admin, others regular users
            role = 'admin' if user_count == 0 else 'user'
            
            try:
                conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                             (username, hashed_password, role))
                conn.commit()
                flash(f'Registration successful as {role}! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists.', 'error')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']  # Save role to session memory
            flash(f"Welcome back, {user['username']} ({user['role']})!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please log in to change your password.', 'error')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        
        with get_db_connection() as conn:
            user = conn.execute('SELECT password FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            
        if user and check_password_hash(user['password'], old_password):
            hashed_password = generate_password_hash(new_password)
            with get_db_connection() as conn:
                conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, session['user_id']))
                conn.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect current password.', 'error')
            
    return render_template('change_password.html')

@app.route('/users')
def users():
    # Protection barrier 1: Must be logged in
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
        
    # Protection barrier 2: Must be an admin
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
        
    with get_db_connection() as conn:
        user_records = conn.execute('SELECT id, username, role FROM users').fetchall()
        
    return render_template('users.html', users=user_records)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
