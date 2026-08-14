import csv
import io
import json
import os
import re
from datetime import datetime, timedelta
from functools import wraps

from urllib.parse import urlencode

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import inspect as sa_inspect, or_, text
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from ai import generate_hots_questions, last_ai_error, summarize_material
from extract import ExtractError, extract_text
from models import (
    Announcement,
    AnnouncementRead,
    Assessment,
    Attempt,
    ChatMessage,
    Conversation,
    Material,
    Question,
    QuizDraft,
    Setting,
    Summary,
    User,
    db,
)


def load_env():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "capstone-dev-secret-change-in-production")
os.makedirs(app.instance_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "bloom.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db.init_app(app)


@app.context_processor
def inject_unread_messages():
    user = current_user()
    if not user:
        return {"unread_messages": 0}
    return {"unread_messages": unread_message_count(user["id"])}


@app.context_processor
def inject_difficulty_helpers():
    return {"difficulty_label": difficulty_label}


SUBJECTS = {
    "english": {"slug": "english", "name": "English", "announce": "English"},
    "mathematics": {"slug": "mathematics", "name": "Mathematics", "announce": "Math"},
    "science": {"slug": "science", "name": "Science", "announce": "Science"},
}

DIFFICULTIES = {
    "easy": {
        "key": "easy",
        "label": "Easy",
        "hint": "Build your understanding with more approachable questions.",
    },
    "medium": {
        "key": "medium",
        "label": "Medium",
        "hint": "Practice with a balanced level of challenge.",
    },
    "hard": {
        "key": "hard",
        "label": "Hard",
        "hint": "Challenge yourself with more complex problems.",
    },
}


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return value or "item"


def normalize_difficulty(value: str | None) -> str:
    key = (value or "").strip().lower()
    return key if key in DIFFICULTIES else "medium"


def difficulty_label(value: str | None) -> str:
    return DIFFICULTIES[normalize_difficulty(value)]["label"]


def practice_setup_url(subject_slug, material_slug, difficulty="medium", focus="mixed", count=3, types=None):
    base = url_for("practice_setup", subject_slug=subject_slug, material_slug=material_slug)
    pairs = [
        ("difficulty", normalize_difficulty(difficulty)),
        ("focus", focus or "mixed"),
        ("count", str(count or 3)),
    ]
    for item in types or []:
        pairs.append(("types", item))
    return f"{base}?{urlencode(pairs)}"


def ensure_schema():
    inspector = sa_inspect(db.engine)
    tables = set(inspector.get_table_names())
    additions = (
        ("quiz_draft", "difficulty", "VARCHAR(20) DEFAULT 'medium'"),
        ("attempt", "difficulty", "VARCHAR(20)"),
        ("assessment", "difficulty", "VARCHAR(20)"),
    )
    with db.engine.begin() as conn:
        for table, column, ddl in additions:
            if table not in tables:
                continue
            columns = {col["name"] for col in inspector.get_columns(table)}
            if column not in columns:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


def unique_slug(base: str, model, field="slug") -> str:
    slug = slugify(base)
    candidate = slug
    index = 2
    while model.query.filter_by(**{field: candidate}).first():
        candidate = f"{slug}-{index}"
        index += 1
    return candidate


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return None
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "subject": user.subject,
        "section": user.section,
    }


def require_user():
    user = current_user()
    if not user:
        flash("Please sign in to continue.", "danger")
        return None
    return user


def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = require_user()
            if not user:
                return redirect(url_for("login"))
            if user["role"] not in roles:
                flash("You do not have access to that page.", "danger")
                return redirect(url_for("home"))
            return fn(user, *args, **kwargs)

        return wrapper

    return decorator


def teacher_subject_slug(user) -> str:
    name = user.get("subject") or "Science"
    for slug, meta in SUBJECTS.items():
        if meta["name"] == name:
            return slug
    return "science"


def teacher_nav():
    return [
        {"label": "Home", "endpoint": "teacher_home", "key": "home"},
        {"label": "Messages", "endpoint": "messages_inbox", "key": "messages"},
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


def announcement_read_ids(user_id: int) -> set[int]:
    return {
        row.announcement_id
        for row in AnnouncementRead.query.filter_by(user_id=user_id).all()
    }


def unread_announcement_count(user_id: int) -> int:
    read_ids = announcement_read_ids(user_id)
    query = Announcement.query
    if read_ids:
        query = query.filter(~Announcement.id.in_(read_ids))
    return query.count()


def mark_announcement_read(user_id: int, announcement_id: int) -> bool:
    announcement = db.session.get(Announcement, announcement_id)
    if not announcement:
        return False
    existing = AnnouncementRead.query.filter_by(
        user_id=user_id, announcement_id=announcement_id
    ).first()
    if existing:
        return True
    try:
        db.session.add(AnnouncementRead(user_id=user_id, announcement_id=announcement_id))
        db.session.commit()
    except Exception:
        db.session.rollback()
        if AnnouncementRead.query.filter_by(user_id=user_id, announcement_id=announcement_id).first():
            return True
        return False
    return True


def announcement_href(announcement_id, filter_name="all", arrive=False):
    kwargs = {}
    if filter_name and filter_name != "all":
        kwargs["filter"] = filter_name
    if arrive:
        kwargs["arrive"] = 1
    return url_for("announcements", announcement_id=announcement_id, **kwargs)


def serialize_announcement(note, read_ids, selected_id=None, filter_name="all"):
    body = (note.body or "").strip()
    preview = " ".join(body.split())
    if len(preview) > 110:
        cut = preview[:107]
        preview = (cut.rsplit(" ", 1)[0] if " " in cut else cut) + "…"
    if not preview:
        preview = "Open to read this announcement."
    teacher_name = note.teacher.name if note.teacher else "Your teacher"
    return {
        "id": note.id,
        "subject": note.subject,
        "title": note.title,
        "body": body,
        "preview": preview,
        "teacher": teacher_name,
        "initials": initials(teacher_name),
        "when": relative_time(note.created_at),
        "posted": note.created_at.strftime("%B %d, %Y · %I:%M %p") if note.created_at else "",
        "unread": note.id not in read_ids,
        "selected": selected_id == note.id,
        "href": announcement_href(note.id, filter_name),
    }


def note_matches_filter(note, filter_name, read_ids):
    if filter_name == "unread":
        return note.id not in read_ids
    if filter_name in {"English", "Math", "Science"}:
        return note.subject == filter_name
    return True


def announcements_context(user=None):
    if not user:
        return {"announcements_preview": [], "unread_announcements": 0, "unread_messages": 0}
    read_ids = announcement_read_ids(user["id"])
    notes = Announcement.query.order_by(Announcement.created_at.desc()).limit(4).all()
    preview = []
    for note in notes:
        preview.append(
            {
                "id": note.id,
                "subject": note.subject,
                "title": note.title,
                "meta": note.created_at.strftime("%b %d") + (f" · {note.teacher.name}" if note.teacher else ""),
                "unread": note.id not in read_ids,
                "href": announcement_href(note.id, arrive=True),
            }
        )
    return {
        "announcements_preview": preview,
        "unread_announcements": unread_announcement_count(user["id"]),
        "unread_messages": unread_message_count(user["id"]),
    }


def initials(name: str) -> str:
    parts = [part for part in (name or "B").split(" ") if part]
    if not parts:
        return "B"
    if len(parts) == 1:
        return parts[0][:1].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()


def relative_time(when) -> str:
    if not when:
        return ""
    seconds = max(0, int((datetime.utcnow() - when).total_seconds()))
    if seconds < 45:
        return "Just now"
    if seconds < 3600:
        mins = max(1, seconds // 60)
        return f"{mins} min ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h ago"
    if seconds < 172800:
        return "Yesterday"
    return when.strftime("%b %d")


def unread_message_count(user_id: int) -> int:
    return (
        ChatMessage.query.join(Conversation)
        .filter(ChatMessage.sender_id != user_id)
        .filter(ChatMessage.read_at.is_(None))
        .filter(or_(Conversation.student_id == user_id, Conversation.teacher_id == user_id))
        .count()
    )


def can_access_conversation(user, conversation: Conversation) -> bool:
    if not conversation:
        return False
    if user["role"] == "student":
        return conversation.student_id == user["id"]
    if user["role"] == "teacher":
        return conversation.teacher_id == user["id"]
    return False


def get_or_create_conversation(student_id: int, teacher_id: int) -> Conversation:
    conversation = Conversation.query.filter_by(student_id=student_id, teacher_id=teacher_id).first()
    if conversation:
        return conversation
    conversation = Conversation(student_id=student_id, teacher_id=teacher_id)
    db.session.add(conversation)
    db.session.commit()
    return conversation


def mark_conversation_read(conversation: Conversation, user_id: int):
    unread = [
        message
        for message in conversation.messages
        if message.sender_id != user_id and message.read_at is None
    ]
    if not unread:
        return
    now = datetime.utcnow()
    for message in unread:
        message.read_at = now
    db.session.commit()


def serialize_message(message: ChatMessage, user_id: int) -> dict:
    mine = message.sender_id == user_id
    status = "sent"
    if mine and message.read_at:
        status = "read"
    return {
        "id": message.id,
        "body": message.body,
        "mine": mine,
        "status": status,
        "created_label": relative_time(message.created_at),
        "created_at": message.created_at.strftime("%b %d · %I:%M %p") if message.created_at else "",
    }


def conversation_preview(conversation: Conversation, user_id: int) -> dict:
    other = conversation.teacher if conversation.student_id == user_id else conversation.student
    last = conversation.messages[-1] if conversation.messages else None
    unread = sum(1 for message in conversation.messages if message.sender_id != user_id and message.read_at is None)
    return {
        "id": conversation.id,
        "other_id": other.id if other else 0,
        "name": other.name if other else "Unknown",
        "meta": (other.subject or other.role.title()) if other else "",
        "initials": initials(other.name if other else "B"),
        "preview": (last.body[:90] if last else "No messages yet"),
        "when": relative_time(last.created_at if last else conversation.updated_at),
        "unread": unread,
        "href": url_for("messages_thread", user_id=other.id) if other else url_for("messages_inbox"),
    }


def same_section(user, other) -> bool:
    left = (user.get("section") if isinstance(user, dict) else getattr(user, "section", None)) or ""
    right = (other.get("section") if isinstance(other, dict) else getattr(other, "section", None)) or ""
    if not left or not right:
        return True
    return left == right


def allowed_chat_partner(user, other) -> bool:
    if not other:
        return False
    if not same_section(user, other):
        return False
    if user["role"] == "student":
        return other.role == "teacher"
    if user["role"] == "teacher":
        return other.role == "student"
    return False


def find_conversation(user, other):
    if user["role"] == "student":
        return Conversation.query.filter_by(student_id=user["id"], teacher_id=other.id).first()
    return Conversation.query.filter_by(student_id=other.id, teacher_id=user["id"]).first()


def ask_teacher_context(user, subject_name: str, topic: str):
    if not user or user["role"] != "student" or not subject_name:
        return None
    teachers = User.query.filter_by(role="teacher", subject=subject_name).order_by(User.name).all()
    teacher = next((item for item in teachers if same_section(user, item)), None) or (teachers[0] if teachers else None)
    if not teacher:
        return None
    draft = f"Hi, I have a question about {topic}."
    return {
        "name": teacher.name,
        "href": url_for("messages_thread", user_id=teacher.id, draft=draft),
    }


def session_user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "subject": user.subject,
        "section": user.section,
    }


def bloom_progress(user_id: int, subject_slug: str) -> tuple[int, str, bool]:
    attempts = Attempt.query.filter_by(user_id=user_id, subject_slug=subject_slug).all()
    if not attempts:
        return 0, "Start with a summary or Practice Check", False
    percents = []
    blooms = {"Analyze": 0, "Evaluate": 0, "Create": 0}
    for attempt in attempts:
        if attempt.score_total_auto:
            percents.append(int(100 * attempt.score_auto / attempt.score_total_auto))
        for item in attempt.review_items():
            bloom = item.get("bloom")
            if bloom in blooms and item.get("status") == "good":
                blooms[bloom] += 1
    percent = int(sum(percents) / len(percents)) if percents else 0
    if not percents:
        return 0, "Keep practicing HOTS items from approved lessons", False
    strongest = max(blooms, key=blooms.get)
    if max(blooms.values()) == 0:
        next_line = "Keep practicing HOTS items from approved lessons"
    else:
        next_line = f"Getting stronger in {strongest}"
    return percent, next_line, True


def build_today(user_id: int) -> list[dict]:
    items = []
    now = datetime.utcnow()
    for assessment in Assessment.query.filter_by(status="published").all():
        if assessment.deadline and assessment.deadline < now:
            continue
        taken = Attempt.query.filter_by(
            user_id=user_id, assessment_id=assessment.id, kind="assessment"
        ).count()
        limit = assessment.attempt_limit if assessment.attempt_limit is not None else 1
        allowed = limit + (1 if assessment.extra_attempt else 0)
        if taken >= allowed:
            continue
        due = "Due soon"
        if assessment.deadline:
            if assessment.deadline.date() == (now + timedelta(days=1)).date():
                due = "Due tomorrow — start now"
            elif assessment.deadline.date() == now.date():
                due = "Due today — start now"
        attempt_label = "1 attempt" if allowed == 1 else f"{allowed} attempts"
        items.append(
            {
                "type": "assessment",
                "priority": "primary",
                "kicker": f"{due} · {SUBJECTS[assessment.subject_slug]['name']}",
                "title": assessment.title,
                "meta": f"{attempt_label} · Assistive check · Posted by your teacher",
                "action": "Start now",
                "href": url_for("assessment_lobby", slug=assessment.slug),
            }
        )
    latest = (
        Attempt.query.filter_by(user_id=user_id, kind="assessment")
        .order_by(Attempt.submitted_at.desc())
        .first()
    )
    if latest:
        items.append(
            {
                "type": "result",
                "priority": "secondary",
                "kicker": f"Result · {SUBJECTS.get(latest.subject_slug, {}).get('name', '')}",
                "title": latest.title,
                "meta": "Review answers and explanations when you feel ready",
                "action": "Review",
                "href": url_for("attempt_review", attempt_id=latest.id),
            }
        )
    approved = Material.query.filter_by(status="approved").order_by(Material.created_at.desc()).first()
    if approved:
        items.append(
            {
                "type": "practice",
                "priority": "secondary",
                "kicker": f"Practice reminder · {SUBJECTS[approved.subject_slug]['name']}",
                "title": f"Try a {approved.title} Practice Check",
                "meta": "Short practice from your approved lesson",
                "action": "Practice",
                "href": url_for("practice_setup", subject_slug=approved.subject_slug, material_slug=approved.slug),
            }
        )
    pending = Material.query.filter_by(owner_id=user_id, source="student", status="pending").first()
    if pending:
        items.append(
            {
                "type": "upload",
                "priority": "secondary",
                "kicker": f"Backup upload · {SUBJECTS[pending.subject_slug]['name']}",
                "title": f"{pending.title} is waiting for approval",
                "meta": "Your teacher will review before practice unlocks",
                "action": "View",
                "href": url_for("subject_hub", slug=pending.subject_slug, tab="study"),
            }
        )
    return items[:5]


def score_answers(questions: list[dict], form) -> tuple[list[dict], int, int, str]:
    review_items = []
    earned = 0
    auto_total = 0
    for q in questions:
        raw = (form.get(f"q{q['id']}") or "").strip()
        if q["type"] == "mcq":
            auto_total += 1
            option_map = {opt["id"]: opt["text"] for opt in q.get("options") or []}
            your_answer = option_map.get(raw, raw or "(No answer)")
            correct_answer = option_map.get(q.get("answer"))
            if raw == q.get("answer"):
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
                "bloom": q.get("bloom"),
                "prompt": q.get("prompt"),
                "your_answer": your_answer,
                "correct_answer": correct_answer,
                "explanation": q.get("explanation"),
                "rubric": q.get("rubric"),
                "citation": q.get("citation"),
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
        encouragement = "Open answers are for learning. Use the explanations and rubric notes to improve."
    return review_items, earned, auto_total, encouragement if auto_total else encouragement


def save_file(file_storage) -> tuple[str, bytes]:
    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ExtractError("Please choose a file to upload.")
    data = file_storage.read()
    if len(data) > 20 * 1024 * 1024:
        raise ExtractError("Files are limited to 20 MB.")
    return filename, data


def create_material(title, subject_slug, owner_id, source, filename, data) -> Material:
    text = extract_text(filename, data)
    stored = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], stored)
    with open(path, "wb") as handle:
        handle.write(data)
    material = Material(
        slug=unique_slug(title or filename, Material),
        title=(title or "").strip() or path_stem(filename),
        subject_slug=subject_slug,
        owner_id=owner_id,
        source=source,
        status="approved" if source == "teacher" else "pending",
        filename=stored,
        extracted_text=text,
    )
    db.session.add(material)
    db.session.flush()
    if source == "teacher":
        attach_summary(material)
        material.status = "approved"
    db.session.commit()
    return material


def path_stem(filename: str) -> str:
    return os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()


def attempt_meta(attempt: Attempt) -> str:
    date_label = attempt.submitted_at.strftime("%b %d") if attempt.submitted_at else "Recent"
    if (
        attempt.kind == "assessment"
        and attempt.assessment
        and not attempt.assessment.release_scores
    ):
        return f"{date_label} · Score pending release"
    if attempt.score_total_auto:
        return f"{date_label} · {attempt.score_auto}/{attempt.score_total_auto} correct"
    return f"{date_label} · Not auto-scored"


def attach_summary(material: Material):
    payload = summarize_material(material.title, material.extracted_text, SUBJECTS[material.subject_slug]["name"])
    summary = material.summary or Summary(material_id=material.id)
    summary.intro = payload["intro"]
    summary.sections_json = json.dumps(payload["sections"])
    db.session.add(summary)


def seed():
    users = [
        ("student@letran-calamba.edu.ph", "Demo Student", "student", None, "student123"),
        ("teacher@letran-calamba.edu.ph", "Demo Science Teacher", "teacher", "Science", "teacher123"),
        ("english.teacher@letran-calamba.edu.ph", "Demo English Teacher", "teacher", "English", "teacher123"),
        ("math.teacher@letran-calamba.edu.ph", "Demo Math Teacher", "teacher", "Mathematics", "teacher123"),
        ("admin@letran-calamba.edu.ph", "Demo Admin", "admin", None, "admin123"),
    ]
    for email, name, role, subject, password in users:
        if User.query.filter_by(email=email).first():
            continue
        db.session.add(
            User(
                email=email,
                name=name,
                role=role,
                subject=subject,
                password_hash=generate_password_hash(password),
            )
        )
    if not db.session.get(Setting, "english_only"):
        db.session.add(Setting(key="english_only", value="yes"))
    if not db.session.get(Setting, "max_upload_mb"):
        db.session.add(Setting(key="max_upload_mb", value="20"))
    db.session.commit()
    seed_demo_content()


def seed_demo_content():
    if Material.query.first():
        return
    teacher = User.query.filter_by(role="teacher", subject="Science").first()
    if not teacher:
        return
    text = (
        "Ecosystems are communities of living things interacting with their environment. "
        "Producers such as plants make food through photosynthesis. Consumers eat plants or other animals. "
        "Decomposers break down dead matter and return nutrients to the soil. Energy flows from the sun to "
        "producers and then to consumers. A food chain shows one path of energy, while a food web shows many "
        "connected chains. If one part of an ecosystem is damaged, other parts can also be affected. Students "
        "should use evidence from this lesson when they explain how living things depend on one another."
    )
    material = Material(
        slug="ecosystems",
        title="Ecosystems",
        subject_slug="science",
        owner_id=teacher.id,
        source="teacher",
        status="approved",
        filename="ecosystems.txt",
        extracted_text=text,
    )
    db.session.add(material)
    db.session.flush()
    attach_summary(material)
    if not Announcement.query.first():
        db.session.add(
            Announcement(
                subject="Science",
                title="Welcome to Bloom",
                body="Read the Ecosystems summary, then try a Practice Check when you are ready.",
                teacher_id=teacher.id,
            )
        )
    db.session.commit()


with app.app_context():
    db.create_all()
    ensure_schema()
    seed()


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
        user = User.query.filter_by(email=email).first()
        if user and password and check_password_hash(user.password_hash, password):
            session.clear()
            session["user_id"] = user.id
            flash("Welcome to Bloom. For security, change your temporary password in Profile later.", "success")
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
    subjects = []
    for slug, meta in SUBJECTS.items():
        percent, insight, has_progress = bloom_progress(user["id"], slug)
        teacher = User.query.filter_by(role="teacher", subject=meta["name"]).first()
        next_action = "Next: Explore approved lessons"
        published = Assessment.query.filter_by(subject_slug=slug, status="published").all()
        open_hots = False
        for assessment in published:
            taken = Attempt.query.filter_by(
                user_id=user["id"], assessment_id=assessment.id, kind="assessment"
            ).count()
            limit = assessment.attempt_limit if assessment.attempt_limit is not None else 1
            allowed = limit + (1 if assessment.extra_attempt else 0)
            if taken < allowed:
                open_hots = True
                break
        if open_hots:
            next_action = "Next: Open a HOTS Assessment"
        elif published:
            next_action = "Next: Review your last result"
        elif Material.query.filter_by(subject_slug=slug, status="approved").first():
            next_action = "Next: Read a summary or start practice"
        subjects.append(
            {
                "slug": slug,
                "name": meta["name"],
                "teacher": teacher.name if teacher else "Subject teacher",
                "progress_label": (
                    "Not started"
                    if percent <= 0
                    else "Completed"
                    if percent >= 100
                    else f"{percent}% complete"
                )
                + (f" · {insight}" if percent > 0 else ""),
                "progress_insight": insight,
                "progress_percent": percent,
                "has_progress": has_progress,
                "next_action": next_action,
            }
        )
    today = build_today(user["id"])
    overall = 0
    tracked = [item for item in subjects if item["has_progress"]]
    if tracked:
        overall = int(round(sum(item["progress_percent"] for item in tracked) / len(tracked)))
    context = {
        "user": user,
        "greeting": f"Hi, {first_name}",
        "topbar_sub": f"Hi, {first_name}",
        "guide_note": "Your next steps are listed in Today. Progress below reflects English, Math, and Science.",
        "weekly_goal": {
            "percent": overall,
            "has_progress": bool(tracked),
            "hint": (
                "Start a summary or Practice Check to begin tracking progress."
                if overall <= 0
                else "Based on your English, Math, and Science work."
            ),
        },
        "today_items": today,
        "subjects": subjects,
    }
    context.update(announcements_context(user))
    return render_template("student_home.html", **context)


@app.route("/subjects/<slug>", methods=["GET", "POST"])
def subject_hub(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    meta = SUBJECTS.get(slug)
    if not meta:
        flash("That subject is not available.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST" and user["role"] == "student":
        return student_backup_upload(user, slug)

    tab = request.args.get("tab", "assessments")
    if tab not in {"assessments", "study", "practice", "results"}:
        tab = "assessments"

    teacher = User.query.filter_by(role="teacher", subject=meta["name"]).first()
    percent, insight, has_progress = bloom_progress(user["id"], slug)
    subject = {
        "slug": slug,
        "name": meta["name"],
        "teacher": teacher.name if teacher else "Subject teacher",
        "progress_label": (
            "Not started"
            if percent <= 0
            else "Completed"
            if percent >= 100
            else f"{percent}% complete"
        )
        + (f" · {insight}" if percent > 0 else ""),
        "progress_percent": percent,
        "next_action": insight,
    }

    now = datetime.utcnow()
    due, open_items, closed = [], [], []
    for assessment in Assessment.query.filter_by(subject_slug=slug).filter(Assessment.status != "draft"):
        taken = Attempt.query.filter_by(user_id=user["id"], assessment_id=assessment.id, kind="assessment").count()
        allowed = assessment.attempt_limit + (1 if assessment.extra_attempt else 0)
        href = url_for("assessment_lobby", slug=assessment.slug)
        entry = {
            "title": assessment.title,
            "status_label": assessment.status.title(),
            "meta": assessment.deadline.strftime("Due %b %d · %I:%M %p") if assessment.deadline else "Open assessment",
            "action": "Start now" if taken < allowed else "View",
            "href": href if taken < allowed else url_for("results", filter="assessments"),
            "primary": taken < allowed and assessment.status == "published",
        }
        if assessment.status == "closed" or (assessment.deadline and assessment.deadline < now and taken >= allowed):
            closed.append(entry)
        elif taken >= allowed:
            closed.append({**entry, "status_label": "Submitted"})
        elif assessment.deadline and assessment.deadline <= now + timedelta(days=1):
            due.append({**entry, "status_label": "Due soon — start now"})
        else:
            open_items.append(entry)

    approved = Material.query.filter_by(subject_slug=slug, status="approved").order_by(Material.created_at.desc()).all()
    materials = []
    practice_items = []
    for material in approved:
        materials.append(
            {
                "kicker": "Approved material",
                "title": material.title,
                "meta": "Summary ready · Citations included" if material.summary else "Approved for study",
                "summary_href": url_for("summary_reader", slug=slug, material_slug=material.slug),
                "practice_href": url_for("practice_setup", subject_slug=slug, material_slug=material.slug),
            }
        )
        practice_items.append(
            {
                "kicker": "Ready",
                "title": f"{material.title} Practice Check",
                "meta": "From approved lesson · Personal practice",
                "action": "Start",
                "href": url_for("practice_setup", subject_slug=slug, material_slug=material.slug),
                "locked": False,
            }
        )
    pending_uploads = [
        f"{item.title}"
        for item in Material.query.filter_by(subject_slug=slug, source="student", status="pending", owner_id=user["id"])
    ]
    for item in Material.query.filter_by(subject_slug=slug, source="student", status="pending"):
        if item.owner_id == user["id"]:
            practice_items.append(
                {
                    "kicker": "Waiting for approval",
                    "title": f"{item.title} practice",
                    "meta": "Backup upload pending teacher review",
                    "action": "Locked",
                    "href": "#",
                    "locked": True,
                }
            )

    result_items = []
    for attempt in Attempt.query.filter_by(user_id=user["id"], subject_slug=slug).order_by(Attempt.submitted_at.desc()):
        result_items.append(
            {
                "kicker": attempt.kind.title(),
                "title": attempt.title,
                "meta": attempt_meta(attempt),
                "action": "Review",
                "href": url_for("attempt_review", attempt_id=attempt.id),
            }
        )

    context = {
        "user": user,
        "subject": subject,
        "tab": tab,
        "assessment_groups": [
            {"label": "Due", "entries": due},
            {"label": "Open", "entries": open_items},
            {"label": "Closed", "entries": closed},
        ],
        "materials": materials,
        "pending_uploads": pending_uploads,
        "practice_items": practice_items,
        "result_items": result_items,
        "ask_teacher": ask_teacher_context(user, meta["name"], meta["name"]),
    }
    context.update(announcements_context(user))
    return render_template("subject_hub.html", **context)


def student_backup_upload(user, slug):
    title = request.form.get("title", "").strip()
    file = request.files.get("file")
    try:
        if not file:
            raise ExtractError("Please choose a Canvas file to upload.")
        filename, data = save_file(file)
        create_material(title or path_stem(filename), slug, user["id"], "student", filename, data)
        flash("Backup uploaded. Practice unlocks after your teacher approves it.", "success")
    except ExtractError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("subject_hub", slug=slug, tab="study"))


@app.route("/subjects/<slug>/summaries/<material_slug>")
def summary_reader(slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    meta = SUBJECTS.get(slug)
    material = Material.query.filter_by(slug=material_slug, subject_slug=slug).first()
    if not meta or not material or material.status != "approved" or not material.summary:
        flash("That summary is not available.", "danger")
        return redirect(url_for("home"))
    teacher = User.query.filter_by(role="teacher", subject=meta["name"]).first()
    context = {
        "user": user,
        "subject": {"slug": slug, "name": meta["name"], "teacher": teacher.name if teacher else ""},
        "summary": {
            "slug": material.slug,
            "title": material.title,
            "intro": material.summary.intro,
            "sections": material.summary.sections(),
        },
        "ask_teacher": ask_teacher_context(user, meta["name"], material.title),
    }
    context.update(announcements_context(user))
    return render_template("summary_reader.html", **context)


@app.route("/subjects/<subject_slug>/practice/<material_slug>")
def practice_setup(subject_slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    meta = SUBJECTS.get(subject_slug)
    material = Material.query.filter_by(slug=material_slug, subject_slug=subject_slug, status="approved").first()
    if not meta or not material:
        flash("That practice setup is not available.", "danger")
        return redirect(url_for("home"))
    selected_focus = request.args.get("focus", "mixed")
    if selected_focus not in {"mixed", "c4", "c5", "c6"}:
        selected_focus = "mixed"
    try:
        selected_count = max(1, min(int(request.args.get("count", 3)), 5))
    except ValueError:
        selected_count = 3
    selected_types = request.args.getlist("types") or ["mcq", "essay", "problem"]
    selected_difficulty = normalize_difficulty(
        request.args.get("difficulty") or session.get("practice_difficulty")
    )
    session["practice_difficulty"] = selected_difficulty
    context = {
        "user": user,
        "subject": {"slug": subject_slug, "name": meta["name"]},
        "material_slug": material.slug,
        "material_title": material.title,
        "difficulties": list(DIFFICULTIES.values()),
        "selected_difficulty": selected_difficulty,
        "selected_focus": selected_focus,
        "selected_count": selected_count,
        "selected_types": selected_types,
        "back_href": url_for("summary_reader", slug=subject_slug, material_slug=material.slug)
        if material.summary
        else url_for("subject_hub", slug=subject_slug, tab="study"),
    }
    context.update(announcements_context(user))
    return render_template("practice_setup.html", **context)


@app.route("/subjects/<subject_slug>/practice/<material_slug>/take")
def practice_take(subject_slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    meta = SUBJECTS.get(subject_slug)
    material = Material.query.filter_by(slug=material_slug, subject_slug=subject_slug, status="approved").first()
    if not meta or not material:
        flash("That practice check is not available.", "danger")
        return redirect(url_for("home"))

    focus = request.args.get("focus", "mixed")
    types = request.args.getlist("types") or ["mcq", "essay", "problem"]
    try:
        count = max(1, min(int(request.args.get("count", 3)), 5))
    except ValueError:
        count = 3
    difficulty = normalize_difficulty(request.args.get("difficulty") or session.get("practice_difficulty"))
    session["practice_difficulty"] = difficulty
    questions = generate_hots_questions(
        material.title, material.extracted_text, meta["name"], focus, count, types, difficulty
    )
    if not questions:
        flash(
            "We couldn't generate your practice right now. "
            f"Your selected difficulty: {difficulty_label(difficulty)}.",
            "danger",
        )
        return redirect(
            practice_setup_url(subject_slug, material_slug, difficulty, focus, count, types)
        )
    if last_ai_error():
        flash(
            "AI generation failed, so Bloom used basic fallback questions. "
            f"Check the terminal for details. ({last_ai_error()[:180]})",
            "danger",
        )
    bloom_label = {"mixed": "Mixed HOTS", "c4": "Analyze", "c5": "Evaluate", "c6": "Create"}.get(focus, "Mixed HOTS")
    QuizDraft.query.filter_by(user_id=user["id"], kind="practice").delete()
    draft = QuizDraft(
        user_id=user["id"],
        kind="practice",
        subject_slug=subject_slug,
        material_slug=material_slug,
        title=material.title,
        bloom_label=bloom_label,
        difficulty=difficulty,
        questions_json=json.dumps(questions),
    )
    db.session.add(draft)
    db.session.commit()
    session["practice_draft_id"] = draft.id
    context = {
        "user": user,
        "subject": {"slug": subject_slug, "name": meta["name"]},
        "material_slug": material_slug,
        "material_title": material.title,
        "questions": questions,
        "bloom_label": bloom_label,
        "difficulty_key": difficulty,
        "difficulty_name": difficulty_label(difficulty),
    }
    context.update(announcements_context(user))
    return render_template("practice_take.html", **context)


@app.route("/subjects/<subject_slug>/practice/<material_slug>/submit", methods=["POST"])
def practice_submit(subject_slug, material_slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    draft = db.session.get(QuizDraft, session.get("practice_draft_id"))
    if not draft or draft.user_id != user["id"] or draft.material_slug != material_slug:
        flash("Please generate a Practice Check first.", "danger")
        return redirect(url_for("practice_setup", subject_slug=subject_slug, material_slug=material_slug))
    questions = draft.questions()
    review_items, earned, auto_total, encouragement = score_answers(questions, request.form)
    attempt = Attempt(
        user_id=user["id"],
        kind="practice",
        subject_slug=subject_slug,
        title=f"{draft.title} Practice Check",
        score_auto=earned,
        score_total_auto=auto_total,
        review_json=json.dumps(review_items),
        encouragement=encouragement,
        difficulty=draft.difficulty,
    )
    db.session.add(attempt)
    db.session.delete(draft)
    db.session.commit()
    session.pop("practice_draft_id", None)
    return redirect(url_for("attempt_review", attempt_id=attempt.id))


@app.route("/results/<int:attempt_id>")
def attempt_review(attempt_id):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    attempt = db.session.get(Attempt, attempt_id)
    if not attempt:
        flash("That result is not available.", "danger")
        return redirect(url_for("results"))
    if attempt.user_id != user["id"] and user["role"] == "student":
        flash("You can only view your own results.", "danger")
        return redirect(url_for("results"))
    meta = SUBJECTS.get(attempt.subject_slug, {"name": "Subject", "slug": attempt.subject_slug})
    review_items = attempt.review_items()
    score_label = (
        f"{attempt.score_auto}/{attempt.score_total_auto} automatic items"
        if attempt.score_total_auto
        else "Open response practice"
    )
    encouragement = attempt.encouragement
    if attempt.kind == "assessment" and attempt.assessment and user["role"] == "student":
        assessment = attempt.assessment
        if not assessment.release_scores:
            score_label = "Score pending release"
            encouragement = "Submitted. Your teacher controls when scores and feedback appear."
        for item in review_items:
            if not assessment.release_answers:
                item["correct_answer"] = None
            if not assessment.release_feedback:
                item["explanation"] = "Feedback will follow your teacher’s release settings."
                item["rubric"] = None
            if not assessment.release_scores:
                item["status_label"] = "Submitted"
                item["status"] = "review"
    context = {
        "user": user,
        "subject": {"name": meta["name"], "slug": attempt.subject_slug},
        "material_title": attempt.title,
        "score_label": score_label,
        "encouragement": encouragement,
        "review_items": review_items,
        "ask_teacher": ask_teacher_context(user, meta["name"], attempt.title),
        "difficulty_name": difficulty_label(attempt.difficulty) if attempt.difficulty else None,
        "kind": attempt.kind,
    }
    context.update(announcements_context(user))
    return render_template("practice_result.html", **context)


@app.route("/assessments/<slug>")
def assessment_lobby(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    assessment = Assessment.query.filter_by(slug=slug).first()
    if not assessment or assessment.status == "draft":
        flash("That assessment is not available.", "danger")
        return redirect(url_for("home"))
    taken = Attempt.query.filter_by(user_id=user["id"], assessment_id=assessment.id, kind="assessment").count()
    allowed = assessment.attempt_limit + (1 if assessment.extra_attempt else 0)
    context = {
        "user": user,
        "assessment": {
            "slug": assessment.slug,
            "subject_slug": assessment.subject_slug,
            "subject": SUBJECTS[assessment.subject_slug]["name"],
            "title": assessment.title,
            "deadline_label": assessment.deadline.strftime("Due %b %d · %I:%M %p") if assessment.deadline else "Open until your teacher closes it",
            "difficulty_name": difficulty_label(assessment.difficulty) if assessment.difficulty else None,
        },
        "can_start": taken < allowed and assessment.status == "published",
        "taken": taken,
        "allowed": allowed,
        "ask_teacher": ask_teacher_context(
            user, SUBJECTS[assessment.subject_slug]["name"], assessment.title
        ),
    }
    context.update(announcements_context(user))
    return render_template("assessment_lobby.html", **context)


@app.route("/assessments/<slug>/take")
def assessment_take(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    assessment = Assessment.query.filter_by(slug=slug).first()
    if not assessment or assessment.status != "published":
        flash("That assessment is not available.", "danger")
        return redirect(url_for("home"))
    taken = Attempt.query.filter_by(user_id=user["id"], assessment_id=assessment.id, kind="assessment").count()
    allowed = assessment.attempt_limit + (1 if assessment.extra_attempt else 0)
    if taken >= allowed:
        flash("You have used your available attempts.", "danger")
        return redirect(url_for("assessment_lobby", slug=slug))
    questions = [q.as_dict() for q in assessment.questions]
    if not questions:
        flash("This assessment has no questions yet.", "danger")
        return redirect(url_for("assessment_lobby", slug=slug))
    session["assessment_started"] = slug
    context = {
        "user": user,
        "assessment": {
            "slug": assessment.slug,
            "subject": SUBJECTS[assessment.subject_slug]["name"],
            "title": assessment.title,
            "difficulty_name": difficulty_label(assessment.difficulty) if assessment.difficulty else None,
        },
        "questions": questions,
    }
    context.update(announcements_context(user))
    return render_template("assessment_take.html", **context)


@app.route("/assessments/<slug>/submit", methods=["POST"])
def assessment_submit(slug):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    assessment = Assessment.query.filter_by(slug=slug).first()
    if not assessment or assessment.status == "draft":
        flash("Please start the assessment first.", "danger")
        return redirect(url_for("home"))
    taken = Attempt.query.filter_by(user_id=user["id"], assessment_id=assessment.id, kind="assessment").count()
    allowed = assessment.attempt_limit + (1 if assessment.extra_attempt else 0)
    started = session.get("assessment_started") == slug
    if taken >= allowed:
        flash("You have used your available attempts.", "danger")
        return redirect(url_for("assessment_lobby", slug=slug))
    if assessment.status == "closed" and not started:
        flash("This assessment is closed.", "danger")
        return redirect(url_for("assessment_lobby", slug=slug))
    questions = [q.as_dict() for q in assessment.questions]
    review_items, earned, auto_total, encouragement = score_answers(questions, request.form)
    attempt = Attempt(
        user_id=user["id"],
        assessment_id=assessment.id,
        kind="assessment",
        subject_slug=assessment.subject_slug,
        title=assessment.title,
        attempt_no=taken + 1,
        score_auto=earned,
        score_total_auto=auto_total,
        review_json=json.dumps(review_items),
        encouragement=encouragement,
        difficulty=assessment.difficulty,
    )
    db.session.add(attempt)
    db.session.commit()
    session.pop("assessment_started", None)
    if not assessment.release_scores:
        flash("Submitted. Scores will appear when your teacher releases them.", "success")
    return redirect(url_for("attempt_review", attempt_id=attempt.id))


@app.route("/practice")
def practice():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] != "student":
        return redirect(url_for("home"))
    ready = []
    locked = []
    for material in Material.query.filter_by(status="approved").order_by(Material.created_at.desc()):
        ready.append(
            {
                "subject": SUBJECTS[material.subject_slug]["name"],
                "title": f"{material.title} Practice Check",
                "meta": "Approved material · Mixed HOTS",
                "href": url_for("practice_setup", subject_slug=material.subject_slug, material_slug=material.slug),
            }
        )
    for material in Material.query.filter_by(owner_id=user["id"], source="student", status="pending"):
        locked.append(
            {
                "subject": SUBJECTS[material.subject_slug]["name"],
                "title": f"{material.title} practice",
                "meta": "Backup upload pending teacher approval",
            }
        )
    context = {"user": user, "practice_ready": ready, "practice_locked": locked}
    context.update(announcements_context(user))
    return render_template("practice_hub.html", **context)


@app.route("/results")
def results():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] != "student":
        return redirect(url_for("home"))
    filter_name = request.args.get("filter", "all")
    query = Attempt.query.filter_by(user_id=user["id"]).order_by(Attempt.submitted_at.desc())
    if filter_name == "assessments":
        query = query.filter_by(kind="assessment")
    elif filter_name == "practice":
        query = query.filter_by(kind="practice")
    else:
        filter_name = "all"
    items = []
    for attempt in query.all():
        items.append(
            {
                "kind": attempt.kind.title(),
                "subject": SUBJECTS.get(attempt.subject_slug, {}).get("name", ""),
                "title": attempt.title,
                "meta": attempt_meta(attempt),
                "difficulty": difficulty_label(attempt.difficulty) if attempt.difficulty else None,
                "action": "Review",
                "href": url_for("attempt_review", attempt_id=attempt.id),
            }
        )
    context = {"user": user, "filter": filter_name, "result_items": items}
    context.update(announcements_context(user))
    return render_template("results.html", **context)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    record = db.session.get(User, user["id"])
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if not check_password_hash(record.password_hash, current):
            flash("Current password is incorrect.", "danger")
        elif len(new) < 8:
            flash("New password must be at least 8 characters.", "danger")
        elif new != confirm:
            flash("New passwords do not match.", "danger")
        else:
            record.password_hash = generate_password_hash(new)
            db.session.commit()
            flash("Password updated. Use your new password next time.", "success")
        return redirect(url_for("profile"))

    if user["role"] != "student":
        return render_template(
            "staff_page.html",
            user=user,
            topbar_sub="Profile",
            role_nav=teacher_nav() if user["role"] == "teacher" else admin_nav(),
            active_nav="profile",
            title="Profile",
            subtitle="Account details and password",
            panels=[{"kicker": "Account", "title": user["name"], "meta": f"{user['email']} · {user['role']}", "action": None, "action_href": None, "soft": True}],
            form_blocks=[
                {
                    "id": "account",
                    "title": "Change password",
                    "note": "Update your temporary password.",
                    "action": url_for("profile"),
                    "submit": "Update Password",
                    "fields": [
                        {"id": "current_password", "name": "current_password", "label": "Current password", "type": "password", "placeholder": "", "required": True},
                        {"id": "new_password", "name": "new_password", "label": "New password", "type": "password", "placeholder": "", "required": True},
                        {"id": "confirm_password", "name": "confirm_password", "label": "Confirm new password", "type": "password", "placeholder": "", "required": True},
                    ],
                }
            ],
        )
    context = {"user": user}
    context.update(announcements_context(user))
    return render_template("profile.html", **context)


@app.route("/announcements")
@app.route("/announcements/<int:announcement_id>")
def announcements(announcement_id=None):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] != "student":
        return redirect(url_for("home"))
    filter_name = request.args.get("filter", "all")
    if filter_name not in {"all", "unread", "English", "Math", "Science"}:
        filter_name = "all"
    selected = None
    arrive = False
    if announcement_id:
        record = db.session.get(Announcement, announcement_id)
        if not record:
            flash("That announcement is not available.", "danger")
            return redirect(url_for("announcements", filter=filter_name if filter_name != "all" else None))
        if not mark_announcement_read(user["id"], announcement_id):
            flash("Unable to update notification status. Please try again.", "danger")
            return redirect(url_for("announcements", filter=filter_name if filter_name != "all" else None))
        arrive = request.args.get("arrive") == "1"
    read_ids = announcement_read_ids(user["id"])
    selected_id = announcement_id
    records = Announcement.query.order_by(Announcement.created_at.desc()).all()
    notes = []
    for note in records:
        item = serialize_announcement(note, read_ids, selected_id, filter_name)
        if note_matches_filter(note, filter_name, read_ids) or item["selected"]:
            notes.append(item)
        if item["selected"]:
            selected = item
    if selected_id and not selected:
        flash("That announcement is not available.", "danger")
        return redirect(url_for("announcements"))
    context = {
        "user": user,
        "filter": filter_name,
        "announcements": notes,
        "selected": selected,
        "arrive": arrive,
        "has_announcements": bool(records),
        "unread_count": unread_announcement_count(user["id"]),
        "list_href": url_for("announcements", filter=filter_name if filter_name != "all" else None),
    }
    context.update(announcements_context(user))
    return render_template("announcements.html", **context)


@app.route("/announcements/<int:announcement_id>/read", methods=["POST"])
def announcement_mark_read(announcement_id):
    user = require_user()
    if not user:
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": False, "error": "Please sign in to continue."}), 401
        return redirect(url_for("login"))
    if user["role"] != "student":
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": False, "error": "You do not have access to that page."}), 403
        return redirect(url_for("home"))
    if not mark_announcement_read(user["id"], announcement_id):
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": False, "error": "Unable to update notification status. Please try again."}), 400
        flash("Unable to update notification status. Please try again.", "danger")
        return redirect(url_for("announcements"))
    if request.headers.get("X-Requested-With") == "fetch":
        return jsonify(
            {
                "ok": True,
                "announcement_id": announcement_id,
                "unread_announcements": unread_announcement_count(user["id"]),
            }
        )
    return redirect(url_for("announcements", announcement_id=announcement_id))


@app.route("/teacher")
@require_role("teacher")
def teacher_home(user):
    slug = teacher_subject_slug(user)
    pending = Material.query.filter_by(subject_slug=slug, status="pending").count()
    approved = Material.query.filter_by(subject_slug=slug, status="approved").count()
    drafts = Assessment.query.filter_by(subject_slug=slug, status="draft").count()
    published = Assessment.query.filter_by(subject_slug=slug, status="published").count()
    attention = []
    unread = unread_message_count(user["id"])
    if unread:
        attention.append(
            {
                "kicker": "Messages",
                "title": f"{unread} student message{'s' if unread != 1 else ''} waiting",
                "meta": "Private academic chat with your students",
                "action": "Open",
                "href": url_for("messages_inbox"),
            }
        )
    for material in Material.query.filter_by(subject_slug=slug, status="pending"):
        attention.append(
            {
                "kicker": "Review queue",
                "title": f"{material.title} awaiting approval",
                "meta": "Student backup upload" if material.source == "student" else "Needs review",
                "action": "Review",
                "href": url_for("teacher_materials"),
            }
        )
    for assessment in Assessment.query.filter_by(subject_slug=slug, status="draft"):
        attention.append(
            {
                "kicker": "HOTS draft",
                "title": assessment.title,
                "meta": "Edit, regenerate, then publish",
                "action": "Open",
                "href": url_for("teacher_hots"),
            }
        )
    if not attention:
        attention.append(
            {
                "kicker": "All clear",
                "title": "No items need attention",
                "meta": "Upload a lesson or generate HOTS questions when ready",
                "action": "Materials",
                "href": url_for("teacher_materials"),
            }
        )
    return render_template(
        "teacher_home.html",
        user=user,
        topbar_sub=f"Teacher · {SUBJECTS[slug]['name']}",
        role_nav=teacher_nav(),
        active_nav="home",
        subject_name=SUBJECTS[slug]["name"],
        stats=[
            {"label": "Approved materials", "value": str(approved), "meta": "Ready for class"},
            {"label": "Draft HOTS sets", "value": str(drafts), "meta": "Needs review"},
            {"label": "Pending uploads", "value": str(pending), "meta": "Student backup"},
            {"label": "Published assessments", "value": str(published), "meta": "Visible to section"},
        ],
        attention=attention,
    )


@app.route("/teacher/materials", methods=["GET", "POST"])
@require_role("teacher")
def teacher_materials(user):
    slug = teacher_subject_slug(user)
    if request.method == "POST":
        action = request.form.get("action", "upload")
        if action == "approve":
            material = db.session.get(Material, request.form.get("material_id", type=int))
            if material and material.subject_slug == slug:
                try:
                    attach_summary(material)
                    material.status = "approved"
                    db.session.commit()
                    flash(f"{material.title} approved and summarized.", "success")
                except Exception:
                    flash("Could not generate a summary. Try again or paste more text.", "danger")
            return redirect(url_for("teacher_materials"))
        if action == "reject":
            material = db.session.get(Material, request.form.get("material_id", type=int))
            if material and material.subject_slug == slug:
                material.status = "rejected"
                material.reject_reason = "Not enough usable lesson text or not aligned to the class material."
                db.session.commit()
                flash("Upload rejected.", "success")
            return redirect(url_for("teacher_materials"))
        title = request.form.get("title", "").strip()
        notes = request.form.get("notes", "").strip()
        file = request.files.get("file")
        try:
            if file and file.filename:
                filename, data = save_file(file)
            elif notes:
                filename, data = "pasted-lesson.txt", notes.encode("utf-8")
            else:
                raise ExtractError("Upload a file or paste lesson text.")
            create_material(title or path_stem(filename), slug, user["id"], "teacher", filename, data)
            flash("Material uploaded, summarized, and approved for your section.", "success")
        except ExtractError as exc:
            flash(str(exc), "danger")
        return redirect(url_for("teacher_materials"))

    panels = []
    for material in Material.query.filter_by(subject_slug=slug).order_by(Material.created_at.desc()):
        panels.append(
            {
                "kicker": material.status.replace("_", " ").title() + f" · {material.source}",
                "title": material.title,
                "meta": (material.filename or "Pasted text") + f" · {len(material.extracted_text or '')} characters",
                "action": "Approve" if material.status == "pending" else None,
                "form_action": url_for("teacher_materials") if material.status == "pending" else None,
                "hidden": {"action": "approve", "material_id": material.id} if material.status == "pending" else None,
                "reject": material.status == "pending",
                "material_id": material.id,
                "soft": material.status != "pending",
            }
        )
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Materials",
        role_nav=teacher_nav(),
        active_nav="materials",
        title="Materials",
        subtitle="Upload Canvas files once. Approve student backups before they can practice.",
        panels=panels,
        form_blocks=[
            {
                "title": "Upload material",
                "note": "PDF, DOCX, PPTX, or paste text. Scanned PDFs without extractable text are rejected.",
                "action": url_for("teacher_materials"),
                "enctype": "multipart/form-data",
                "loading": "Uploading and summarizing…",
                "submit": "Upload & summarize",
                "fields": [
                    {"id": "title", "name": "title", "label": "Material title", "type": "text", "placeholder": "Ecosystems", "required": True},
                    {"id": "file", "name": "file", "label": "File", "type": "file", "placeholder": "", "required": False, "accept": ".pdf,.docx,.pptx,.txt"},
                    {"id": "notes", "name": "notes", "label": "Or paste text", "type": "textarea", "placeholder": "Paste lesson text here...", "required": False},
                ],
            }
        ],
    )


@app.route("/teacher/hots", methods=["GET", "POST"])
@require_role("teacher")
def teacher_hots(user):
    slug = teacher_subject_slug(user)
    if request.method == "POST":
        action = request.form.get("action", "generate")
        if action == "generate":
            material = Material.query.filter_by(id=request.form.get("material_id", type=int), subject_slug=slug, status="approved").first()
            if not material:
                flash("Choose an approved material first.", "danger")
                return redirect(url_for("teacher_hots"))
            try:
                count = max(1, min(int(request.form.get("count") or 5), 8))
            except ValueError:
                count = 5
            bloom = request.form.get("bloom") or "mixed"
            difficulty = normalize_difficulty(request.form.get("difficulty"))
            questions = generate_hots_questions(
                material.title,
                material.extracted_text,
                SUBJECTS[slug]["name"],
                bloom,
                count,
                ["mcq", "essay", "problem"],
                difficulty,
            )
            assessment = Assessment(
                slug=unique_slug(f"{material.title}-hots", Assessment),
                title=f"{material.title} HOTS Assessment",
                subject_slug=slug,
                material_id=material.id,
                created_by=user["id"],
                status="draft",
                difficulty=difficulty,
            )
            db.session.add(assessment)
            db.session.flush()
            for item in questions:
                db.session.add(
                    Question(
                        assessment_id=assessment.id,
                        bloom=item["bloom"],
                        qtype=item["type"],
                        prompt=item["prompt"],
                        options_json=json.dumps(item.get("options") or []),
                        answer=item.get("answer"),
                        explanation=item.get("explanation") or "",
                        rubric=item.get("rubric"),
                        citation=item.get("citation") or "",
                    )
                )
            db.session.commit()
            flash("HOTS set generated. Review items before publishing.", "success")
        elif action == "publish":
            assessment = Assessment.query.filter_by(id=request.form.get("assessment_id", type=int), subject_slug=slug).first()
            if assessment:
                assessment.status = "published"
                deadline = request.form.get("deadline")
                if deadline:
                    try:
                        assessment.deadline = datetime.fromisoformat(deadline)
                    except ValueError:
                        assessment.deadline = datetime.utcnow() + timedelta(days=2)
                else:
                    assessment.deadline = datetime.utcnow() + timedelta(days=2)
                db.session.commit()
                flash("Assessment published to the section.", "success")
        elif action == "regenerate":
            question = db.session.get(Question, request.form.get("question_id", type=int))
            if question and question.assessment.subject_slug == slug:
                material = question.assessment.material
                generated = generate_hots_questions(
                    material.title if material else question.assessment.title,
                    material.extracted_text if material else question.prompt,
                    SUBJECTS[slug]["name"],
                    question.bloom,
                    1,
                    [question.qtype],
                    question.assessment.difficulty or "medium",
                )
                if not generated:
                    flash("Could not regenerate that question.", "danger")
                    return redirect(url_for("teacher_hots"))
                item = generated[0]
                question.prompt = item["prompt"]
                question.options_json = json.dumps(item.get("options") or [])
                question.answer = item.get("answer")
                question.explanation = item.get("explanation") or ""
                question.rubric = item.get("rubric")
                question.citation = item.get("citation") or ""
                db.session.commit()
                flash("Question regenerated.", "success")
        return redirect(url_for("teacher_hots"))

    materials = Material.query.filter_by(subject_slug=slug, status="approved").all()
    assessments = Assessment.query.filter_by(subject_slug=slug).order_by(Assessment.created_at.desc()).all()
    return render_template(
        "teacher_hots.html",
        user=user,
        topbar_sub="HOTS Generator",
        role_nav=teacher_nav(),
        active_nav="hots",
        materials=materials,
        assessments=assessments,
        subject_name=SUBJECTS[slug]["name"],
    )


@app.route("/teacher/monitor", methods=["GET", "POST"])
@require_role("teacher")
def teacher_monitor(user):
    slug = teacher_subject_slug(user)
    if request.method == "POST":
        assessment = Assessment.query.filter_by(id=request.form.get("assessment_id", type=int), subject_slug=slug).first()
        action = request.form.get("action")
        if assessment and action == "close":
            assessment.status = "closed"
            db.session.commit()
            flash("Assessment closed. Students already answering may still submit.", "success")
        elif assessment and action == "reopen":
            assessment.status = "published"
            assessment.extra_attempt = True
            db.session.commit()
            flash("Assessment reopened with one extra attempt. Original attempts stay in history.", "success")
        elif assessment and action == "release_scores":
            assessment.release_scores = True
            db.session.commit()
            flash("Scores released.", "success")
        elif assessment and action == "release_answers":
            assessment.release_answers = True
            db.session.commit()
            flash("Answers released.", "success")
        elif assessment and action == "release_feedback":
            assessment.release_feedback = True
            db.session.commit()
            flash("Feedback released.", "success")
        return redirect(url_for("teacher_monitor"))

    panels = []
    for assessment in Assessment.query.filter_by(subject_slug=slug).order_by(Assessment.created_at.desc()):
        attempts = Attempt.query.filter_by(assessment_id=assessment.id, kind="assessment").all()
        students = User.query.filter_by(role="student").count() or 1
        avg = int(sum(a.score_auto for a in attempts) / max(len(attempts), 1)) if attempts else 0
        panels.append(
            {
                "kicker": assessment.status.title(),
                "title": assessment.title,
                "meta": (
                    f"{len(attempts)}/{students} submitted · Avg auto {avg} · "
                    f"{difficulty_label(assessment.difficulty) if assessment.difficulty else 'Medium'} · "
                    f"Extra attempt {'on' if assessment.extra_attempt else 'off'}"
                ),
                "assessment_id": assessment.id,
                "status": assessment.status,
                "release_scores": assessment.release_scores,
                "release_answers": assessment.release_answers,
                "release_feedback": assessment.release_feedback,
            }
        )
    practice_n = Attempt.query.filter_by(kind="practice", subject_slug=slug).count()
    return render_template(
        "teacher_monitor.html",
        user=user,
        topbar_sub="Monitoring",
        role_nav=teacher_nav(),
        active_nav="monitor",
        panels=panels,
        practice_n=practice_n,
        subject_name=SUBJECTS[slug]["name"],
    )


@app.route("/teacher/announce", methods=["GET", "POST"])
@require_role("teacher")
def teacher_announce(user):
    slug = teacher_subject_slug(user)
    label = SUBJECTS[slug]["announce"]
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title:
            flash("Please add a title.", "danger")
        else:
            db.session.add(Announcement(subject=label, title=title, body=body, teacher_id=user["id"]))
            db.session.commit()
            flash("Announcement posted to your subject feed.", "success")
        return redirect(url_for("teacher_announce"))
    notes = Announcement.query.filter_by(subject=label).order_by(Announcement.created_at.desc()).all()
    panels = [
        {
            "kicker": note.subject,
            "title": note.title,
            "meta": note.created_at.strftime("%b %d") + (f" — {note.body}" if note.body else ""),
            "action": None,
            "action_href": None,
            "soft": True,
        }
        for note in notes
    ]
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Announcements",
        role_nav=teacher_nav(),
        active_nav="announce",
        title="Subject announcements",
        subtitle="Posts appear in the shared student feed, filterable by subject.",
        panels=panels,
        form_blocks=[
            {
                "title": "New announcement",
                "note": "Keep it short and student-friendly.",
                "action": url_for("teacher_announce"),
                "submit": "Post announcement",
                "fields": [
                    {"id": "title", "name": "title", "label": "Title", "type": "text", "placeholder": "Assessment reminder", "required": True},
                    {"id": "body", "name": "body", "label": "Message", "type": "textarea", "placeholder": "Write your announcement...", "required": True},
                ],
            }
        ],
    )


@app.route("/admin")
@require_role("admin")
def admin_home(user):
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
                "title": f"{User.query.count()} accounts",
                "meta": f"{User.query.filter_by(role='student').count()} students · {User.query.filter_by(role='teacher').count()} teachers",
                "action": "Manage",
                "action_href": url_for("admin_users"),
                "soft": True,
            },
            {
                "kicker": "Content",
                "title": f"{Material.query.filter_by(status='approved').count()} approved materials",
                "meta": f"{Assessment.query.filter_by(status='published').count()} published assessments",
                "action": "Reports",
                "action_href": url_for("admin_reports"),
                "soft": True,
            },
        ],
        form_blocks=[],
    )


@app.route("/admin/users", methods=["GET", "POST"])
@require_role("admin")
def admin_users(user):
    if request.method == "POST":
        raw = request.form.get("csv", "").strip()
        created = 0
        reader = csv.reader(io.StringIO(raw))
        for row in reader:
            if not row or len(row) < 4:
                continue
            email, name, role, password = [part.strip() for part in row[:4]]
            subject = row[4].strip() if len(row) > 4 else None
            email = email.lower()
            role = role.lower()
            if role not in {"student", "teacher", "admin"} or User.query.filter_by(email=email).first():
                continue
            if role == "teacher" and subject in {"English", "Mathematics", "Science", "Math"}:
                subject = "Mathematics" if subject == "Math" else subject
            else:
                subject = subject if role == "teacher" else None
            db.session.add(
                User(
                    email=email,
                    name=name or email.split("@")[0],
                    role=role,
                    subject=subject,
                    password_hash=generate_password_hash(password or "Temp1234"),
                )
            )
            created += 1
        db.session.commit()
        if created:
            flash(f"Imported {created} user(s). They can sign in with their temporary passwords.", "success")
        else:
            flash("No new users imported. Check the CSV format, or those emails may already exist.", "danger")
        return redirect(url_for("admin_users"))

    panels = []
    for record in User.query.order_by(User.role, User.name).all():
        panels.append(
            {
                "kicker": record.role.title() + (f" · {record.subject}" if record.subject else ""),
                "title": record.name,
                "meta": record.email,
                "action": None,
                "action_href": None,
                "soft": True,
            }
        )
    return render_template(
        "staff_page.html",
        user=user,
        topbar_sub="Users",
        role_nav=admin_nav(),
        active_nav="users",
        title="Users",
        subtitle="Bulk import school emails, names, roles, and temporary passwords.",
        panels=panels,
        form_blocks=[
            {
                "title": "Bulk import",
                "note": "CSV rows: email, full name, role, temporary password, subject (teachers)",
                "action": url_for("admin_users"),
                "submit": "Import users",
                "sample_target": "csv",
                "sample_value": "student2@letran-calamba.edu.ph, Ana Cruz, student, Temp1234",
                "fields": [
                    {
                        "id": "csv",
                        "name": "csv",
                        "label": "CSV data",
                        "type": "textarea",
                        "placeholder": "student2@letran-calamba.edu.ph, Ana Cruz, student, Temp1234",
                        "required": True,
                    }
                ],
            }
        ],
    )


@app.route("/admin/section")
@require_role("admin")
def admin_section(user):
    teachers = ", ".join(t.subject or t.name for t in User.query.filter_by(role="teacher").all()) or "None yet"
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
                "meta": f"{User.query.filter_by(role='student').count()} students · Teachers: {teachers}",
                "action": None,
                "action_href": None,
                "soft": True,
            }
        ],
        form_blocks=[],
    )


@app.route("/admin/reports")
@require_role("admin")
def admin_reports(user):
    students = User.query.filter_by(role="student").count() or 1
    active = db.session.query(Attempt.user_id).distinct().count()
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
                "title": f"{int(100 * active / students)}% students with activity",
                "meta": f"{Attempt.query.count()} total attempts",
                "action": None,
                "action_href": None,
                "soft": True,
            },
            {
                "kicker": "Assessments",
                "title": f"{Assessment.query.filter_by(status='published').count()} published",
                "meta": f"{Assessment.query.filter_by(status='draft').count()} drafts",
                "action": None,
                "action_href": None,
                "soft": True,
            },
        ],
        form_blocks=[],
    )


@app.route("/admin/settings", methods=["GET", "POST"])
@require_role("admin")
def admin_settings(user):
    if request.method == "POST":
        flash("Pilot defaults saved for this session. Upload limits remain 20 MB / 100 pages.", "success")
        return redirect(url_for("admin_settings"))
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
            {
                "kicker": "AI",
                "title": "Prompt engineering only",
                "meta": "Set OPENAI_API_KEY or GEMINI_API_KEY. Without a key, Bloom uses a grounded fallback generator.",
                "action": None,
                "action_href": None,
                "soft": True,
            },
        ],
        form_blocks=[],
    )


@app.route("/messages")
def messages_inbox():
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] == "admin":
        flash("Messages are for students and teachers.", "danger")
        return redirect(url_for("home"))

    threads = []
    if user["role"] == "student":
        teachers = User.query.filter_by(role="teacher").order_by(User.subject, User.name).all()
        for teacher in teachers:
            if not same_section(user, teacher):
                continue
            conversation = Conversation.query.filter_by(student_id=user["id"], teacher_id=teacher.id).first()
            if conversation and conversation.messages:
                threads.append(conversation_preview(conversation, user["id"]))
            else:
                threads.append(
                    {
                        "id": 0,
                        "other_id": teacher.id,
                        "name": teacher.name,
                        "meta": teacher.subject or "Teacher",
                        "initials": initials(teacher.name),
                        "preview": "Start a private question about a lesson or assessment",
                        "when": "",
                        "unread": 0,
                        "href": url_for("messages_thread", user_id=teacher.id),
                    }
                )
    else:
        conversations = (
            Conversation.query.filter_by(teacher_id=user["id"])
            .order_by(Conversation.updated_at.desc())
            .all()
        )
        threads = [
            conversation_preview(item, user["id"])
            for item in conversations
            if item.messages and item.student and same_section(user, item.student)
        ]
        threads.sort(key=lambda item: (0 if item["unread"] else 1, item["when"] == ""))

    context = {
        "user": user,
        "threads": threads,
        "is_teacher": user["role"] == "teacher",
        "topbar_sub": "Messages",
        "role_nav": teacher_nav() if user["role"] == "teacher" else None,
        "active_nav": "messages",
    }
    context.update(announcements_context(user))
    return render_template("messages_inbox.html", **context)


@app.route("/messages/with/<int:user_id>", methods=["GET", "POST"])
def messages_thread(user_id):
    user = require_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] == "admin":
        flash("Messages are for students and teachers.", "danger")
        return redirect(url_for("home"))

    other = db.session.get(User, user_id)
    if not other or not allowed_chat_partner(user, other):
        flash(
            "You can only message your teachers."
            if user["role"] == "student"
            else "You can only message students in your section.",
            "danger",
        )
        return redirect(url_for("messages_inbox"))

    conversation = find_conversation(user, other)
    if user["role"] == "teacher" and (not conversation or not conversation.messages):
        flash("That student has not started a conversation yet.", "danger")
        return redirect(url_for("messages_inbox"))

    if request.method == "POST":
        body = (request.form.get("body") or "").strip()
        if not body:
            flash("Please type a message first.", "danger")
        elif len(body) > 2000:
            flash("Messages are limited to 2,000 characters.", "danger")
        else:
            if user["role"] == "student":
                conversation = get_or_create_conversation(user["id"], other.id)
            elif not conversation:
                flash("That student has not started a conversation yet.", "danger")
                if request.headers.get("X-Requested-With") == "fetch":
                    return jsonify({"ok": False, "error": "Could not send that message."}), 400
                return redirect(url_for("messages_inbox"))
            if conversation and can_access_conversation(user, conversation):
                db.session.add(
                    ChatMessage(conversation_id=conversation.id, sender_id=user["id"], body=body)
                )
                conversation.updated_at = datetime.utcnow()
                db.session.commit()
                if request.headers.get("X-Requested-With") == "fetch":
                    last = conversation.messages[-1]
                    return jsonify({"ok": True, "message": serialize_message(last, user["id"])})
            else:
                flash("You do not have access to that conversation.", "danger")
        if request.headers.get("X-Requested-With") == "fetch":
            return jsonify({"ok": False, "error": "Could not send that message."}), 400
        return redirect(url_for("messages_thread", user_id=other.id))

    if conversation:
        mark_conversation_read(conversation, user["id"])
    draft = (request.args.get("draft") or "").strip()[:2000]
    messages = [serialize_message(item, user["id"]) for item in (conversation.messages if conversation else [])]
    context = {
        "user": user,
        "other": {
            "id": other.id,
            "name": other.name,
            "meta": other.subject or other.role.title(),
            "initials": initials(other.name),
        },
        "messages": messages,
        "draft": draft,
        "poll_url": url_for("messages_updates", user_id=other.id),
        "send_url": url_for("messages_thread", user_id=other.id),
        "topbar_sub": "Messages",
        "role_nav": teacher_nav() if user["role"] == "teacher" else None,
        "active_nav": "messages",
    }
    context.update(announcements_context(user))
    return render_template("messages_thread.html", **context)


@app.route("/messages/with/<int:user_id>/updates")
def messages_updates(user_id):
    user = require_user()
    if not user:
        return jsonify({"ok": False}), 401
    other = db.session.get(User, user_id)
    if not other or not allowed_chat_partner(user, other):
        return jsonify({"ok": False}), 403
    conversation = find_conversation(user, other)
    if not conversation:
        return jsonify({"ok": True, "messages": [], "read_ids": [], "unread_messages": unread_message_count(user["id"])})
    if not can_access_conversation(user, conversation):
        return jsonify({"ok": False}), 403
    mark_conversation_read(conversation, user["id"])
    after = request.args.get("after", type=int) or 0
    fresh = [item for item in conversation.messages if item.id > after]
    read_ids = [item.id for item in conversation.messages if item.sender_id == user["id"] and item.read_at]
    return jsonify(
        {
            "ok": True,
            "messages": [serialize_message(item, user["id"]) for item in fresh],
            "read_ids": read_ids,
            "unread_messages": unread_message_count(user["id"]),
        }
    )


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="images/letran-calamba-logo.png"))


@app.errorhandler(404)
def not_found(_error):
    return render_template(
        "error.html",
        user=current_user(),
        code=404,
        title="Page not found",
        message="That page is not in Bloom. Head back home and try another path.",
    ), 404


@app.errorhandler(413)
def too_large(_error):
    flash("That file is too large. Uploads are limited to 20 MB.", "danger")
    return redirect(request.referrer or url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You signed out of Bloom.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
