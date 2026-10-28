import io
import zipfile
from datetime import datetime
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import login_required

from potyk_io_back.admin.backup import list_backups, upload_main_db
from potyk_io_back.admin.forms import BackupForm, CommitPushForm, NewPostForm
from potyk_io_back.admin.git_ops import commit_and_push, list_uncommitted
from potyk_io_back.admin.posts import create_post
from potyk_io_back.potyk_io.menu import admin_menu_groups

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "templates"


def is_local() -> bool:
    if current_app.debug:
        return True
    host = (request.host or "").lower()
    return (
        host.startswith("localhost")
        or host.startswith("127.0.0.1")
        or host.startswith("[::1]")
    )


def admin_nav_context() -> dict:
    return {
        "is_local": is_local(),
        "menu_groups": admin_menu_groups(local=is_local()),
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


@admin_bp.route("/")
@login_required
def index():
    return render_template("admin/index.html")


@admin_bp.route("/download-content")
@login_required
def download_content():
    if not TEMPLATES_DIR.is_dir():
        abort(404)

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in TEMPLATES_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(TEMPLATES_DIR).as_posix())
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"templates-{stamp}.zip",
    )


@admin_bp.route("/backups", methods=["GET", "POST"])
@login_required
def backups():
    form = BackupForm()
    if form.validate_on_submit():
        result = upload_main_db()
        flash(result.message, "success" if result.ok else "error")
        return redirect(url_for("admin.backups"))

    objects, list_error = list_backups()
    if list_error:
        flash(list_error, "error")
    return render_template(
        "admin/backups.html",
        form=form,
        backups=objects,
    )


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


@admin_bp.route("/design-system")
@login_required
def design_system():
    return render_template("admin/design_system.html")


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
