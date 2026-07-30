import os

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "capstone-dev-secret-change-in-production")

# Demo credentials for the login page (replace with a database in a full app)
DEMO_USER = "admin"
DEMO_PASSWORD_HASH = generate_password_hash("admin123")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if (
            username == DEMO_USER
            and password
            and check_password_hash(DEMO_PASSWORD_HASH, password)
        ):
            flash("Login successful.", "success")
        else:
            flash("Invalid username or password.", "danger")

        return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
