from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB_PATH = os.path.join(os.path.dirname(__file__), "studysphere.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT DEFAULT '',
            course TEXT NOT NULL, due_date TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium', status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter your name, a valid email and a password of at least 6 characters.", "error")
            return render_template("auth.html", mode="register")
        try:
            with db() as con:
                cur = con.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                                  (name, email, generate_password_hash(password)))
                session["user_id"] = cur.lastrowid
                session["name"] = name
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "error")
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"], session["name"] = user["id"], user["name"]
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "error")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    with db() as con:
        rows = con.execute("SELECT * FROM assignments WHERE user_id=? ORDER BY due_date",
                           (session["user_id"],)).fetchall()
    today = datetime.now().date().isoformat()
    total = len(rows)
    submitted = sum(r["status"] == "Submitted" for r in rows)
    pending = sum(r["status"] == "Pending" for r in rows)
    due_soon = sum(today <= r["due_date"] <= (datetime.now().date().replace(day=min(28, datetime.now().day+7))).isoformat()
                   and r["status"] != "Submitted" for r in rows)
    return render_template("dashboard.html", assignments=rows, total=total,
                           submitted=submitted, pending=pending, due_soon=due_soon)

@app.route("/assignments", methods=["GET", "POST"])
@login_required
def assignments():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        course = request.form.get("course", "").strip()
        due_date = request.form.get("due_date", "")
        if not title or not course or not due_date:
            flash("Title, course and due date are required.", "error")
        else:
            with db() as con:
                con.execute("""INSERT INTO assignments
                    (user_id,title,description,course,due_date,priority,status)
                    VALUES(?,?,?,?,?,?,?)""",
                    (session["user_id"], title, request.form.get("description","").strip(),
                     course, due_date, request.form.get("priority","Medium"),
                     request.form.get("status","Pending")))
            flash("Assignment added successfully.", "success")
        return redirect(url_for("assignments"))
    with db() as con:
        rows = con.execute("SELECT * FROM assignments WHERE user_id=? ORDER BY due_date",
                           (session["user_id"],)).fetchall()
    return render_template("assignments.html", assignments=rows)

@app.route("/assignments/<int:item_id>/edit", methods=["POST"])
@login_required
def edit_assignment(item_id):
    fields = (request.form.get("title","").strip(), request.form.get("description","").strip(),
              request.form.get("course","").strip(), request.form.get("due_date",""),
              request.form.get("priority","Medium"), request.form.get("status","Pending"),
              item_id, session["user_id"])
    with db() as con:
        con.execute("""UPDATE assignments SET title=?,description=?,course=?,due_date=?,
                    priority=?,status=? WHERE id=? AND user_id=?""", fields)
    flash("Assignment updated.", "success")
    return redirect(url_for("assignments"))

@app.route("/assignments/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_assignment(item_id):
    with db() as con:
        con.execute("DELETE FROM assignments WHERE id=? AND user_id=?",
                    (item_id, session["user_id"]))
    flash("Assignment deleted.", "success")
    return redirect(url_for("assignments"))

@app.route("/database")
def database_page():
    return render_template("database.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
