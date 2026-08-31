"""RevTech feedback page.

Covers requirements:
- S.2.2: The feedback page shall display a dropdown menu, and a textbox where 
         the user must select the desired module from the dropdown menu and type in 
         the feedback in the textbox
- T.S.3.1: The feedback button directs the user to the feedback page
- T.S.3.2: The feedback page displays a dropdown menu and textbox. When the user 
          enters their feedback and pressed the submit button, the response will be 
          emailed to the team.
"""

import streamlit as st

from revtech.email_utils import send_feedback_email
from revtech.navigation import render_navigation

st.set_page_config(page_title="Feedback", page_icon="🏎️")

render_navigation("feedback")

# Main content
_left, center, _right = st.columns([1, 2, 1])

with center:
    st.title("Send Us Feedback", text_alignment="center")
    st.caption(
        "Help us improve RevTech by sharing your thoughts",
        text_alignment="center",
    )

    with st.container(border=True):
        with st.form("feedback_form", clear_on_submit=True):
            # Get current user info
            current_user = st.session_state.get("auth_user")
            user_name = current_user["username"] if current_user else ""
            user_email = st.text_input(
                "Your Email",
                placeholder="example@email.com",
                help="We'll use this to contact you if we need more details",
            )

            # Module selection dropdown
            modules = [
                "Select a module...",
                "Login & Authentication",
                "Account Management",
                "Graph & Data Visualization",
                "File Upload & Storage",
                "General / Other",
            ]
            module = st.selectbox(
                "What module is your feedback about?",
                modules,
                help="Select the feature or area of RevTech your feedback relates to",
            )

            # Feedback text area
            feedback_text = st.text_area(
                "Your Feedback",
                placeholder="Tell us what you think... (minimum 10 characters)",
                height=200,
                help="Please provide detailed feedback to help us improve",
            )

            # Submit button
            submitted = st.form_submit_button(
                "Submit Feedback",
                type="primary",
                width="stretch",
                use_container_width=True,
            )

        # Handle form submission
        if submitted:
            # Validation
            validation_errors = []

            if not user_email or "@" not in user_email:
                validation_errors.append("Please enter a valid email address")

            if module == "Select a module...":
                validation_errors.append("Please select a module")

            if not feedback_text or len(feedback_text) < 10:
                validation_errors.append("Feedback must be at least 10 characters long")

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # Send the feedback email
                success, message = send_feedback_email(
                    user_name=user_name or "Anonymous User",
                    user_email=user_email,
                    module=module,
                    feedback=feedback_text,
                )

                if success:
                    st.success(message)
                    st.info(
                        "💡 **Tip**: You can always send more feedback using this form!"
                    )
                else:
                    st.error(message)

    # Contact info section
    st.divider()
    st.info(
        "📧 **Direct Contact**\n\n"
        "If you prefer to email us directly, reach out to: **support@revtech.com**"
    )
