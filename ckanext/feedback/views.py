from __future__ import annotations

import hashlib
import logging

import requests as http_requests
from flask import Blueprint, jsonify

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckan.common import _, current_user

from ckanext.feedback import config
from ckanext.feedback import model as feedback_model

log = logging.getLogger(__name__)

feedback_blueprint = Blueprint(
    "feedback",
    __name__,
    url_prefix="/dataset/<package_id>/feedback",
)


def _ip_hash() -> str:
    ip = (
        tk.request.access_route[0]
        if tk.request.access_route
        else tk.request.remote_addr
    )
    return hashlib.sha256(ip.encode()).hexdigest()


@feedback_blueprint.route("/rate", methods=["POST"])
def rate(package_id: str):
    rating = tk.request.form.get("rating", type=int)
    if not rating or rating < 1 or rating > 5:
        return jsonify({"error": "Invalid rating"}), 400

    # Verify the package exists.
    try:
        tk.get_action("package_show")({}, {"id": package_id})
    except tk.ObjectNotFound:
        return jsonify({"error": "Dataset not found"}), 404

    ip_hash = _ip_hash()
    user_id = current_user.name if current_user.is_authenticated else None

    feedback_model.upsert_rating(package_id, ip_hash, user_id, rating)
    avg = feedback_model.get_average_rating(package_id)

    return jsonify({
        "average": avg["average"],
        "count": avg["count"],
        "user_rating": rating,
    })


@feedback_blueprint.route("/submit", methods=["POST"])
def submit(package_id: str):
    # Verify the package exists.
    try:
        pkg = tk.get_action("package_show")({}, {"id": package_id})
    except tk.ObjectNotFound:
        tk.abort(404, _("Dataset not found"))

    subject_type = tk.request.form.get("subject_type", "").strip()
    reason = tk.request.form.get("reason", "").strip()
    body = tk.request.form.get("body", "").strip()

    if not subject_type or not reason or not body:
        h.flash_error(_("Please fill in all required fields."))
        return h.redirect_to("dataset.read", id=package_id)

    # reCAPTCHA verification.
    secret = config.recaptcha_secret_key()
    if secret:
        recaptcha_response = tk.request.form.get("g-recaptcha-response", "")
        try:
            resp = http_requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": secret,
                    "response": recaptcha_response,
                },
                timeout=10,
            )
            if not resp.json().get("success"):
                h.flash_error(_("reCAPTCHA verification failed. Please try again."))
                return h.redirect_to("dataset.read", id=package_id)
        except http_requests.RequestException:
            log.exception("reCAPTCHA verification request failed")
            h.flash_error(_("reCAPTCHA verification failed. Please try again."))
            return h.redirect_to("dataset.read", id=package_id)

    user_id = current_user.name if current_user.is_authenticated else None
    author_name = tk.request.form.get("author_name", "").strip() or None
    author_email = tk.request.form.get("author_email", "").strip() or None

    feedback_model.create_submission(
        package_id=package_id,
        user_id=user_id,
        author_name=author_name,
        author_email=author_email,
        subject_type=subject_type,
        reason=reason,
        body=body,
    )

    # Email notification.
    recipients = config.email_recipients()
    if recipients:
        _send_notification(pkg, subject_type, reason, body, author_name, author_email)

    h.flash_success(_("Thank you for your feedback!"))
    return h.redirect_to("dataset.read", id=package_id)


def _send_notification(
    pkg: dict,
    subject_type: str,
    reason: str,
    body: str,
    author_name: str | None,
    author_email: str | None,
):
    from ckan.lib.mailer import mail_recipient

    dataset_title = pkg.get("title") or pkg.get("name")
    subject = _("Dataset feedback: {title}").format(title=dataset_title)
    mail_body = (
        f"Dataset: {dataset_title}\n"
        f"URL: {h.url_for('dataset.read', id=pkg['name'], _external=True)}\n\n"
        f"From: {author_name or 'Anonymous'}\n"
        f"Email: {author_email or 'Not provided'}\n"
        f"I am a: {subject_type}\n"
        f"Reason: {reason}\n\n"
        f"Feedback:\n{body}\n"
    )

    for email in config.email_recipients():
        try:
            mail_recipient("CKAN Admin", email, subject, mail_body)
        except Exception:
            log.exception("Failed to send feedback notification to %s", email)
