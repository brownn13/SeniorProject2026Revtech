"""Shared navigation controls for RevTech pages."""

import streamlit as st


def render_navigation(current_page):
    """Render page and authentication actions without using the sidebar."""
    current_user = st.session_state.get("auth_user")
    actions = []

    if current_page != "home":
        actions.append(("Home", "launch.py"))
    if current_user and current_page != "graph":
        actions.append(("Graph", "pages/2_graph.py"))

    spacer, *action_columns = st.columns([6, *([1] * (len(actions) + 1))])
    del spacer

    for column, (label, page) in zip(action_columns, actions):
        if column.button(label, key=f"nav_{label.lower()}", width="stretch"):
            st.switch_page(page)

    auth_column = action_columns[-1]
    if current_user:
        if auth_column.button("Logout", key="nav_logout", width="stretch"):
            st.session_state.pop("auth_user", None)
            st.session_state.pop("just_logged_in", None)
            st.switch_page("launch.py")
    elif auth_column.button("Login", key="nav_login", width="stretch"):
        st.switch_page("pages/1_login.py")
