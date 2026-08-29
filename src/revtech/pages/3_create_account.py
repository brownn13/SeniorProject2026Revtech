"""Self-service account registration page."""

import sqlite3

import streamlit as st

from revtech.user_store import create_user, init_db


st.set_page_config(page_title="Create Account", page_icon="🏎️")
init_db()

_left, center, _right = st.columns([1, 2, 1])

with center:
    st.title("Create an account", text_alignment="center")
    st.caption("Register to view and graph your data logs", text_alignment="center")

    with st.container(border=True):
        with st.form("create_account_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            password = st.text_input(
                "Password",
                type="password",
                placeholder="At least 8 characters",
            )
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button(
                "Create account", type="primary", width="stretch"
            )

        st.page_link(
            "pages/1_login.py",
            label="Back to login",
            width="stretch",
        )

    if submitted:
        username = username.strip()
        if not username:
            st.error("Please enter a username.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                create_user(username, password, role="user")
            except sqlite3.IntegrityError:
                st.error("That username already exists.")
            else:
                st.session_state.account_created = True
                st.switch_page("pages/1_login.py")
