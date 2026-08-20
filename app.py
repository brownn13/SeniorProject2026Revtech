import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash  # type: ignore
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user  # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# --- FLASK-LOGIN SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'error'

class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = int(user_id)
        self.username = username
        self.role = role

    @property
    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None


# --- CUSTOM ROLE DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Correctly check if any users exist by fetching the first index [0]
        row_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        
        if row_count == 0:
            admin_username = 'admin'
            hashed_password = generate_password_hash('admin')
            admin_role = 'admin'
            
            conn.execute(
                'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                (admin_username, hashed_password, admin_role)
            )
            conn.commit()


# --- APPLICATION ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        with get_db() as conn:
            user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            role = 'admin' if user_count == 0 else 'user'
            
            try:
                conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                             (username, password, role))
                conn.commit()
                flash('Registered successfully!', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists.', 'error')
                
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)
            return redirect(url_for('home'))
            
        flash('Invalid credentials.', 'error')
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


# --- PROFILE & PASSWORD MANAGEMENT ---

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('profile'))
            
        with get_db() as conn:
            # Fetch user password hash from the database
            user = conn.execute('SELECT password FROM users WHERE id = ?', (current_user.id,)).fetchone()
            
            # Verify the old password matches our recorded hash
            if user and check_password_hash(user['password'], current_password):
                hashed_password = generate_password_hash(new_password)
                conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, current_user.id))
                conn.commit()
                flash('Your password has been updated successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Incorrect current password.', 'error')
                
    return render_template('profile.html')


# --- PROTECTED ADMIN ROUTES ---

@app.route('/users')
@login_required
@admin_required
def user_list():
    with get_db() as conn:
        users = conn.execute('SELECT id, username, role FROM users').fetchall()
    return render_template('users.html', users=users)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('user_list'))
        
    with get_db() as conn:
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        
    flash('User deleted.', 'success')
    return redirect(url_for('user_list'))

@app.route('/admin/register', methods=['POST'])
@login_required
@admin_required
def register_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password or not role:
        flash('All fields are required.', 'error')
        return redirect(url_for('user_list'))

    hashed_password = generate_password_hash(password)

    with get_db() as conn:
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                         (username, hashed_password, role))
            conn.commit()
            flash(f'User "{username}" registered successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'error')

    return redirect(url_for('user_list'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

