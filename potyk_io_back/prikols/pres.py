from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import PRIKOLS_MENU_GROUPS

prikols_bp = Blueprint("prikols", __name__, url_prefix="/prikols")


@prikols_bp.context_processor
def prikols_nav_context():
    return {
        "menu_groups": PRIKOLS_MENU_GROUPS,
        "section_brand_title": "potyk-prikols",
        "section_brand_url": "/prikols",
    }


@prikols_bp.get("/")
def index():
    return render_template("potyk-prikols/index.html")
