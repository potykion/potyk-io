from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from sqlalchemy import select

from potyk_io_back.anti.entities import AntiPost
from potyk_io_back.anti.forms import AntiPostForm
from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.menu import ANTI_MENU_GROUPS

anti_bp = Blueprint("anti", __name__, url_prefix="/anti")


@anti_bp.before_request
@login_required
def require_login():
    pass


@anti_bp.context_processor
def anti_nav_context():
    return {
        "menu_groups": ANTI_MENU_GROUPS,
        "section_brand_title": "potyk-anti",
        "section_brand_url": "/anti",
    }


@anti_bp.get("/")
def index():
    posts = db.session.scalars(
        select(AntiPost).order_by(AntiPost.created_at.desc(), AntiPost.id.desc())
    ).all()
    return render_template(
        "potyk-anti/index.html",
        posts=posts,
        form=AntiPostForm(),
    )


@anti_bp.post("/post")
def create_post():
    form = AntiPostForm()
    if not form.validate_on_submit():
        error = (form.body.errors or form.errors.get("csrf_token") or ["Не вышло запостить"])[0]
        return jsonify({"ok": False, "error": error}), 400

    body = (form.body.data or "").strip()
    post = AntiPost(body=body)
    db.session.add(post)
    db.session.commit()
    return jsonify(
        {
            "ok": True,
            "post": {
                "id": post.id,
                "body": post.body,
                "created_at": post.created_at.isoformat(timespec="seconds"),
                "created_at_display": post.created_at.strftime("%d.%m.%Y %H:%M"),
            },
        }
    )
