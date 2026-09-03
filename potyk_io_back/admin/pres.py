from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from potyk_io_back.admin.forms import CommitPushForm, NewPostForm
from potyk_io_back.admin.git_ops import commit_and_push, list_uncommitted
from potyk_io_back.admin.posts import create_post
from potyk_io_back.inbox.pres import entries_from_db
from potyk_io_back.inbox.tasks import load_local_tasks
from potyk_io_back.potyk_io.menu import admin_menu_groups

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def is_local() -> bool:
    if current_app.debug:
        return True
    host = (request.host or "").lower()
    return (
        host.startswith("localhost")
        or host.startswith("127.0.0.1")
        or host.startswith("[::1]")
    )


def inbox_count() -> int:
    if is_local():
        return len(load_local_tasks())
    return len(entries_from_db())


def admin_nav_context() -> dict:
    count = inbox_count()
    return {
        "is_local": is_local(),
        "menu_groups": admin_menu_groups(
            local=is_local(),
            inbox_badge=count if count else None,
        ),
        "section_brand_title": "админка",
        "section_brand_url": "/admin",
    }


@admin_bp.context_processor
def _admin_ctx():
    return admin_nav_context()


def flash_form_errors(form) -> None:
    for messages in form.errors.values():
        for message in messages:
            flash(message, "error")


@admin_bp.get("/")
@login_required
def index():
    return redirect(url_for("inbox.index"))


@admin_bp.route("/posts/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        try:
            created = create_post(form.title.data or "", form.cover.data)
        except ValueError as exc:
            flash(str(exc), "error")
        else:
            flash(f"Пост создан: {created.url}", "success")
            return redirect(created.url)
    elif form.is_submitted():
        flash_form_errors(form)
    return render_template("admin/new_post.html", form=form)


@admin_bp.route("/commit", methods=["GET", "POST"])
@login_required
def commit():
    if not is_local():
        abort(404)

    form = CommitPushForm()
    files: list[str] = []
    try:
        files = list_uncommitted()
    except RuntimeError as exc:
        flash(str(exc), "error")

    if form.validate_on_submit():
        result = commit_and_push()
        if result.ok:
            flash(result.message, "success")
        else:
            flash(result.message, "error")
        return redirect(url_for("admin.commit"))

    return render_template("admin/commit.html", form=form, files=files)
