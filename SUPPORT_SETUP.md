# Support Feature Setup Guide

## Overview
The Support feature includes three pages:
- **Support Hub** (4_support.py) - Main entry point with navigation to Q&A and Feedback
- **Q&A Page** (5_qa.py) - Display of common questions and answers
- **Feedback Page** (6_feedback.py) - Form for users to submit feedback via email

## Email Configuration

The feedback form requires email configuration to send feedback to the support team. 

### Environment Variables Required

Set the following environment variables before running the app:

```powershell
# SMTP Configuration
$env:REVTECH_SMTP_SERVER = "smtp.gmail.com"          # Default: smtp.gmail.com
$env:REVTECH_SMTP_PORT = "587"                       # Default: 587
$env:REVTECH_SENDER_EMAIL = "your-email@gmail.com"   # Required
$env:REVTECH_SENDER_PASSWORD = "your-app-password"   # Required (NOT your Gmail password)
$env:REVTECH_SUPPORT_EMAIL = "support@revtech.com"   # Email to receive feedback
```

### Using Gmail (Recommended)

1. **Enable 2-Factor Authentication** on your Google Account
2. **Generate an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Copy this password and use it as `REVTECH_SENDER_PASSWORD`

3. **Set Environment Variables**:
```powershell
$env:REVTECH_SENDER_EMAIL = "your-email@gmail.com"
$env:REVTECH_SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"  # The app password
$env:REVTECH_SUPPORT_EMAIL = "your-email@gmail.com"  # Or your team's email
```

4. **Run the app**:
```powershell
uv run revtech
```

### Using Other Email Providers

If using a different email provider (Outlook, SendGrid, etc.), adjust:
- `REVTECH_SMTP_SERVER` - Your provider's SMTP server
- `REVTECH_SMTP_PORT` - Your provider's SMTP port (usually 587 or 465)
- `REVTECH_SENDER_EMAIL` - Your email address
- `REVTECH_SENDER_PASSWORD` - Your email password or app-specific password

### Optional: Using Streamlit Secrets

Instead of environment variables, you can add to `.streamlit/secrets.toml`:

```toml
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "your-email@gmail.com"
sender_password = "xxxx xxxx xxxx xxxx"
support_email = "support@revtech.com"
```

Then modify `email_utils.py` to read from `st.secrets` if needed.

## Test Scenarios

### T.S.1 - Load the Support Page
1. Log in to RevTech
2. Click "Support" in the navigation bar
3. **Expected**: Support hub loads with Q&A and Feedback buttons visible

### T.S.2 - Q&A Button Navigation
1. On Support page, click "Go to Q&A" button
2. **Expected**: Q&A page loads with 10 frequently asked questions in expanders

### T.S.3.1 - Feedback Button Navigation
1. On Support page, click "Go to Feedback" button
2. **Expected**: Feedback page loads with dropdown menu and textbox visible

### T.S.3.2 - Feedback Submission (Email Test)
1. On Feedback page, fill out the form:
   - Email: your test email
   - Module: "Graph & Data Visualization"
   - Feedback: "This is a test feedback message"
2. Click "Submit Feedback"
3. **Expected**: 
   - Success message appears
   - Email is sent to the configured support email
   - Check the support email inbox for the feedback

## Code Structure

- `src/revtech/pages/4_support.py` - Support hub page
- `src/revtech/pages/5_qa.py` - Q&A page with FAQs
- `src/revtech/pages/6_feedback.py` - Feedback form page
- `src/revtech/email_utils.py` - Email sending utility functions
- `src/revtech/navigation.py` - Updated to include Support link

## Design Consistency

All pages follow the existing RevTech design:
- Centered layout with 3-column grid (1:2:1 ratio)
- Bordered containers for sections
- Consistent emoji icons (🏎️)
- Primary button styling with hover effects
- Dividers for visual separation
- Consistent heading hierarchy

## Requirements Coverage

✅ S.1.1 - Support page includes button to Q&A page
✅ S.1.2 - Q&A page displays common questions and answers
✅ S.2.1 - Support page includes link to feedback page
✅ S.2.2 - Feedback page displays dropdown and textbox
✅ T.S.1 - Support page loads completely
✅ T.S.2 - Q&A button directs to Q&A page
✅ T.S.3.1 - Feedback button directs to feedback page
✅ T.S.3.2 - Feedback page sends email to team
