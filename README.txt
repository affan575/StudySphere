STUDYSPHERE - VS CODE PROJECT
=============================

WHAT IS INCLUDED
- Home page
- Registration and login pages
- Student dashboard with assignment statistics
- Assignment CRUD (Create, Read, Update, Delete)
- Database / MERN architecture information page
- Dark purple responsive UI
- Python Flask backend with SQLite storage

RUN IN VS CODE (WINDOWS)
1. Extract the ZIP file.
2. Open the extracted StudySphere_VSCode folder in VS Code.
3. Open Terminal > New Terminal.
4. Create a virtual environment:
      py -m venv .venv
5. Activate it:
      .venv\Scripts\activate
6. Install requirements:
      pip install -r requirements.txt
7. Start the application:
      py app.py
8. Open this address in your browser:
      http://127.0.0.1:5000

FIRST USE
- Click Create account.
- Register with your name, email and password (minimum 6 characters).
- Log in and add assignments from the Assignments page.

DATABASE
The running demo stores accounts and assignments in studysphere.db (created automatically).
Passwords are stored as secure hashes, not plain text.
The Database page explains the MongoDB collections and MERN architecture from the supplied design.
This Python version uses SQLite so it can run immediately without installing MongoDB or Node.js.

IMPORTANT
- Do not share your SECRET_KEY in a public repository. Set a strong SECRET_KEY environment variable for deployment.
- This is a learning/demo project. For production, add CSRF protection, stronger validation and deployment security.
