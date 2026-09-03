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


@admin_bp.context_processor
def _admin_ctx():
    return {"is_local": is_local()}


def flash_form_errors(form) -> None:
    for messages in form.errors.values():
        for message in messages:
            flash(message, "error")


@admin_bp.get("/")
@login_required
def index():
    sections = [
        {
            "title": "Создание поста",
            "url": url_for("admin.new_post"),
            "description": "Название и обложка (картинка или видео)",
        },
    ]
    if is_local():
        sections.append(
            {
                "title": "Коммит и пуш",
                "url": url_for("admin.commit"),
                "description": "Незакоммиченные файлы → commit + push",
            }
        )
    return render_template("admin/index.html", sections=sections)


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
