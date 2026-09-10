from flask import Blueprint, render_template
from sqlalchemy import select

from potyk_io_back.culture.entities import CultureVisit, seed_culture_visits_if_empty
from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.menu import CULTURE_MENU_GROUPS

culture_bp = Blueprint("culture", __name__, url_prefix="/culture")


@culture_bp.context_processor
def culture_nav_context():
    return {
        "menu_groups": CULTURE_MENU_GROUPS,
        "section_brand_title": "potyk-culture",
        "section_brand_url": "/culture",
    }


@culture_bp.get("/")
def index():
    seed_culture_visits_if_empty()
    visits = db.session.scalars(
        select(CultureVisit).order_by(CultureVisit.visited_at.desc(), CultureVisit.id.desc())
    ).all()
    return render_template("potyk-culture/index.html", visits=visits)
