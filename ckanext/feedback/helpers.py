from __future__ import annotations

import hashlib

import ckan.plugins.toolkit as tk
from ckan.common import request

from ckanext.feedback import config, model as feedback_model


def _ip_hash() -> str:
    ip = request.access_route[0] if request.access_route else request.remote_addr
    return hashlib.sha256(ip.encode()).hexdigest()


def feedback_rating_avg(package_id: str) -> dict:
    return feedback_model.get_average_rating(package_id)


def feedback_user_rating(package_id: str) -> int | None:
    return feedback_model.get_user_rating(package_id, _ip_hash())


def feedback_recaptcha_site_key() -> str:
    return config.recaptcha_site_key()


def feedback_subject_types() -> list[str]:
    return config.subject_types()


def feedback_reasons() -> list[str]:
    return config.reasons()
