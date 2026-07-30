import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "capstone-dev-secret-change-in-production")

# Demo credentials for the login page (replace with a database in a full app)
DEMO_USER = "admin"
DEMO_PASSWORD_HASH = generate_password_hash("admin123")


@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username == DEMO_USER
            and password
            and check_password_hash(DEMO_PASSWORD_HASH, password)
        ):
            session["user"] = username
            flash("Deployed. Welcome to the lineup board.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        flash("Sign in to deploy to the board.", "danger")
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    flash("You left the site. Sign in to deploy again.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
