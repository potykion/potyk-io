from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import READS_MENU_GROUPS

reads_bp = Blueprint("reads", __name__, url_prefix="/reads")


@reads_bp.context_processor
def reads_nav_context():
    return {
        "menu_groups": READS_MENU_GROUPS,
        "section_brand_title": "potyk-reads",
        "section_brand_url": "/reads",
    }


@reads_bp.get("/")
def index():
    return render_template("potyk-reads/index.html")
