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
        "subject": None,
    },
    "teacher@letran-calamba.edu.ph": {
        "password_hash": generate_password_hash("teacher123"),
        "name": "Demo Teacher",
        "role": "teacher",
        "subject": "Science",
    },
    "admin@letran-calamba.edu.ph": {
        "password_hash": generate_password_hash("admin123"),
        "name": "Demo Admin",
        "role": "admin",
        "subject": None,
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
                "subject": user.get("subject"),
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
        return redirect(url_for("teacher_home"))
    if user["role"] == "admin":
        return redirect(url_for("admin_home"))

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
        "material_slug": material_slug,
        "material_title": summary["title"],
        "back_href": url_for(
            "summary_reader", slug=subject_slug, material_slug=material_slug
        ),
    }
    context.update(announcements_context())
    return render_template("practice_setup.html", **context)


def build_practice_questions(subject_slug, material_slug):
    bank = {
        "science:ecosystems": [
            {
                "id": 1,
                "type": "mcq",
                "type_label": "Multiple choice",
                "bloom": "Analyze",
                "prompt": "A forest loses many trees after a storm. Which change best shows how energy flow in the food chain may be affected?",
                "citation": "p. 6",
                "options": [
                    {"id": "a", "text": "Producers increase, so every consumer gets more energy."},
                    {"id": "b", "text": "Fewer producers may mean less energy available to consumers."},
                    {"id": "c", "text": "Decomposers stop working because sunlight increases."},
                    {"id": "d", "text": "Consumers become producers to balance the ecosystem."},
                ],
                "answer": "b",
                "explanation": "With fewer producers, less energy enters the food chain, so consumers may receive less energy.",
                "rubric": None,
            },
            {
                "id": 2,
                "type": "essay",
                "type_label": "Essay",
                "bloom": "Evaluate",
                "prompt": "A classmate says every food chain should be very long so more animals can get energy. Do you agree? Explain using energy flow.",
                "citation": "p. 6",
                "options": [],
                "answer": None,
                "explanation": "Strong answers disagree and explain that only part of the energy moves to each next level, so long chains leave little energy near the end.",
                "rubric": "Clear claim + evidence from energy flow + short explanation.",
            },
            {
                "id": 3,
                "type": "problem",
                "type_label": "Problem-solving",
                "bloom": "Create",
                "prompt": "Create a 3-step food chain for a school garden ecosystem and label the producer and consumers.",
                "citation": "pp. 4–5",
                "options": [],
                "answer": None,
                "explanation": "A solid response includes one producer and two consumers in a sensible order, with clear labels.",
                "rubric": "Original chain + correct roles + logical order.",
            },
        ],
        "mathematics:fractions": [
            {
                "id": 1,
                "type": "mcq",
                "type_label": "Multiple choice",
                "bloom": "Analyze",
                "prompt": "Which pair shows equivalent fractions?",
                "citation": "pp. 3–4",
                "options": [
                    {"id": "a", "text": "1/2 and 2/4"},
                    {"id": "b", "text": "1/3 and 1/4"},
                    {"id": "c", "text": "2/3 and 3/2"},
                    {"id": "d", "text": "3/4 and 4/3"},
                ],
                "answer": "a",
                "explanation": "1/2 and 2/4 name the same amount.",
                "rubric": None,
            },
            {
                "id": 2,
                "type": "problem",
                "type_label": "Problem-solving",
                "bloom": "Evaluate",
                "prompt": "Maya says 2/5 is greater than 3/5 because 2 is easier to work with. Is she correct? Explain.",
                "citation": "pp. 1–2",
                "options": [],
                "answer": None,
                "explanation": "She is not correct. With the same denominator, the larger numerator is greater, so 3/5 > 2/5.",
                "rubric": "Decision + denominator reasoning.",
            },
            {
                "id": 3,
                "type": "essay",
                "type_label": "Essay",
                "bloom": "Create",
                "prompt": "Create a real-life classroom example that uses the fraction 3/4 and explain what the numerator and denominator mean in your example.",
                "citation": "pp. 1–2",
                "options": [],
                "answer": None,
                "explanation": "Good answers invent a clear situation and correctly define numerator and denominator in context.",
                "rubric": "Original example + correct fraction parts.",
            },
        ],
        "english:poetry-analysis": [
            {
                "id": 1,
                "type": "mcq",
                "type_label": "Multiple choice",
                "bloom": "Analyze",
                "prompt": "Which strategy best helps you understand a poem’s mood?",
                "citation": "pp. 1–2",
                "options": [
                    {"id": "a", "text": "Count only the number of stanzas."},
                    {"id": "b", "text": "Notice imagery, word choice, and repeated sounds."},
                    {"id": "c", "text": "Ignore figurative language."},
                    {"id": "d", "text": "Read only the title."},
                ],
                "answer": "b",
                "explanation": "Mood is often shown through imagery, diction, and sound devices.",
                "rubric": None,
            },
            {
                "id": 2,
                "type": "essay",
                "type_label": "Essay",
                "bloom": "Evaluate",
                "prompt": "Why is quoted evidence important when you make a claim about a poem?",
                "citation": "p. 3",
                "options": [],
                "answer": None,
                "explanation": "Evidence shows your claim is based on the text, not only personal opinion.",
                "rubric": "Clear reason + connection to claim support.",
            },
            {
                "id": 3,
                "type": "problem",
                "type_label": "Problem-solving",
                "bloom": "Create",
                "prompt": "Write one claim about a poem’s message and support it with one short quoted detail plus a one-sentence explanation.",
                "citation": "p. 3",
                "options": [],
                "answer": None,
                "explanation": "Strong responses include claim + quote + explanation that links them.",
                "rubric": "Claim, evidence, explanation.",
            },
        ],
    }
    return bank.get(f"{subject_slug}:{material_slug}", bank["science:ecosystems"])


@app.route("/subjects/<subject_slug>/practice/<material_slug>/take")
def practice_take(subject_slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    subject = SUBJECT_BY_SLUG.get(subject_slug)
    summary = DEMO_SUMMARIES.get(subject_slug, {}).get(material_slug)
    if not subject or not summary:
        flash("That practice check is not available.", "danger")
        return redirect(url_for("home"))

    focus = request.args.get("focus", "mixed")
    bloom_labels = {
        "mixed": "Mixed HOTS",
        "c4": "Analyze",
        "c5": "Evaluate",
        "c6": "Create",
    }
    questions = build_practice_questions(subject_slug, material_slug)
    try:
        count = max(1, min(int(request.args.get("count", 3)), len(questions)))
    except ValueError:
        count = min(3, len(questions))
    questions = questions[:count]

    context = {
        "user": user,
        "subject": subject,
        "material_slug": material_slug,
        "material_title": summary["title"],
        "questions": questions,
        "bloom_label": bloom_labels.get(focus, "Mixed HOTS"),
    }
    context.update(announcements_context())
    return render_template("practice_take.html", **context)


@app.route("/subjects/<subject_slug>/practice/<material_slug>/submit", methods=["POST"])
def practice_submit(subject_slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    subject = SUBJECT_BY_SLUG.get(subject_slug)
    summary = DEMO_SUMMARIES.get(subject_slug, {}).get(material_slug)
    if not subject or not summary:
        flash("That practice check is not available.", "danger")
        return redirect(url_for("home"))

    questions = build_practice_questions(subject_slug, material_slug)
    shown_ids = {
        int(key[1:])
        for key in request.form
        if key.startswith("q") and key[1:].isdigit()
    }

    review_items = []
    earned = 0
    auto_total = 0

    for q in questions:
        if shown_ids and q["id"] not in shown_ids:
            continue

        raw = (request.form.get(f"q{q['id']}") or "").strip()
        if q["type"] == "mcq":
            auto_total += 1
            option_map = {opt["id"]: opt["text"] for opt in q["options"]}
            your_answer = option_map.get(raw, raw or "(No answer)")
            correct_answer = option_map.get(q["answer"])
            if raw == q["answer"]:
                earned += 1
                status, status_label = "good", "Good job"
            else:
                status, status_label = "improve", "Let’s improve"
        else:
            your_answer = raw or "(No answer)"
            correct_answer = None
            if raw:
                status, status_label = "review", "Teacher-style review"
            else:
                status, status_label = "improve", "Try again next time"

        review_items.append(
            {
                "bloom": q["bloom"],
                "prompt": q["prompt"],
                "your_answer": your_answer,
                "correct_answer": correct_answer,
                "explanation": q["explanation"],
                "rubric": q.get("rubric"),
                "citation": q["citation"],
                "status": status,
                "status_label": status_label,
            }
        )

    if auto_total:
        score_label = f"{earned}/{auto_total} automatic items"
        encouragement = (
            "Great focus on the multiple-choice items. Review the open answers to grow more."
            if earned == auto_total
            else "Good effort. Review 1–2 items below to strengthen your HOTS skills."
        )
    else:
        score_label = "Open response practice"
        encouragement = (
            "Open answers are for learning. Use the explanations and rubric notes to improve."
        )

    context = {
        "user": user,
        "subject": subject,
        "material_title": summary["title"],
        "score_label": score_label,
        "encouragement": encouragement,
        "review_items": review_items,
    }
    context.update(announcements_context())
    return render_template("practice_result.html", **context)


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
    if user["role"] != "student":
        return redirect(url_for("home"))

    context = {
        "user": user,
        "practice_ready": [
            {
                "subject": "Science",
                "title": "Ecosystems Practice Check",
                "meta": "Approved material · Mixed HOTS",
                "href": "/subjects/science/practice/ecosystems",
            },
            {
                "subject": "Mathematics",
                "title": "Fractions Practice Check",
                "meta": "New summary available",
                "href": "/subjects/mathematics/practice/fractions",
            },
            {
                "subject": "English",
                "title": "Poetry Practice Check",
                "meta": "Approved material",
                "href": "/subjects/english/practice/poetry-analysis",
            },
        ],
        "practice_locked": [
            {
                "subject": "Science",
                "title": "Lab handout practice",
                "meta": "Backup upload pending teacher approval",
            }
        ],
    }
    context.update(announcements_context())
    return render_template("practice_hub.html", **context)


@app.route("/results")
def results():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] != "student":
        return redirect(url_for("home"))

    filter_name = request.args.get("filter", "all")
    all_items = [
        {
            "kind": "Assessment",
            "subject": "English",
            "title": "Poetry analysis feedback",
            "meta": "Released · Review explanations and rubric notes",
            "action": "Review",
            "href": "/subjects/english?tab=results",
            "bucket": "assessments",
        },
        {
            "kind": "Assessment",
            "subject": "Science",
            "title": "Matter HOTS Check",
            "meta": "Submitted · Waiting for release",
            "action": "Waiting",
            "href": "/subjects/science?tab=results",
            "bucket": "assessments",
        },
        {
            "kind": "Practice",
            "subject": "Mathematics",
            "title": "Fractions Practice Check",
            "meta": "Personal practice · Supportive feedback ready",
            "action": "Open",
            "href": "/subjects/mathematics/practice/fractions",
            "bucket": "practice",
        },
    ]
    if filter_name in {"assessments", "practice"}:
        items = [item for item in all_items if item["bucket"] == filter_name]
    else:
        items = all_items
        filter_name = "all"

    context = {"user": user, "filter": filter_name, "result_items": items}
    context.update(announcements_context())
    return render_template("results.html", **context)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        record = DEMO_USERS.get(user["email"])
        if not record or not check_password_hash(record["password_hash"], current):
            flash("Current password is incorrect.", "danger")
        elif len(new) < 8:
            flash("New password must be at least 8 characters.", "danger")
        elif new != confirm:
            flash("New passwords do not match.", "danger")
        else:
            record["password_hash"] = generate_password_hash(new)
            flash("Password updated. Use your new password next time.", "success")
        return redirect(url_for("profile"))

    if user["role"] != "student":
        # Staff can still change password from a simple profile view
        topbar_sub = "Profile"
        role_nav = teacher_nav() if user["role"] == "teacher" else admin_nav()
        return render_template(
            "staff_page.html",
            user=user,
            topbar_sub=topbar_sub,
            role_nav=role_nav,
            active_nav="profile",
            title="Profile",
            subtitle="Account details and password",
            panels=[
                {
                    "kicker": "Account",
                    "title": user["name"],
                    "meta": f"{user['email']} · {user['role']}",
                    "action": None,
                    "action_href": None,
                    "soft": True,
                }
            ],
            form_blocks=[
                {
                    "title": "Change password",
                    "note": "Update your temporary password.",
                    "action": url_for("profile"),
                    "submit": "Update Password",
                    "fields": [
                        {
                            "id": "current_password",
                            "name": "current_password",
                            "label": "Current password",
                            "type": "password",
                            "placeholder": "",
                            "required": True,
                        },
                        {
                            "id": "new_password",
                            "name": "new_password",
                            "label": "New password",
                            "type": "password",
                            "placeholder": "",
                            "required": True,
                        },
                        {
                            "id": "confirm_password",
                            "name": "confirm_password",
                            "label": "Confirm new password",
                            "type": "password",
                            "placeholder": "",
                            "required": True,
                        },
                    ],
                }
            ],
        )

    context = {"user": user}
    context.update(announcements_context())
    return render_template("profile.html", **context)


@app.route("/announcements")
def announcements():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] != "student":
        return redirect(url_for("home"))

    filter_name = request.args.get("filter", "all")
    notes = DEMO_ANNOUNCEMENTS
    if filter_name != "all":
        notes = [n for n in DEMO_ANNOUNCEMENTS if n["subject"] == filter_name]
    context = {"user": user, "filter": filter_name, "announcements": notes}
    context.update(announcements_context())
    return render_template("announcements.html", **context)


def teacher_nav():
    return [
        {"label": "Home", "endpoint": "teacher_home", "key": "home"},
        {"label": "Materials", "endpoint": "teacher_materials", "key": "materials"},
        {"label": "HOTS", "endpoint": "teacher_hots", "key": "hots"},
        {"label": "Monitor", "endpoint": "teacher_monitor", "key": "monitor"},
        {"label": "Announce", "endpoint": "teacher_announce", "key": "announce"},
    ]


def admin_nav():
    return [
        {"label": "Home", "endpoint": "admin_home", "key": "home"},
        {"label": "Users", "endpoint": "admin_users", "key": "users"},
        {"label": "Section", "endpoint": "admin_section", "key": "section"},
        {"label": "Reports", "endpoint": "admin_reports", "key": "reports"},
        {"label": "Settings", "endpoint": "admin_settings", "key": "settings"},
    ]


@app.route("/teacher")
def teacher_home():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] != "teacher":
        return redirect(url_for("home"))

    subject_name = user.get("subject") or "Science"
    return render_template(
        "teacher_home.html",
        user=user,
        topbar_sub=f"Teacher · {subject_name}",
        role_nav=teacher_nav(),
        active_nav="home",
        subject_name=subject_name,
        stats=[
            {"label": "Approved materials", "value": "4", "meta": "Ready for class"},
            {"label": "Draft HOTS items", "value": "6", "meta": "Needs review"},
            {"label": "Pending uploads", "value": "1", "meta": "Student backup"},
            {"label": "Due assessments", "value": "1", "meta": "Ecosystems tomorrow"},
        ],
        attention=[
            {
                "kicker": "Review queue",
                "title": "Lab handout.pdf awaiting approval",
                "meta": "Student backup upload",
                "action": "Review",
                "href": url_for("teacher_materials"),
            },
            {
                "kicker": "HOTS draft",
                "title": "Ecosystems question set",
                "meta": "Edit, regenerate, then publish",
                "action": "Open",
                "href": url_for("teacher_hots"),
            },
        ],
    )


@app.route("/teacher/materials", methods=["GET", "POST"])
def teacher_materials():
    user = require_user()
    if not user or user["role"] != "teacher":
        return redirect(url_for("login"))
    if request.method == "POST":
        flash("Demo upload received. In production this extracts text and queues an AI summary.", "success")
        return redirect(url_for("teacher_materials"))

    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Materials",
        role_nav=teacher_nav(),
        active_nav="materials",
        title="Materials",
        subtitle="Upload Canvas files once. Approve before students practice.",
        panels=[
            {
                "kicker": "Approved",
                "title": "Ecosystems",
                "meta": "Summary ready · Visible to section",
                "action": "View",
                "action_href": url_for("teacher_hots"),
                "soft": True,
            },
            {
                "kicker": "Pending approval",
                "title": "Lab handout.pdf",
                "meta": "Student backup upload",
                "action": "Approve",
                "action_href": url_for("teacher_materials"),
                "soft": False,
            },
        ],
        form_blocks=[
            {
                "title": "Upload material",
                "note": "PDF, DOCX, PPTX, or paste text. Scanned PDFs without extractable text are rejected.",
                "action": url_for("teacher_materials"),
                "submit": "Upload & summarize",
                "fields": [
                    {
                        "id": "title",
                        "name": "title",
                        "label": "Material title",
                        "type": "text",
                        "placeholder": "Ecosystems",
                        "required": True,
                    },
                    {
                        "id": "file",
                        "name": "file",
                        "label": "File upload (demo)",
                        "type": "text",
                        "placeholder": "ecosystems.pdf",
                        "required": False,
                    },
                    {
                        "id": "notes",
                        "name": "notes",
                        "label": "Or paste text",
                        "type": "textarea",
                        "placeholder": "Paste lesson text here...",
                        "required": False,
                    },
                ],
            }
        ],
    )


@app.route("/teacher/hots", methods=["GET", "POST"])
def teacher_hots():
    user = require_user()
    if not user or user["role"] != "teacher":
        return redirect(url_for("login"))
    if request.method == "POST":
        flash("Demo HOTS set generated. Review items before publishing to the section.", "success")
        return redirect(url_for("teacher_hots"))

    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="HOTS Generator",
        role_nav=teacher_nav(),
        active_nav="hots",
        title="AI HOTS Question Generator",
        subtitle="Generate C4–C6 questions from an approved material, then edit before publish.",
        panels=[
            {
                "kicker": "Draft item · Analyze",
                "title": "How does fewer producers affect energy flow?",
                "meta": "Citation: p. 6 · Multiple choice",
                "action": "Regenerate",
                "action_href": url_for("teacher_hots"),
                "soft": True,
            },
            {
                "kicker": "Draft item · Evaluate",
                "title": "Should food chains be very long? Explain.",
                "meta": "Citation: p. 6 · Essay · Rubric attached",
                "action": "Edit",
                "action_href": url_for("teacher_hots"),
                "soft": True,
            },
        ],
        form_blocks=[
            {
                "title": "Generate from material",
                "note": "Grounded only in uploaded content. Teacher approval required before students see items.",
                "action": url_for("teacher_hots"),
                "submit": "Generate HOTS set",
                "fields": [
                    {
                        "id": "material",
                        "name": "material",
                        "label": "Material",
                        "type": "select",
                        "options": ["Ecosystems", "Cells"],
                        "required": True,
                    },
                    {
                        "id": "bloom",
                        "name": "bloom",
                        "label": "Bloom focus",
                        "type": "select",
                        "options": ["Mixed C4–C6", "Analyze", "Evaluate", "Create"],
                        "required": True,
                    },
                    {
                        "id": "count",
                        "name": "count",
                        "label": "Question count",
                        "type": "select",
                        "options": ["5", "8", "10"],
                        "required": True,
                    },
                ],
            }
        ],
    )


@app.route("/teacher/monitor")
def teacher_monitor():
    user = require_user()
    if not user or user["role"] != "teacher":
        return redirect(url_for("login"))
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Monitoring",
        role_nav=teacher_nav(),
        active_nav="monitor",
        title="Monitoring & Analytics",
        subtitle="Completion, scores, Bloom performance, and practice activity for your subject.",
        panels=[
            {
                "kicker": "Assessment",
                "title": "Ecosystems HOTS Assessment",
                "meta": "12/30 started · Avg 71% on auto items · C5 weakest",
                "action": "Details",
                "action_href": url_for("teacher_monitor"),
                "soft": True,
            },
            {
                "kicker": "Practice activity",
                "title": "Fractions / Ecosystems practice",
                "meta": "18 practice checks this week · Common miss: energy flow",
                "action": "View",
                "action_href": url_for("teacher_monitor"),
                "soft": True,
            },
            {
                "kicker": "Release controls",
                "title": "Scores / answers / feedback",
                "meta": "Can be released independently after close",
                "action": "Configure",
                "action_href": url_for("teacher_hots"),
                "soft": False,
            },
        ],
        form_blocks=[],
    )


@app.route("/teacher/announce", methods=["GET", "POST"])
def teacher_announce():
    user = require_user()
    if not user or user["role"] != "teacher":
        return redirect(url_for("login"))
    if request.method == "POST":
        flash("Announcement posted to your subject feed.", "success")
        return redirect(url_for("teacher_announce"))
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Announcements",
        role_nav=teacher_nav(),
        active_nav="announce",
        title="Subject announcements",
        subtitle="Posts appear in the shared student feed, filterable by subject.",
        panels=[
            {
                "kicker": "Science",
                "title": "Ecosystems assessment opens tomorrow",
                "meta": "Posted yesterday",
                "action": None,
                "action_href": None,
                "soft": True,
            }
        ],
        form_blocks=[
            {
                "title": "New announcement",
                "note": "Keep it short and student-friendly.",
                "action": url_for("teacher_announce"),
                "submit": "Post announcement",
                "fields": [
                    {
                        "id": "title",
                        "name": "title",
                        "label": "Title",
                        "type": "text",
                        "placeholder": "Assessment reminder",
                        "required": True,
                    },
                    {
                        "id": "body",
                        "name": "body",
                        "label": "Message",
                        "type": "textarea",
                        "placeholder": "Write your announcement...",
                        "required": True,
                    },
                ],
            }
        ],
    )


@app.route("/admin")
def admin_home():
    user = require_user()
    if not user or user["role"] != "admin":
        return redirect(url_for("login"))
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Admin",
        role_nav=admin_nav(),
        active_nav="home",
        title="Admin dashboard",
        subtitle="Pilot section oversight for Grade 7 Bloom.",
        panels=[
            {
                "kicker": "Users",
                "title": "128 imported accounts",
                "meta": "1 section · 3 subject teachers",
                "action": "Manage",
                "action_href": url_for("admin_users"),
                "soft": True,
            },
            {
                "kicker": "System",
                "title": "Usability pilot ready",
                "meta": "Research focus: usability, acceptability, perceived effectiveness",
                "action": "Reports",
                "action_href": url_for("admin_reports"),
                "soft": True,
            },
        ],
        form_blocks=[],
    )


@app.route("/admin/users", methods=["GET", "POST"])
def admin_users():
    user = require_user()
    if not user or user["role"] != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        flash("Demo bulk import accepted. Users can sign in with temporary passwords.", "success")
        return redirect(url_for("admin_users"))
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Users",
        role_nav=admin_nav(),
        active_nav="users",
        title="Users",
        subtitle="Bulk import school emails, names, roles, and temporary passwords.",
        panels=[
            {
                "kicker": "Student",
                "title": "Demo Student",
                "meta": "student@letran-calamba.edu.ph",
                "action": None,
                "action_href": None,
                "soft": True,
            },
            {
                "kicker": "Teacher · Science",
                "title": "Demo Teacher",
                "meta": "teacher@letran-calamba.edu.ph",
                "action": None,
                "action_href": None,
                "soft": True,
            },
        ],
        form_blocks=[
            {
                "title": "Bulk import",
                "note": "Paste CSV rows: email, full name, role, temporary password, subject/section",
                "action": url_for("admin_users"),
                "submit": "Import users",
                "fields": [
                    {
                        "id": "csv",
                        "name": "csv",
                        "label": "CSV data",
                        "type": "textarea",
                        "placeholder": "student1@letran-calamba.edu.ph, Ana Cruz, student, Temp1234, Grade7",
                        "required": True,
                    }
                ],
            }
        ],
    )


@app.route("/admin/section")
def admin_section():
    user = require_user()
    if not user or user["role"] != "admin":
        return redirect(url_for("login"))
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Section",
        role_nav=admin_nav(),
        active_nav="section",
        title="Section management",
        subtitle="One Grade 7 pilot section with English, Math, and Science teachers.",
        panels=[
            {
                "kicker": "Pilot section",
                "title": "Grade 7 · Section A",
                "meta": "Students can view all three subjects",
                "action": None,
                "action_href": None,
                "soft": True,
            }
        ],
        form_blocks=[],
    )


@app.route("/admin/reports")
def admin_reports():
    user = require_user()
    if not user or user["role"] != "admin":
        return redirect(url_for("login"))
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Reports",
        role_nav=admin_nav(),
        active_nav="reports",
        title="Reports & analytics",
        subtitle="Section-level completion, Bloom performance, and participation snapshots.",
        panels=[
            {
                "kicker": "Participation",
                "title": "89% students active this week",
                "meta": "Practice + assessment combined",
                "action": None,
                "action_href": None,
                "soft": True,
            },
            {
                "kicker": "Bloom focus",
                "title": "Evaluate (C5) needs support",
                "meta": "Across English and Science",
                "action": None,
                "action_href": None,
                "soft": True,
            },
        ],
        form_blocks=[],
    )


@app.route("/admin/settings")
def admin_settings():
    user = require_user()
    if not user or user["role"] != "admin":
        return redirect(url_for("login"))
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Settings",
        role_nav=admin_nav(),
        active_nav="settings",
        title="System settings",
        subtitle="Pilot defaults for uploads, English-only content, and privacy reminders.",
        panels=[
            {
                "kicker": "Uploads",
                "title": "20 MB · 100 pages · reject weak scans",
                "meta": "No OCR in research scope",
                "action": None,
                "action_href": None,
                "soft": True,
            },
            {
                "kicker": "Privacy",
                "title": "Minimize student data in AI prompts",
                "meta": "Role-based access · school email accounts",
                "action": None,
                "action_href": None,
                "soft": True,
            },
        ],
        form_blocks=[],
    )


@app.route("/assessments/<slug>/take")
def assessment_take(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    assessment = DEMO_ASSESSMENTS.get(slug)
    if not assessment:
        flash("That assessment is not available.", "danger")
        return redirect(url_for("home"))
    questions = build_practice_questions("science", "ecosystems")
    context = {
        "user": user,
        "assessment": assessment,
        "questions": questions,
    }
    context.update(announcements_context())
    return render_template("assessment_take.html", **context)


@app.route("/assessments/<slug>/submit", methods=["POST"])
def assessment_submit(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    assessment = DEMO_ASSESSMENTS.get(slug)
    if not assessment:
        flash("That assessment is not available.", "danger")
        return redirect(url_for("home"))

    # Reuse practice scoring presentation with assessment wording
    questions = build_practice_questions("science", "ecosystems")
    review_items = []
    earned = 0
    auto_total = 0
    for q in questions:
        raw = (request.form.get(f"q{q['id']}") or "").strip()
        if q["type"] == "mcq":
            auto_total += 1
            option_map = {opt["id"]: opt["text"] for opt in q["options"]}
            your_answer = option_map.get(raw, raw or "(No answer)")
            correct_answer = option_map.get(q["answer"])
            if raw == q["answer"]:
                earned += 1
                status, status_label = "good", "Good job"
            else:
                status, status_label = "improve", "Let’s improve"
        else:
            your_answer = raw or "(No answer)"
            correct_answer = None
            status, status_label = ("review", "Pending release") if raw else ("improve", "No answer")
        review_items.append(
            {
                "bloom": q["bloom"],
                "prompt": q["prompt"],
                "your_answer": your_answer,
                "correct_answer": None if status_label == "Pending release" else correct_answer,
                "explanation": "Feedback will follow your teacher’s release settings."
                if q["type"] != "mcq"
                else q["explanation"],
                "rubric": q.get("rubric"),
                "citation": q["citation"],
                "status": status,
                "status_label": status_label,
            }
        )

    context = {
        "user": user,
        "subject": {"name": assessment["subject"], "slug": "science"},
        "material_title": assessment["title"],
        "score_label": f"{earned}/{auto_total} automatic items · open items pending release",
        "encouragement": "Submitted. Your teacher controls when full answers and feedback appear.",
        "review_items": review_items,
    }
    context.update(announcements_context())
    return render_template("practice_result.html", **context)


@app.route("/logout")
def logout():
    session.clear()
    flash("You signed out of Bloom.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
