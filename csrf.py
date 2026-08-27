"""Lightweight CSRF protection without Flask-WTF."""

from __future__ import annotations

import secrets

from flask import flash, jsonify, redirect, request, session, url_for


def get_csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def _submitted_token() -> str | None:
    token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    if token:
        return token
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        value = payload.get("csrf_token")
        if value:
            return str(value)
    return None


def csrf_is_valid() -> bool:
    expected = session.get("_csrf_token")
    submitted = _submitted_token()
    if not expected or not submitted:
        return False
    return secrets.compare_digest(str(submitted), str(expected))


def init_csrf(app):
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": get_csrf_token}

    @app.before_request
    def enforce_csrf():
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        if csrf_is_valid():
            return None
        wants_json = (
            request.headers.get("X-Requested-With") == "fetch"
            or "application/json" in (request.headers.get("Accept") or "")
        )
        message = "Your session expired or this form is out of date. Refresh the page and try again."
        if wants_json:
            return jsonify({"ok": False, "error": message}), 400
        flash(message, "danger")
        target = request.referrer or url_for("login" if not session.get("user_id") else "home")
        return redirect(target)
