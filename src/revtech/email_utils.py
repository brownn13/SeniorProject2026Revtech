"""Email utilities for RevTech support feedback."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_feedback_email(user_name: str, user_email: str, module: str, feedback: str) -> tuple[bool, str]:
    """
    Send feedback email to the RevTech support team.
    
    Args:
        user_name: Name of the user submitting feedback
        user_email: Email of the user submitting feedback
        module: Module the feedback is about
        feedback: The feedback text
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Get email configuration from environment
    smtp_server = os.environ.get("REVTECH_SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("REVTECH_SMTP_PORT", "587"))
    sender_email = os.environ.get("REVTECH_SENDER_EMAIL")
    sender_password = os.environ.get("REVTECH_SENDER_PASSWORD")
    support_email = os.environ.get("REVTECH_SUPPORT_EMAIL", "support@revtech.com")
    
    # Validate configuration
    if not sender_email or not sender_password:
        return (
            False,
            "Email configuration is incomplete. Please contact the RevTech team directly.",
        )
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = support_email
        msg["Subject"] = f"RevTech Feedback: {module}"
        
        # Create email body
        body = f"""
New Feedback from RevTech User

User Name: {user_name}
User Email: {user_email}
Module: {module}

Feedback:
{feedback}

---
This email was sent automatically by the RevTech feedback system.
"""
        
        msg.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True, "Thank you! Your feedback has been sent to the RevTech team."
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please contact support directly."
    except smtplib.SMTPException as e:
        return False, f"Failed to send email: {str(e)}"
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"
