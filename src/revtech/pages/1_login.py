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

from revtech.file_store import delete_user_uploads
from revtech.user_store import create_user, find_user, get_db, init_db, list_users

# Where to send the user after a successful login (requirement L.2.3).
# The dashboard page does not exist on main yet. When a teammate adds it,
# change this one line to "pages/3_dashboard.py".
LANDING_PAGE = "pages/2_graph.py"

st.set_page_config(page_title="Login", page_icon="🏎️")

# Presentation only. Everything is scoped to the .st-key-* classes that
# Streamlit adds for keyed containers, so the signed-in view below is
# untouched. Colours come from the theme variables so this still looks
# right if the team edits .streamlit/config.toml.
st.markdown(
    """
    <style>
    /* Less dead space above the title. */
    [data-testid="stMainBlockContainer"] { padding-top: 2.5rem; }

    /* Hero: big centred car above the title. */
    .st-key-login_hero { text-align: center; }
    .st-key-login_hero .revtech-emoji {
        font-size: 4rem;
        line-height: 1;
        margin-bottom: 0.25rem;
        animation: revtech-bob 2.6s ease-in-out infinite;
    }

    /* Card settles into place on load. */
    .st-key-login_card { animation: revtech-rise 0.45s ease-out both; }

    /* Submit button lifts slightly under the cursor. */
    .st-key-login_card [data-testid="stFormSubmitButton"] button {
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .st-key-login_card [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
        box-shadow: 0 4px 12px color-mix(
            in srgb, var(--primary-color, #4c8bf5) 35%, transparent
        );
    }

    /* Signed-in card matches the login card, with room before the
       full-width admin section that follows it. */
    .st-key-signed_in_card {
        animation: revtech-rise 0.45s ease-out both;
        margin-bottom: 1.5rem;
    }

    /* "Continue to the app" is the primary action here; the Log out
       button keeps Streamlit's quieter secondary styling. */
    .st-key-signed_in_card [data-testid="stPageLink"] a {
        background: var(--primary-color, #4c8bf5);
        border-radius: 0.5rem;
        justify-content: center;
        padding: 0.5rem 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .st-key-signed_in_card [data-testid="stPageLink"] a,
    .st-key-signed_in_card [data-testid="stPageLink"] a * {
        color: #ffffff;
    }
    .st-key-signed_in_card [data-testid="stPageLink"] a:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28);
        box-shadow: 0 4px 12px color-mix(
            in srgb, var(--primary-color, #4c8bf5) 35%, transparent
        );
    }

    @keyframes revtech-bob {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-6px); }
    }
    @keyframes revtech-rise {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: none; }
    }

    /* Motion is opt-out for anyone who asks the OS to reduce it. */
    @media (prefers-reduced-motion: reduce) {
        .st-key-login_hero .revtech-emoji,
        .st-key-login_card,
        .st-key-signed_in_card { animation: none; }
        .st-key-login_card [data-testid="stFormSubmitButton"] button,
        .st-key-login_card [data-testid="stFormSubmitButton"] button:hover,
        .st-key-signed_in_card [data-testid="stPageLink"] a,
        .st-key-signed_in_card [data-testid="stPageLink"] a:hover {
            transition: none;
            transform: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
    # Keep the form off the far-left edge on wide screens.
    _left, center, _right = st.columns([1, 2, 1])

    with center:
        with st.container(key="login_hero"):
            # text_alignment is the supported way to centre these; Streamlit
            # sets an explicit left alignment that plain inherited CSS loses to.
            st.markdown(
                '<div class="revtech-emoji">🏎️</div>',
                unsafe_allow_html=True,
                width="stretch",
                text_alignment="center",
            )
            st.title("RevTech", text_alignment="center")
            st.caption("Sign in to view your data logs", text_alignment="center")

        with st.container(border=True, key="login_card"):
            if st.session_state.pop("account_created", False):
                st.success("Account created successfully. You can now log in.")

            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input(
                    "Password", type="password", placeholder="Enter your password"
                )
                submitted = st.form_submit_button(
                    "Secure Log In", type="primary", width="stretch"
                )

            st.page_link(
                "pages/3_create_account.py",
                label="Create a new account",
                width="stretch",
            )

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
                    create_user(new_username, new_password, new_role)
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
                deleted_user_id = labels[choice]
                with get_db() as connection:
                    connection.execute(
                        "DELETE FROM users WHERE id = ?", (deleted_user_id,)
                    )
                    connection.commit()
                try:
                    delete_user_uploads(deleted_user_id)
                except OSError as error:
                    st.warning(
                        f"User deleted, but their saved logs could not be removed: {error}"
                    )
                    return
                st.success("User and saved logs deleted.")
                st.rerun()


def render_signed_in():
    user = current_user()

    # Same centred layout as the login view.
    _left, center, _right = st.columns([1, 2, 1])

    with center:
        with st.container(border=True, key="signed_in_card"):
            st.title(f"Welcome, {user['username']}!", text_alignment="center")
            st.caption(f"Signed in as: {user['role']}", text_alignment="center")

            # Requirement L.2.3 — send the user onward after a successful login.
            landing_path = Path(__file__).resolve().parent.parent / LANDING_PAGE
            if landing_path.exists():
                if st.session_state.pop("just_logged_in", False):
                    st.switch_page(LANDING_PAGE)
                st.page_link(
                    LANDING_PAGE,
                    label="Continue to the app",
                    icon="➡️",
                    width="stretch",
                )
            else:
                st.session_state.pop("just_logged_in", False)
                st.warning(
                    f"Landing page `{LANDING_PAGE}` was not found. "
                    "Update LANDING_PAGE at the top of this file once it exists."
                )

            if st.button("Log out", width="stretch"):
                sign_out()
                st.rerun()

        render_change_password()

    # Left at full width — the user table needs the horizontal space.
    if is_admin():
        render_admin_panel()


# --- PAGE -------------------------------------------------------------------

if current_user():
    render_signed_in()
else:
    render_login_form()
