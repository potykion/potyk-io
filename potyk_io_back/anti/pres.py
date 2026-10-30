from flask import Blueprint, flash, redirect, render_template, url_for
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
        posts = db.session.scalars(
            select(AntiPost).order_by(AntiPost.created_at.desc(), AntiPost.id.desc())
        ).all()
        return render_template(
            "potyk-anti/index.html",
            posts=posts,
            form=form,
            open_post_modal=True,
        ), 400

    body = (form.body.data or "").strip()
    db.session.add(AntiPost(body=body))
    db.session.commit()
    flash("Запостил", "success")
    return redirect(url_for("anti.index"))
