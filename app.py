import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "capstone-dev-secret-change-in-production")

# Temporary demo accounts for login UI testing (replace with real auth later)
DEMO_USERS = {
    "student@letran-calamba.edu.ph": {
        "password_hash": generate_password_hash("student123"),
        "name": "Demo Student",
        "role": "student",
    },
    "teacher@letran-calamba.edu.ph": {
        "password_hash": generate_password_hash("teacher123"),
        "name": "Demo Teacher",
        "role": "teacher",
    },
}


@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = DEMO_USERS.get(email)

        if user and password and check_password_hash(user["password_hash"], password):
            session["user"] = {
                "email": email,
                "name": user["name"],
                "role": user["role"],
            }
            flash("Welcome to Bloom. For security, change your temporary password in Profile later.", "success")
            return redirect(url_for("home"))

        flash("School email or password is incorrect.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/home")
def home():
    user = session.get("user")
    if not user:
        flash("Please sign in to continue.", "danger")
        return redirect(url_for("login"))

    return render_template("index.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    flash("You signed out of Bloom.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
