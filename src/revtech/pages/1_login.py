# 1_login.py
"""RevTech login page.

Ported from the Flask prototype on the `login_page` branch. The database
schema, scrypt password hashing, and admin/user role rules are unchanged,
so the existing users.db continues to work as-is.

Covers requirements L.1.1, L.1.2, L.2.1, L.2.2, L.2.3.
"""

import sqlite3
from pathlib import Path

import streamlit as st
from werkzeug.security import check_password_hash, generate_password_hash

# Where to send the user after a successful login (requirement L.2.3).
# The dashboard page does not exist on main yet. When a teammate adds it,
# change this one line to "pages/3_dashboard.py".
LANDING_PAGE = "pages/2_graph.py"

# users.db lives next to launch.py so it is found no matter which
# directory Streamlit is started from.
DB_PATH = Path(__file__).resolve().parent.parent / "users.db"

st.set_page_config(page_title="Login", page_icon="🏎️")


# --- DATABASE ---------------------------------------------------------------


def get_db():
    """Open a connection with dictionary-style row access."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the users table and seed a default admin on first run."""
    with get_db() as connection:
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


def find_user(username):
    with get_db() as connection:
        return connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def list_users(name_filter="", role_filter="All"):
    query = "SELECT id, username, role FROM users WHERE username LIKE ?"
    parameters = [f"%{name_filter}%"]
    if role_filter != "All":
        query += " AND role = ?"
        parameters.append(role_filter)
    with get_db() as connection:
        return connection.execute(query + " ORDER BY id", parameters).fetchall()


init_db()


# --- SESSION HELPERS --------------------------------------------------------


def current_user():
    """Return the signed-in user dict, or None."""
    return st.session_state.get("auth_user")


def is_admin():
    user = current_user()
    return bool(user) and user["role"] == "admin"


def sign_out():
    st.session_state.pop("auth_user", None)
    st.session_state.pop("just_logged_in", None)


# --- LOGIN FORM (L.1.1, L.1.2, L.2.1, L.2.2) --------------------------------


def render_login_form():
    st.title("System Sign In")
    st.caption("Please enter your credentials to continue.")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input(
            "Password", type="password", placeholder="Enter your password"
        )
        submitted = st.form_submit_button("Secure Log In")

    if not submitted:
        return

    if not username or not password:
        st.error("Please enter both a username and a password.")
        return

    user = find_user(username)
    if user and check_password_hash(user["password"], password):
        st.session_state.auth_user = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        }
        st.session_state.just_logged_in = True
        st.rerun()
    else:
        # Requirement L.2.2
        st.error(
            "Invalid credentials. Please check the username and password "
            "before logging in."
        )


# --- SIGNED-IN VIEW ---------------------------------------------------------


def render_change_password():
    with st.expander("Change my password"):
        with st.form("change_password_form"):
            current_password = st.text_input("Current password", type="password")
            new_password = st.text_input("New password", type="password")
            confirm_password = st.text_input("Confirm new password", type="password")
            submitted = st.form_submit_button("Update password")

        if not submitted:
            return

        if new_password != confirm_password:
            st.error("New passwords do not match.")
            return
        if not new_password:
            st.error("New password cannot be blank.")
            return

        user_id = current_user()["id"]
        with get_db() as connection:
            row = connection.execute(
                "SELECT password FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if row and check_password_hash(row["password"], current_password):
                connection.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (generate_password_hash(new_password), user_id),
                )
                connection.commit()
                st.success("Your password has been updated.")
            else:
                st.error("Incorrect current password.")


def render_admin_panel():
    st.divider()
    st.subheader("User management")
    st.caption("Visible to administrators only.")

    search_column, role_column = st.columns(2)
    name_filter = search_column.text_input("Search by username", key="user_search")
    role_filter = role_column.selectbox("Filter by role", ["All", "admin", "user"])

    users = list_users(name_filter, role_filter)
    st.dataframe(
        [{"ID": u["id"], "Username": u["username"], "Role": u["role"]} for u in users],
        hide_index=True,
        width="stretch",
    )

    with st.expander("Register a new user"):
        with st.form("register_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            submitted = st.form_submit_button("Create user")

        if submitted:
            if not new_username or not new_password:
                st.error("All fields are required.")
            else:
                try:
                    with get_db() as connection:
                        connection.execute(
                            "INSERT INTO users (username, password, role) "
                            "VALUES (?, ?, ?)",
                            (
                                new_username,
                                generate_password_hash(new_password),
                                new_role,
                            ),
                        )
                        connection.commit()
                    st.success(f'User "{new_username}" registered successfully.')
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That username already exists.")

    with st.expander("Delete a user"):
        deletable = [u for u in users if u["id"] != current_user()["id"]]
        if not deletable:
            st.info("No other users available to delete.")
        else:
            labels = {f'{u["username"]} (ID {u["id"]})': u["id"] for u in deletable}
            choice = st.selectbox("Select a user", list(labels))
            if st.button("Delete user", type="primary"):
                with get_db() as connection:
                    connection.execute(
                        "DELETE FROM users WHERE id = ?", (labels[choice],)
                    )
                    connection.commit()
                st.success("User deleted.")
                st.rerun()


def render_signed_in():
    user = current_user()
    st.title(f"Welcome, {user['username']}!")
    st.caption(f"Signed in as: {user['role']}")

    # Requirement L.2.3 — send the user onward after a successful login.
    landing_path = Path(__file__).resolve().parent.parent / LANDING_PAGE
    if landing_path.exists():
        if st.session_state.pop("just_logged_in", False):
            st.switch_page(LANDING_PAGE)
        st.page_link(LANDING_PAGE, label="Continue to the app", icon="➡️")
    else:
        st.session_state.pop("just_logged_in", False)
        st.warning(
            f"Landing page `{LANDING_PAGE}` was not found. "
            "Update LANDING_PAGE at the top of this file once it exists."
        )

    if st.button("Log out"):
        sign_out()
        st.rerun()

    render_change_password()

    if is_admin():
        render_admin_panel()


# --- PAGE -------------------------------------------------------------------

if current_user():
    render_signed_in()
else:
    render_login_form()
