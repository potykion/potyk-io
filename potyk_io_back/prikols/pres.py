from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import PRIKOL_MENU_GROUPS

prikol_bp = Blueprint("prikol", __name__, url_prefix="/prikol")


@prikol_bp.context_processor
def prikol_nav_context():
    return {
        "menu_groups": PRIKOL_MENU_GROUPS,
        "section_brand_title": "potyk-prikol",
        "section_brand_url": "/prikol",
    }


@prikol_bp.get("/")
def index():
    return render_template("potyk-prikol/index.html")
