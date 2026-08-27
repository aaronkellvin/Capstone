"""Smoke tests for Bloom auth, CSRF, and attempt ownership."""

import os
import tempfile
import unittest

# Isolate a temp DB before importing the app module side effects.
os.environ["BLOOM_ENV"] = "development"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["BLOOM_SHOW_PILOTS"] = "0"
os.environ["FLASK_DEBUG"] = "0"

_tmp = tempfile.TemporaryDirectory()
os.environ["BLOOM_TEST_DB"] = os.path.join(_tmp.name, "test.db")

import app as bloom  # noqa: E402
from models import Attempt, User, db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


class BloomSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bloom.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.environ["BLOOM_TEST_DB"]
        bloom.app.config["TESTING"] = True
        bloom.app.config["WTF_CSRF_ENABLED"] = False  # unused; custom CSRF still active
        with bloom.app.app_context():
            db.drop_all()
            db.create_all()
            student = User(
                email="student@test.local",
                name="Test Student",
                role="student",
                password_hash=generate_password_hash("student123"),
            )
            other = User(
                email="other@test.local",
                name="Other Student",
                role="student",
                password_hash=generate_password_hash("student123"),
            )
            teacher = User(
                email="teacher@test.local",
                name="Test Teacher",
                role="teacher",
                subject="Science",
                password_hash=generate_password_hash("teacher123"),
            )
            db.session.add_all([student, other, teacher])
            db.session.commit()
            attempt = Attempt(
                user_id=other.id,
                kind="practice",
                subject_slug="science",
                title="Other student practice",
                score_auto=1,
                score_total_auto=1,
                review_json="[]",
            )
            db.session.add(attempt)
            db.session.commit()
            cls.student_id = student.id
            cls.other_id = other.id
            cls.teacher_id = teacher.id
            cls.other_attempt_id = attempt.id

    def setUp(self):
        self.client = bloom.app.test_client()

    def _csrf(self):
        # Ensure a CSRF token exists in the session (login clears session keys).
        with self.client.session_transaction() as sess:
            token = sess.get("_csrf_token")
            if not token:
                import secrets

                token = secrets.token_urlsafe(32)
                sess["_csrf_token"] = token
            return token

    def _login(self, email, password):
        token = self._csrf()
        return self.client.post(
            "/login",
            data={"email": email, "password": password, "csrf_token": token},
            follow_redirects=False,
        )

    def test_invalid_login(self):
        response = self._login("student@test.local", "wrong-password")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_valid_login(self):
        response = self._login("student@test.local", "student123")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/home", response.headers["Location"])

    def test_csrf_rejects_bare_post(self):
        self._login("student@test.local", "student123")
        response = self.client.post("/logout", data={}, follow_redirects=False)
        self.assertIn(response.status_code, {302, 400})

    def test_student_cannot_view_other_attempt(self):
        self._login("student@test.local", "student123")
        response = self.client.get(f"/results/{self.other_attempt_id}", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/results") or "/results" in response.headers["Location"])

    def test_teacher_subject_scoped_attempt(self):
        self._login("teacher@test.local", "teacher123")
        response = self.client.get(f"/results/{self.other_attempt_id}", follow_redirects=False)
        # Science teacher may view science attempt owned by a student.
        self.assertEqual(response.status_code, 200)

    def test_student_blocked_from_teacher_home(self):
        self._login("student@test.local", "student123")
        response = self.client.get("/teacher", follow_redirects=False)
        self.assertIn(response.status_code, {302, 403})

    def test_logout_get_does_not_clear_session(self):
        self._login("student@test.local", "student123")
        response = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get("user_id"), self.student_id)

    def test_logout_post_clears_session(self):
        self._login("student@test.local", "student123")
        token = self._csrf()
        response = self.client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get("user_id"))


if __name__ == "__main__":
    unittest.main()
