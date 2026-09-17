from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import MONEY_MENU_GROUPS

money_bp = Blueprint("money", __name__, url_prefix="/money")


@money_bp.context_processor
def money_nav_context():
    return {
        "menu_groups": MONEY_MENU_GROUPS,
        "section_brand_title": "potyk-money",
        "section_brand_url": "/money",
    }


@money_bp.get("/")
def index():
    return render_template("potyk-money/index.html")
