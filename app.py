import os

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "capstone-dev-secret-change-in-production")

# Demo credentials for the login page (replace with a database in a full app)
DEMO_USER = "admin"
DEMO_PASSWORD_HASH = generate_password_hash("admin123")

LINEUPS = {
    "window": {
        "slug": "window",
        "title": "Window",
        "site": "A-site",
        "summary": "Stand mid window, aim the beam at the arch lip, left-click throw.",
        "steps": [
            "From T Spawn, move to the left side near the wooden cart / trash bin.",
            "Look up toward the rooftops and find the antenna / railing lineup mark.",
            "Align your crosshair, then jump-throw the smoke so it blooms inside Window.",
            "The smoke blocks the AWP nest so your team can take mid safely.",
        ],
        # Swap youtube_id or drop a file at static/videos/window.mp4
        "youtube_id": "mWGQa2K4uQs",
        "video_file": "videos/window.mp4",
        "ready": True,
    },
    "jungle": {
        "slug": "jungle",
        "title": "Jungle",
        "site": "A-site",
        "summary": "From stairs, align crosshair with the teal mark and jump-throw.",
        "steps": [],
        "youtube_id": None,
        "video_file": "videos/jungle.mp4",
        "ready": False,
    },
}


def login_required():
    if not session.get("user"):
        flash("Sign in to deploy to the board.", "danger")
        return False
    return True


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
    if not login_required():
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["user"],
        lineups=LINEUPS.values(),
    )


@app.route("/lineup/<slug>")
def lineup(slug):
    if not login_required():
        return redirect(url_for("login"))

    entry = LINEUPS.get(slug)
    if not entry or not entry.get("ready"):
        abort(404)

    local_video = None
    video_path = entry.get("video_file")
    if video_path:
        full_path = os.path.join(app.static_folder, video_path)
        if os.path.isfile(full_path):
            local_video = video_path

    return render_template(
        "lineup.html",
        username=session["user"],
        lineup=entry,
        local_video=local_video,
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You left the site. Sign in to deploy again.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
