from __future__ import annotations

import logging

from flask import Blueprint

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.plugins.toolkit as tk
from ckan.common import _, current_user

from ckanext.feedback import model as feedback_model

log = logging.getLogger(__name__)

feedback_admin = Blueprint(
    "feedback_admin",
    __name__,
    url_prefix="/ckan-admin/feedback",
)


@feedback_admin.before_request
def before_request():
    try:
        context = {"user": current_user.name, "auth_user_obj": current_user}
        logic.check_access("sysadmin", context)
    except logic.NotAuthorized:
        base.abort(403, _("Need to be system administrator to administer"))


@feedback_admin.route("", methods=["GET"])
def index():
    page = tk.request.args.get("page", 1, type=int)
    package_id = tk.request.args.get("package_id", "").strip() or None

    total_count = feedback_model.count_submissions(package_id=package_id)
    submissions = feedback_model.get_submissions(
        page=page, per_page=20, package_id=package_id
    )

    page_obj = h.Page(
        collection=submissions,
        page=page,
        item_count=total_count,
        items_per_page=20,
        url=h.pager_url,
        presliced_list=True,
    )

    return tk.render(
        "admin/feedback.html",
        extra_vars={
            "page": page_obj,
            "total_count": total_count,
            "package_id_filter": package_id,
        },
    )


@feedback_admin.route("/delete/<int:submission_id>", methods=["POST"])
def delete(submission_id: int):
    feedback_model.delete_submission(submission_id)
    h.flash_success(_("Feedback submission deleted."))
    return h.redirect_to("feedback_admin.index")
