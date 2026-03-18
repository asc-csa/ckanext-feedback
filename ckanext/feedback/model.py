from __future__ import annotations

import datetime
import logging
from typing import Optional

from sqlalchemy import Column, Table, UniqueConstraint, types, Integer, DateTime
from ckan.model import meta

log = logging.getLogger(__name__)

feedback_rating_table = Table(
    "feedback_rating",
    meta.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("package_id", types.UnicodeText, index=True, nullable=False),
    Column("ip_hash", types.UnicodeText, nullable=False),
    Column("user_id", types.UnicodeText, nullable=True),
    Column("rating", Integer, nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
    UniqueConstraint("package_id", "ip_hash", name="uq_feedback_rating_pkg_ip"),
)

feedback_submission_table = Table(
    "feedback_submission",
    meta.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("package_id", types.UnicodeText, index=True, nullable=False),
    Column("user_id", types.UnicodeText, nullable=True),
    Column("author_name", types.UnicodeText, nullable=True),
    Column("author_email", types.UnicodeText, nullable=True),
    Column("subject_type", types.UnicodeText, nullable=False),
    Column("reason", types.UnicodeText, nullable=False),
    Column("body", types.UnicodeText, nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)


class FeedbackRating:
    id: int
    package_id: str
    ip_hash: str
    user_id: Optional[str]
    rating: int
    created_at: datetime.datetime


class FeedbackSubmission:
    id: int
    package_id: str
    user_id: Optional[str]
    author_name: Optional[str]
    author_email: Optional[str]
    subject_type: str
    reason: str
    body: str
    created_at: datetime.datetime


meta.registry.map_imperatively(FeedbackRating, feedback_rating_table)
meta.registry.map_imperatively(FeedbackSubmission, feedback_submission_table)


def upsert_rating(
    package_id: str,
    ip_hash: str,
    user_id: Optional[str],
    rating: int,
):
    session = meta.Session
    existing = (
        session.query(FeedbackRating)
        .filter_by(package_id=package_id, ip_hash=ip_hash)
        .first()
    )
    if existing is None:
        existing = FeedbackRating()
        existing.package_id = package_id
        existing.ip_hash = ip_hash
        session.add(existing)

    existing.user_id = user_id
    existing.rating = rating
    existing.created_at = datetime.datetime.utcnow()
    session.commit()


def get_average_rating(package_id: str) -> dict:
    from sqlalchemy import func

    session = meta.Session
    row = (
        session.query(
            func.avg(FeedbackRating.rating),
            func.count(FeedbackRating.id),
        )
        .filter_by(package_id=package_id)
        .first()
    )
    avg_val = row[0]
    count = row[1]
    return {
        "average": round(float(avg_val), 1) if avg_val else 0,
        "count": count,
    }


def get_user_rating(package_id: str, ip_hash: str) -> Optional[int]:
    session = meta.Session
    row = (
        session.query(FeedbackRating)
        .filter_by(package_id=package_id, ip_hash=ip_hash)
        .first()
    )
    return row.rating if row else None


def create_submission(
    package_id: str,
    user_id: Optional[str],
    author_name: Optional[str],
    author_email: Optional[str],
    subject_type: str,
    reason: str,
    body: str,
) -> FeedbackSubmission:
    session = meta.Session
    sub = FeedbackSubmission()
    sub.package_id = package_id
    sub.user_id = user_id
    sub.author_name = author_name
    sub.author_email = author_email
    sub.subject_type = subject_type
    sub.reason = reason
    sub.body = body
    sub.created_at = datetime.datetime.utcnow()
    session.add(sub)
    session.commit()
    return sub


def get_submissions(
    page: int = 1,
    per_page: int = 20,
    package_id: Optional[str] = None,
) -> list[FeedbackSubmission]:
    q = meta.Session.query(FeedbackSubmission)
    if package_id:
        q = q.filter_by(package_id=package_id)
    q = q.order_by(FeedbackSubmission.created_at.desc())
    offset = (page - 1) * per_page
    return q.offset(offset).limit(per_page).all()


def count_submissions(package_id: Optional[str] = None) -> int:
    q = meta.Session.query(FeedbackSubmission)
    if package_id:
        q = q.filter_by(package_id=package_id)
    return q.count()


def delete_submission(submission_id: int):
    session = meta.Session
    sub = session.query(FeedbackSubmission).get(submission_id)
    if sub:
        session.delete(sub)
        session.commit()
