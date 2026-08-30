"""SQLite-backed user account operations shared by Streamlit pages."""

import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


DB_PATH = Path(__file__).resolve().parent / "users.db"


def get_db(db_path=None):
    """Open a connection with dictionary-style row access."""
    connection = sqlite3.connect(db_path or DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path=None):
    """Create the users table and seed a default admin on first run."""
    with get_db(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            connection.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", generate_password_hash("admin"), "admin"),
            )
            connection.commit()


def create_user(username, password, role="user", db_path=None):
    """Create a user with a securely hashed password and return its ID."""
    with get_db(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role),
        )
        connection.commit()
        return cursor.lastrowid


def find_user(username, db_path=None):
    with get_db(db_path) as connection:
        return connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def list_users(name_filter="", role_filter="All", db_path=None):
    query = "SELECT id, username, role FROM users WHERE username LIKE ?"
    parameters = [f"%{name_filter}%"]
    if role_filter != "All":
        query += " AND role = ?"
        parameters.append(role_filter)
    with get_db(db_path) as connection:
        return connection.execute(query + " ORDER BY id", parameters).fetchall()
