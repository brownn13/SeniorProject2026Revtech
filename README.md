Login Pages Features:

Home page
Login page  ( default username is admin and password is admin )
Profile page to change password, which creates a secure, Salted hash of the password
Admin view users list page, and non-admins cannot access the users list
Admin can register a new user with a role and create a secure, salted hash of the password
Admin can delete a user
Admin can search users by name and role
On successful login, the user sees the dashboard page
Logout page


Source code under branch login_page in GitHub https://github.com/brownn13/SeniorProject2026Revtech/tree/login_page


Main login Python code is in loginapp.py and the SQLite database file is users.db
