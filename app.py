import os
import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


def _valid_email(email):
    local, sep, domain = email.partition("@")
    return bool(local) and bool(sep) and "." in domain and not domain.startswith(".") \
        and not domain.endswith(".") and " " not in email


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    def fail(message):
        return render_template("register.html", error=message, name=name, email=email), 400

    if not name or not email or not password:
        return fail("All fields are required.")
    if not _valid_email(email):
        return fail("Please enter a valid email address.")
    if len(password) < 8:
        return fail("Password must be at least 8 characters.")

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return fail("An account with this email already exists.")
    finally:
        conn.close()

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    error = "Invalid email or password."

    if not email or not password:
        return render_template("login.html", error=error, email=email), 401

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error=error, email=email), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (session["user_id"],),
        ).fetchone()

        if user is None:
            session.clear()
            return redirect(url_for("login"))

        summary = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS count "
            "FROM expenses WHERE user_id = ?",
            (session["user_id"],),
        ).fetchone()
    finally:
        conn.close()

    member_since = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %Y")
    total_spent = f"₹{summary['total']:,.2f}"

    return render_template(
        "profile.html",
        user=user,
        member_since=member_since,
        total_spent=total_spent,
        expense_count=summary["count"],
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
