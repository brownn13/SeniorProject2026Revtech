"""RevTech Q&A page with common questions and answers.

Covers requirements:
- S.1.2: The Q/A page shall display common questions and answers users may have
- T.S.2: The Q/A button directs the user to the Q/A page
"""

import streamlit as st

from revtech.navigation import render_navigation

st.set_page_config(page_title="Q&A", page_icon="🏎️")

render_navigation("qa")

# Main content
_left, center, _right = st.columns([1, 2.5, 1])

with center:
    st.title("Frequently Asked Questions", text_alignment="center")
    st.caption("Find answers to common questions", text_alignment="center")

    # FAQ data
    faqs = [
        {
            "question": "How do I upload a CSV file?",
            "answer": "Navigate to the Graph page and click the 'Upload a CSV' section. Select your CSV file and it will be encrypted and saved securely to your account.",
        },
        {
            "question": "What file formats are supported?",
            "answer": "We support CSV (Comma-Separated Values) files with UTF-8 encoding. Files with leading metadata rows (starting with #) are automatically handled.",
        },
        {
            "question": "Are my uploaded files secure?",
            "answer": "Yes! All uploaded files are encrypted using industry-standard encryption (Fernet) and stored securely. Only you can access your files.",
        },
        {
            "question": "How do I create an account?",
            "answer": "Click 'Create Account' from the login page. Choose a username and password (at least 8 characters). Your account will be created immediately.",
        },
        {
            "question": "What if I forget my password?",
            "answer": "Currently, you'll need to contact the RevTech team at support@revtech.com to reset your password. We're working on self-service password reset!",
        },
        {
            "question": "Can I download my saved graphs?",
            "answer": "You can export graphs as images or data files. Use the download options available in the Graph page after generating your visualization.",
        },
        {
            "question": "Why is my graph not displaying correctly?",
            "answer": "Make sure your CSV contains at least one numeric column. Columns with text-only data are ignored. Check that your data formatting is consistent.",
        },
        {
            "question": "How long are files stored?",
            "answer": "Your encrypted files are stored indefinitely as long as your account remains active. You can delete any file at any time from the Graph page.",
        },
        {
            "question": "Is there a file size limit?",
            "answer": "Currently, CSV files up to 100MB are supported. For larger files, contact the support team at support@revtech.com.",
        },
        {
            "question": "How do I delete my account?",
            "answer": "Contact the RevTech team at support@revtech.com with your username. We can securely delete your account and all associated data.",
        },
    ]

    # Display FAQs with expanders
    with st.container(border=True):
        for idx, faq in enumerate(faqs):
            with st.expander(f"**{faq['question']}**"):
                st.write(faq["answer"])

    # Support contact section
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.info(
            "💬 **Still have questions?**\n\n"
            "Send us feedback using the feedback form and we'll get back to you!"
        )
    with col2:
        if st.button("Send Feedback", key="qa_feedback_btn", width="stretch"):
            st.switch_page("pages/6_feedback.py")
