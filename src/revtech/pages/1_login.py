# 1_login.py
"""RevTech login page.

Ported from the Flask prototype on the `login_page` branch. The database
schema, scrypt password hashing, and admin/user role rules are unchanged,
so the existing users.db continues to work as-is.

Covers requirements L.1.1, L.1.2, L.2.1, L.2.2, L.2.3.
"""

import math
import sqlite3
from pathlib import Path
from urllib.parse import quote

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


# --- BACKGROUND -------------------------------------------------------------
#
# The card floats over a slow-scrolling telemetry trace. It is drawn as an SVG
# data URI rather than a real chart so it costs nothing at runtime and never
# fights Streamlit for layout: it lives entirely inside `background-image`.

# Racing red leads, with the theme blue from .streamlit/config.toml as the
# supporting channel and a muted steel for the calm line up top.
RED_COLOR = "#ff3b56"
PRIMARY_COLOR = "#4c8bf5"
STEEL_COLOR = "#93a9c9"

# One tile of the scrolling background, in SVG user units.
TILE_WIDTH = 1600
TILE_HEIGHT = 900


def rpm_shape(position):
    """Four gear pulls: a steep climb, then an instant drop at each shift."""
    pull = (position * 4.0) % 1.0
    return 0.22 + 0.78 * pull**0.7


def boost_shape(position):
    """Spools up right after each shift, then holds on the plateau."""
    pull = (position * 4.0) % 1.0
    return min(1.0, pull * 5.0) * (0.86 + 0.14 * math.sin(position * 40.0 * math.pi))


def afr_shape(position):
    """A calm channel that wanders around the middle of its range."""
    return (
        0.5
        + 0.30 * math.sin(6.0 * math.pi * position)
        + 0.12 * math.sin(16.0 * math.pi * position)
    )


def trace_path(shape, baseline, amplitude, samples=200):
    """Sample `shape` across one tile and return it as an SVG path.

    Every shape completes a whole number of cycles across the tile, so the
    right edge lines up with the left edge and the scroll loops seamlessly.
    """
    points = []
    for index in range(samples + 1):
        position = index / samples
        x = position * TILE_WIDTH
        y = baseline - amplitude * shape(position)
        points.append(f"{x:.0f} {y:.1f}")
    return "M " + " L ".join(points)


def background_image():
    """Build the `data:` URI for the telemetry backdrop."""
    rpm = trace_path(rpm_shape, 700.0, 170.0)
    boost = trace_path(boost_shape, 800.0, 110.0)
    # Sits high on the page so the composition is not all bottom-weighted.
    afr = trace_path(afr_shape, 320.0, 75.0)
    under_rpm = f"{rpm} L {TILE_WIDTH} {TILE_HEIGHT} L 0 {TILE_HEIGHT} Z"

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {TILE_WIDTH} {TILE_HEIGHT}" preserveAspectRatio="none">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{RED_COLOR}" stop-opacity="0.15"/>'
        f'<stop offset="100%" stop-color="{RED_COLOR}" stop-opacity="0"/>'
        "</linearGradient></defs>"
        f'<path d="{under_rpm}" fill="url(#g)"/>'
        f'<path d="{afr}" fill="none" stroke="{STEEL_COLOR}" '
        'stroke-opacity="0.30" stroke-width="2"/>'
        f'<path d="{boost}" fill="none" stroke="{PRIMARY_COLOR}" '
        'stroke-opacity="0.58" stroke-width="2.5"/>'
        # RPM is the hero channel: a wide faint pass for the glow, then the
        # crisp line on top.
        f'<path d="{rpm}" fill="none" stroke="{RED_COLOR}" '
        'stroke-opacity="0.14" stroke-width="11"/>'
        f'<path d="{rpm}" fill="none" stroke="{RED_COLOR}" '
        'stroke-opacity="0.70" stroke-width="2.5"/>'
        "</svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="")


# Presentation only. Everything that touches a card is scoped to the
# .st-key-* classes Streamlit adds for keyed containers, so the admin panel
# further down keeps its normal styling.
PAGE_STYLE = """
<style>
/* ---------- canvas ---------- */

[data-testid="stAppViewContainer"],
[data-testid="stHeader"] { background: transparent !important; }

/* Nothing to deploy from a sign-in screen. */
[data-testid="stAppDeployButton"] { display: none; }

.stApp {
    background:
        radial-gradient(900px 620px at 12% -5%,  rgba(76, 139, 245, 0.18), transparent 62%),
        radial-gradient(880px 660px at 85% 105%, rgba(255, 59, 86, 0.16), transparent 62%),
        linear-gradient(160deg, #0a070c 0%, #0b1018 48%, #10121c 100%) !important;
}

/* Instrument-cluster grid, faded off at the edges. */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.045) 1px, transparent 1px);
    background-size: 72px 72px;
    -webkit-mask-image: radial-gradient(125% 95% at 50% 40%, #000 22%, transparent 76%);
    mask-image: radial-gradient(125% 95% at 50% 40%, #000 22%, transparent 76%);
}

/* The scrolling telemetry trace. Tiles are a fixed width so the traces read
   at the same scale on any monitor, and one drift cycle moves the background
   by exactly one tile, which lands the next one seam-free. */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.55;
    background-image: url("__BACKGROUND__");
    background-size: 1100px 100vh;
    background-repeat: repeat-x;
    animation: revtech-drift 42s linear infinite;
    -webkit-mask-image: linear-gradient(180deg, transparent, #000 22%, #000 78%, transparent);
    mask-image: linear-gradient(180deg, transparent, #000 22%, #000 78%, transparent);
}

/* Page content sits above both backdrop layers. */
[data-testid="stMainBlockContainer"] {
    position: relative;
    z-index: 1;
    padding-top: 4rem;
    padding-bottom: 3.5rem;
}

/* ---------- the modal card ---------- */

.st-key-login_card,
.st-key-signed_in_card {
    max-width: 430px;
    margin: 0 auto;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.10) !important;
    border-radius: 24px !important;
    padding: 2.2rem 1.9rem 1.6rem !important;
    background: rgba(13, 18, 28, 0.62) !important;
    -webkit-backdrop-filter: blur(22px) saturate(140%);
    backdrop-filter: blur(22px) saturate(140%);
    box-shadow:
        0 30px 70px rgba(0, 0, 0, 0.55),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    animation: revtech-rise 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}

/* Hairline of colour along the top edge of the card. */
.st-key-login_card::before,
.st-key-signed_in_card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(
        90deg, transparent, rgba(76, 139, 245, 0.75), rgba(255, 59, 86, 0.95), transparent
    );
}

.st-key-signed_in_card { margin-bottom: 1.5rem; }

/* The admin panel is full width and data-heavy, so it gets a calmer, more
   opaque version of the same surface — traces running under a user table
   are hard to read. */
.st-key-admin_panel {
    margin-top: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 20px !important;
    padding: 1.6rem 1.8rem !important;
    background: rgba(11, 16, 25, 0.86) !important;
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
    box-shadow: 0 20px 46px rgba(0, 0, 0, 0.45);
}

/* ---------- card header ---------- */

.revtech-mark {
    width: 58px;
    height: 58px;
    margin: 0 auto 0.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    line-height: 1;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: linear-gradient(145deg, rgba(255, 59, 86, 0.42), rgba(76, 139, 245, 0.22));
    box-shadow:
        0 10px 26px rgba(255, 59, 86, 0.30),
        inset 0 1px 0 rgba(255, 255, 255, 0.20);
    animation: revtech-bob 3s ease-in-out infinite;
}

/* Streamlit gives every h1 a large font size and generous vertical padding.
   Both have to be overridden or the card grows a hole under the title. */
h1.revtech-title {
    margin: 0 0 0.35rem !important;
    padding: 0 !important;
    text-align: center;
    font-size: 1.55rem !important;
    line-height: 1.25;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(92deg, #ffffff, #ffd4dc 55%, #cfe0ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
}

/* Streamlit hides the anchor icon it adds next to headings only on hover. */
h1.revtech-title [data-testid="stHeaderActionElements"] { display: none; }

.revtech-sub {
    margin: 0 0 0.4rem !important;
    text-align: center;
    font-size: 0.88rem;
    color: rgba(250, 250, 250, 0.55);
}

.revtech-foot {
    margin: 1.1rem 0 0;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.07);
    text-align: center;
    font-size: 0.78rem;
    color: rgba(250, 250, 250, 0.42);
}

/* ---------- fields ---------- */

.st-key-login_card [data-baseweb="input"],
.st-key-login_card [data-baseweb="base-input"] {
    background: rgba(255, 255, 255, 0.045) !important;
    border-color: rgba(255, 255, 255, 0.10) !important;
    border-radius: 12px !important;
}
.st-key-login_card [data-baseweb="input"] input { background: transparent !important; }
.st-key-login_card [data-baseweb="input"]:focus-within {
    border-color: rgba(255, 59, 86, 0.85) !important;
    box-shadow: 0 0 0 3px rgba(255, 59, 86, 0.18);
}
.st-key-login_card label p {
    font-size: 0.82rem !important;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: rgba(250, 250, 250, 0.72) !important;
}
.st-key-login_card [data-testid="stAlert"] { border-radius: 12px; }

/* ---------- primary action ---------- */

.st-key-login_card [data-testid="stFormSubmitButton"] button {
    margin-top: 0.4rem;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    color: #ffffff !important;
    background: linear-gradient(135deg, #ff4d63, #e5123c 55%, #b5122f) !important;
    box-shadow: 0 10px 24px rgba(255, 59, 86, 0.38);
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}
.st-key-login_card [data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px);
    filter: brightness(1.08);
    box-shadow: 0 16px 32px rgba(255, 59, 86, 0.50);
}
.st-key-login_card [data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0);
}

/* "Continue to the app" is the primary action on the signed-in card; the
   Log out button keeps Streamlit's quieter secondary styling. */
.st-key-signed_in_card [data-testid="stPageLink"] a {
    border-radius: 12px;
    justify-content: center;
    padding: 0.55rem 1rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ff4d63, #e5123c 55%, #b5122f);
    box-shadow: 0 10px 24px rgba(255, 59, 86, 0.38);
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}
.st-key-signed_in_card [data-testid="stPageLink"] a,
.st-key-signed_in_card [data-testid="stPageLink"] a * { color: #ffffff; }
.st-key-signed_in_card [data-testid="stPageLink"] a:hover {
    transform: translateY(-2px);
    filter: brightness(1.08);
    box-shadow: 0 16px 32px rgba(255, 59, 86, 0.50);
}

/* ---------- motion ---------- */

@keyframes revtech-drift { to { background-position: -1100px 0; } }
@keyframes revtech-bob {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-5px); }
}
@keyframes revtech-rise {
    from { opacity: 0; transform: translateY(14px) scale(0.985); }
    to   { opacity: 1; transform: none; }
}

/* Motion is opt-out for anyone who asks the OS to reduce it. */
@media (prefers-reduced-motion: reduce) {
    .stApp::after,
    .revtech-mark,
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
"""

st.markdown(
    PAGE_STYLE.replace("__BACKGROUND__", background_image()),
    unsafe_allow_html=True,
)


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
    # Keep the card off the far-left edge on wide screens; the card's own
    # max-width does the rest.
    _left, center, _right = st.columns([1, 2, 1])

    with center:
        with st.container(border=True, key="login_card"):
            st.markdown(
                '<div class="revtech-mark">🏎️</div>'
                '<h1 class="revtech-title">Welcome back</h1>'
                '<p class="revtech-sub">Sign in to view your RevTech data logs</p>',
                unsafe_allow_html=True,
            )

            with st.form("login_form", border=False):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input(
                    "Password", type="password", placeholder="Enter your password"
                )
                submitted = st.form_submit_button(
                    "Secure Log In", type="primary", width="stretch"
                )

            # Handled inside the card so any failure stays in the modal.
            if submitted:
                if not username or not password:
                    st.error("Please enter both a username and a password.")
                else:
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
                            "Invalid credentials. Please check the username and "
                            "password before logging in."
                        )

            st.markdown(
                '<p class="revtech-foot">Accounts are issued by a RevTech '
                "administrator.</p>",
                unsafe_allow_html=True,
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

    # Same centred layout as the login view.
    _left, center, _right = st.columns([1, 2, 1])

    with center:
        with st.container(border=True, key="signed_in_card"):
            st.markdown(
                '<div class="revtech-mark">🏎️</div>'
                f'<h1 class="revtech-title">Welcome, {user["username"]}!</h1>'
                f'<p class="revtech-sub">Signed in as {user["role"]}</p>',
                unsafe_allow_html=True,
            )

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
        with st.container(border=True, key="admin_panel"):
            render_admin_panel()


# --- PAGE -------------------------------------------------------------------

if current_user():
    render_signed_in()
else:
    render_login_form()
