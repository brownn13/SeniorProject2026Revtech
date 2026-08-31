"""RevTech support hub page.

Covers requirements:
- S.1.1: The support page shall include a button to the Q/A page
- S.2.1: The support page shall include a link to the feedback page
- T.S.1: Load the support page completely
"""

import streamlit as st

from revtech.navigation import render_navigation

st.set_page_config(page_title="Support", page_icon="🏎️")

render_navigation("support")

# Main content
_left, center, _right = st.columns([1, 2, 1])

with center:
    st.title("Support Center", text_alignment="center")
    st.caption(
        "Get help, find answers, or send us feedback",
        text_alignment="center",
    )

    with st.container(border=True):
        st.subheader("📚 Need Help?", divider="green")
        st.write(
            "Browse our frequently asked questions to find quick answers to common issues."
        )
        if st.button("Go to Q&A", key="support_qa_btn", width="stretch", type="primary"):
            st.switch_page("pages/5_qa.py")

    with st.container(border=True):
        st.subheader("💬 Send Us Feedback", divider="blue")
        st.write(
            "Have suggestions or encountered an issue? We'd love to hear from you!"
        )
        if st.button(
            "Go to Feedback", key="support_feedback_btn", width="stretch", type="primary"
        ):
            st.switch_page("pages/6_feedback.py")
