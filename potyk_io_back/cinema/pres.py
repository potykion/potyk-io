import json
from pathlib import Path

from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required

from potyk_io_back.potyk_io.collections.movies import load_movies_data, movies_for_client
from potyk_io_back.potyk_io.md_rendering import render_body_html, split_frontmatter
from potyk_io_back.potyk_io.menu import CINEMA_MENU_GROUPS

cinema_bp = Blueprint("cinema", __name__, url_prefix="/cinema")

CINEMA_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-cinema"


@cinema_bp.context_processor
def cinema_nav_context():
    return {
        "menu_groups": CINEMA_MENU_GROUPS,
        "section_brand_title": "potyk-cinema",
        "section_brand_url": "/cinema",
    }


@cinema_bp.get("/")
def index():
    page = load_movies_data()
    return render_template(
        "potyk-cinema/index.html",
        collections=page.collections,
        movies_by_collection_json=json.dumps(movies_for_client(page), ensure_ascii=False),
    )


@cinema_bp.get("/where-to-watch")
def where_to_watch():
    return render_template("potyk-cinema/where-to-watch.html")


@cinema_bp.get("/vietnamese-cinema")
def vietnamese_cinema():
    file = CINEMA_TEMPLATES_DIR / "vietnamese-cinema.md"
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    return render_body_html(body, meta, title="Вьетнамское кино")


@cinema_bp.get("/admin")
@login_required
def movies_admin_redirect():
    return redirect(url_for("admin.cinema"), code=301)
