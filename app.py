import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "capstone-dev-secret-change-in-production")

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

# Priority-ranked Today feed (max 5). Order = visual importance.
DEMO_TODAY = [
    {
        "type": "assessment",
        "priority": "primary",
        "kicker": "Due tomorrow — start now · Science",
        "title": "Ecosystems HOTS Assessment",
        "meta": "1 attempt · Assistive check · Posted by your Science teacher",
        "action": "Start now",
        "href": "/assessments/ecosystems",
    },
    {
        "type": "result",
        "priority": "secondary",
        "kicker": "Result released · English",
        "title": "Poetry analysis feedback is ready",
        "meta": "Review answers and explanations when you feel ready",
        "action": "Review",
        "href": "/results",
    },
    {
        "type": "practice",
        "priority": "secondary",
        "kicker": "Practice reminder · Math",
        "title": "Try a Fractions Practice Check",
        "meta": "Short practice from your approved lesson",
        "action": "Practice",
        "href": "/practice",
    },
    {
        "type": "upload",
        "priority": "secondary",
        "kicker": "Backup upload · Science",
        "title": "Lab handout is waiting for approval",
        "meta": "Your teacher will review before practice unlocks",
        "action": "View",
        "href": "/subjects/science",
    },
    {
        "type": "announcement",
        "priority": "tertiary",
        "kicker": "Announcement · English",
        "title": "Reading guide posted",
        "meta": "Also available anytime from the bell",
        "action": "Open",
        "href": "/announcements",
    },
]

DEMO_SUBJECTS = [
    {
        "slug": "english",
        "name": "English",
        "progress_label": "Progress 72% · Getting stronger in Evaluate",
        "progress_percent": 72,
        "next_action": "Next: Review poetry feedback",
    },
    {
        "slug": "mathematics",
        "name": "Mathematics",
        "progress_label": "Progress 58% · Practice building Analyze skills",
        "progress_percent": 58,
        "next_action": "Next: Fractions Practice Check",
    },
    {
        "slug": "science",
        "name": "Science",
        "progress_label": "Progress 41% · Assessment due tomorrow",
        "progress_percent": 41,
        "next_action": "Next: Ecosystems HOTS Assessment",
    },
]

DEMO_ASSESSMENTS = {
    "ecosystems": {
        "slug": "ecosystems",
        "subject": "Science",
        "title": "Ecosystems HOTS Assessment",
        "deadline_label": "Due tomorrow · 5:00 PM",
    }
}


def current_user():
    return session.get("user")


def require_user():
    user = current_user()
    if not user:
        flash("Please sign in to continue.", "danger")
        return None
    return user


DEMO_ANNOUNCEMENTS = [
    {
        "subject": "English",
        "title": "Reading guide posted",
        "meta": "Today · Mrs. Santos",
        "unread": True,
    },
    {
        "subject": "Science",
        "title": "Ecosystems assessment opens tomorrow",
        "meta": "Yesterday · Mr. Reyes",
        "unread": True,
    },
    {
        "subject": "Math",
        "title": "Fractions practice tips",
        "meta": "Mon · Ms. Cruz",
        "unread": True,
    },
]


def announcements_context():
    unread = sum(1 for note in DEMO_ANNOUNCEMENTS if note.get("unread"))
    return {
        "announcements_preview": DEMO_ANNOUNCEMENTS[:4],
        "unread_announcements": unread,
    }


def render_student_placeholder(user, title, message, active_tab):
    context = {
        "user": user,
        "title": title,
        "message": message,
        "active_tab": active_tab,
        "topbar_sub": title,
    }
    context.update(announcements_context())
    return render_template("placeholder.html", **context)


@app.route("/")
def index():
    if current_user():
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
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
            flash(
                "Welcome to Bloom. For security, change your temporary password in Profile later.",
                "success",
            )
            return redirect(url_for("home"))

        flash("School email or password is incorrect.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/home")
def home():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    if user["role"] == "teacher":
        return render_student_placeholder(
            user,
            "Teacher Home",
            "Teacher dashboard comes next. Student Home is ready for design review.",
            "home",
        )

    first_name = user["name"].split(" ")[0]
    context = {
        "user": user,
        "greeting": f"Hi, {first_name}",
        "topbar_sub": f"Hi, {first_name}",
        "guide_title": "Due tomorrow — start Science when you're ready",
        "guide_note": "Balanced plan for today: one assessment, one review, and light practice.",
        "weekly_goal": {
            "done": 2,
            "target": 3,
            "percent": 67,
            "hint": "Gentle goal only — no streak pressure. One more Practice Check this week is enough.",
        },
        "today_items": DEMO_TODAY[:5],
        "subjects": DEMO_SUBJECTS,
    }
    context.update(announcements_context())
    return render_template("student_home.html", **context)


@app.route("/assessments/<slug>")
def assessment_lobby(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    assessment = DEMO_ASSESSMENTS.get(slug)
    if not assessment:
        flash("That assessment is not available.", "danger")
        return redirect(url_for("home"))

    return render_template(
        "assessment_lobby.html",
        user=user,
        assessment=assessment,
        **announcements_context(),
    )


@app.route("/subjects/<slug>")
def subject_hub(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    names = {
        "english": "English",
        "mathematics": "Mathematics",
        "science": "Science",
    }
    name = names.get(slug, slug.title())
    return render_student_placeholder(
        user,
        name,
        "Subject hub (Assessments first) comes next.",
        "home",
    )


@app.route("/practice")
def practice():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    return render_student_placeholder(
        user,
        "Practice",
        "Practice hub comes next.",
        "practice",
    )


@app.route("/results")
def results():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    return render_student_placeholder(
        user,
        "Results",
        "Supportive results page comes next.",
        "results",
    )


@app.route("/profile")
def profile():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    return render_student_placeholder(
        user,
        "Profile",
        "Profile and password change come next.",
        "profile",
    )


@app.route("/announcements")
def announcements():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    return render_student_placeholder(
        user,
        "Announcements",
        "Shared announcements feed with subject filters comes next.",
        "home",
    )


@app.route("/logout")
def logout():
    session.clear()
    flash("You signed out of Bloom.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
