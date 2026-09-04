from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import ART_MENU_GROUPS

art_bp = Blueprint("art", __name__, url_prefix="/art")


@art_bp.context_processor
def art_nav_context():
    return {
        "menu_groups": ART_MENU_GROUPS,
        "section_brand_title": "potyk-art",
        "section_brand_url": "/art",
    }


@art_bp.get("/")
def index():
    return render_template("potyk-art/index.html")
