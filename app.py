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
        "teacher": "Mrs. Santos",
        "progress_label": "Progress 72% · Getting stronger in Evaluate",
        "progress_percent": 72,
        "next_action": "Next: Review poetry feedback",
    },
    {
        "slug": "mathematics",
        "name": "Mathematics",
        "teacher": "Ms. Cruz",
        "progress_label": "Progress 58% · Practice building Analyze skills",
        "progress_percent": 58,
        "next_action": "Next: Fractions Practice Check",
    },
    {
        "slug": "science",
        "name": "Science",
        "teacher": "Mr. Reyes",
        "progress_label": "Progress 41% · Assessment due tomorrow",
        "progress_percent": 41,
        "next_action": "Next: Ecosystems HOTS Assessment",
    },
]

SUBJECT_BY_SLUG = {item["slug"]: item for item in DEMO_SUBJECTS}

SUBJECT_HUB_CONTENT = {
    "science": {
        "assessments": {
            "due": [
                {
                    "title": "Ecosystems HOTS Assessment",
                    "status_label": "Due tomorrow — start now",
                    "meta": "1 attempt · Due tomorrow · 5:00 PM",
                    "action": "Start now",
                    "href": "/assessments/ecosystems",
                    "primary": True,
                }
            ],
            "open": [
                {
                    "title": "Cells HOTS Check",
                    "status_label": "Open",
                    "meta": "Due Friday · Assistive assessment",
                    "action": "Open",
                    "href": "/assessments/ecosystems",
                    "primary": False,
                }
            ],
            "closed": [
                {
                    "title": "Matter HOTS Check",
                    "status_label": "Closed",
                    "meta": "Submitted · Result pending release",
                    "action": "View",
                    "href": "/results",
                    "primary": False,
                }
            ],
        },
        "materials": [
            {
                "kicker": "Approved material",
                "title": "Ecosystems",
                "meta": "Summary ready · Citations included",
                "summary_href": "/subjects/science/summaries/ecosystems",
                "practice_href": "/subjects/science/practice/ecosystems",
            },
            {
                "kicker": "Approved material",
                "title": "Cells",
                "meta": "Summary ready",
                "summary_href": "/subjects/science/summaries/cells",
                "practice_href": "/subjects/science/practice/cells",
            },
        ],
        "pending_uploads": ["Lab handout.pdf"],
        "practice_items": [
            {
                "kicker": "Ready",
                "title": "Ecosystems Practice Check",
                "meta": "From approved lesson · Personal practice",
                "action": "Start",
                "href": "/subjects/science/practice/ecosystems",
                "locked": False,
            },
            {
                "kicker": "Waiting for approval",
                "title": "Lab handout practice",
                "meta": "Backup upload pending teacher review",
                "action": "Locked",
                "href": "#",
                "locked": True,
            },
        ],
        "results": [
            {
                "kicker": "Pending release",
                "title": "Matter HOTS Check",
                "meta": "Submitted · Feedback not released yet",
                "action": "Waiting",
                "href": "/results",
            }
        ],
    },
    "mathematics": {
        "assessments": {"due": [], "open": [], "closed": []},
        "materials": [
            {
                "kicker": "New summary",
                "title": "Fractions",
                "meta": "AI summary ready with citations",
                "summary_href": "/subjects/mathematics/summaries/fractions",
                "practice_href": "/subjects/mathematics/practice/fractions",
            }
        ],
        "pending_uploads": [],
        "practice_items": [
            {
                "kicker": "Ready",
                "title": "Fractions Practice Check",
                "meta": "Great next step for Analyze skills",
                "action": "Start",
                "href": "/practice",
                "locked": False,
            }
        ],
        "results": [],
    },
    "english": {
        "assessments": {"due": [], "open": [], "closed": []},
        "materials": [
            {
                "kicker": "Approved material",
                "title": "Poetry analysis",
                "meta": "Reading guide available",
                "summary_href": "/subjects/english/summaries/poetry-analysis",
                "practice_href": "/subjects/english/practice/poetry-analysis",
            }
        ],
        "pending_uploads": [],
        "practice_items": [
            {
                "kicker": "Ready",
                "title": "Poetry Practice Check",
                "meta": "Review Evaluate skills",
                "action": "Start",
                "href": "/practice",
                "locked": False,
            }
        ],
        "results": [
            {
                "kicker": "Released",
                "title": "Poetry analysis feedback",
                "meta": "Score and explanations ready",
                "action": "Review",
                "href": "/results",
            }
        ],
    },
}

DEMO_ASSESSMENTS = {
    "ecosystems": {
        "slug": "ecosystems",
        "subject": "Science",
        "title": "Ecosystems HOTS Assessment",
        "deadline_label": "Due tomorrow · 5:00 PM",
    }
}

DEMO_SUMMARIES = {
    "science": {
        "ecosystems": {
            "slug": "ecosystems",
            "title": "Ecosystems",
            "intro": "A short student-friendly summary from your teacher’s uploaded material.",
            "sections": [
                {
                    "id": "intro",
                    "heading": "What is an ecosystem?",
                    "body": "An ecosystem is a community of living things interacting with each other and with non-living parts of the environment, such as sunlight, water, and soil.",
                    "citation": "pp. 2–3",
                },
                {
                    "id": "food-chains",
                    "heading": "Food chains",
                    "body": "Food chains show how energy moves from one organism to another. Producers make food, consumers eat other organisms, and decomposers break down dead matter.",
                    "citation": "pp. 4–5",
                },
                {
                    "id": "energy-flow",
                    "heading": "Energy flow",
                    "body": "Energy flows in one direction through an ecosystem. Only part of the energy is passed to the next level, which is why food chains are usually short.",
                    "citation": "p. 6",
                },
            ],
        },
        "cells": {
            "slug": "cells",
            "title": "Cells",
            "intro": "Key ideas from your Cells lesson, grounded only in the uploaded material.",
            "sections": [
                {
                    "id": "basics",
                    "heading": "Cell basics",
                    "body": "Cells are the basic units of life. Plant and animal cells share some parts, but plant cells have unique structures such as a cell wall and chloroplasts.",
                    "citation": "pp. 1–2",
                },
                {
                    "id": "organelles",
                    "heading": "Important parts",
                    "body": "The nucleus controls the cell, mitochondria release energy, and the membrane protects the cell while controlling what enters and leaves.",
                    "citation": "pp. 3–4",
                },
            ],
        },
    },
    "mathematics": {
        "fractions": {
            "slug": "fractions",
            "title": "Fractions",
            "intro": "A calm walkthrough of the main fraction ideas from your lesson.",
            "sections": [
                {
                    "id": "meaning",
                    "heading": "What fractions mean",
                    "body": "A fraction shows equal parts of a whole. The denominator tells how many equal parts there are, and the numerator tells how many parts are being considered.",
                    "citation": "pp. 1–2",
                },
                {
                    "id": "compare",
                    "heading": "Comparing fractions",
                    "body": "Fractions are easier to compare when they share the same denominator. Equivalent fractions name the same amount in different forms.",
                    "citation": "pp. 3–4",
                },
            ],
        }
    },
    "english": {
        "poetry-analysis": {
            "slug": "poetry-analysis",
            "title": "Poetry analysis",
            "intro": "A short guide to reading poems carefully using your class material.",
            "sections": [
                {
                    "id": "notice",
                    "heading": "Notice the language",
                    "body": "Look for word choice, imagery, and repeated sounds. These details help you understand the poem’s mood and message.",
                    "citation": "pp. 1–2",
                },
                {
                    "id": "evidence",
                    "heading": "Support your ideas",
                    "body": "When you make a claim about a poem, support it with short quoted evidence and explain how the evidence connects to your idea.",
                    "citation": "p. 3",
                },
            ],
        }
    },
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


@app.route("/subjects/<slug>/summaries/<material_slug>")
def summary_reader(slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    subject = SUBJECT_BY_SLUG.get(slug)
    summary = DEMO_SUMMARIES.get(slug, {}).get(material_slug)
    if not subject or not summary:
        flash("That summary is not available.", "danger")
        return redirect(url_for("home"))

    context = {
        "user": user,
        "subject": subject,
        "summary": summary,
    }
    context.update(announcements_context())
    return render_template("summary_reader.html", **context)


@app.route("/subjects/<subject_slug>/practice/<material_slug>")
def practice_setup(subject_slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    subject = SUBJECT_BY_SLUG.get(subject_slug)
    summary = DEMO_SUMMARIES.get(subject_slug, {}).get(material_slug)
    if not subject or not summary:
        flash("That practice setup is not available.", "danger")
        return redirect(url_for("home"))

    context = {
        "user": user,
        "subject": subject,
        "material_title": summary["title"],
        "back_href": url_for(
            "summary_reader", slug=subject_slug, material_slug=material_slug
        ),
    }
    context.update(announcements_context())
    return render_template("practice_setup.html", **context)


@app.route("/subjects/<slug>")
def subject_hub(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    subject = SUBJECT_BY_SLUG.get(slug)
    if not subject:
        flash("That subject is not available.", "danger")
        return redirect(url_for("home"))

    tab = request.args.get("tab", "assessments")
    if tab not in {"assessments", "study", "practice", "results"}:
        tab = "assessments"

    content = SUBJECT_HUB_CONTENT.get(slug, {})
    assessments = content.get("assessments", {"due": [], "open": [], "closed": []})
    assessment_groups = [
        {"label": "Due", "entries": assessments.get("due", [])},
        {"label": "Open", "entries": assessments.get("open", [])},
        {"label": "Closed", "entries": assessments.get("closed", [])},
    ]

    context = {
        "user": user,
        "subject": subject,
        "tab": tab,
        "assessment_groups": assessment_groups,
        "materials": content.get("materials", []),
        "pending_uploads": content.get("pending_uploads", []),
        "practice_items": content.get("practice_items", []),
        "result_items": content.get("results", []),
    }
    context.update(announcements_context())
    return render_template("subject_hub.html", **context)


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
