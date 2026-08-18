from flask import Blueprint, render_template
from flask_login import login_required

from potyk_io_back.potyk_io.menu import MENU_GROUPS

inbox_bp = Blueprint("inbox", __name__, url_prefix="/inbox")


@inbox_bp.context_processor
def inject_menu():
    return {
        "menu_groups": MENU_GROUPS,
    }


@inbox_bp.get("/")
@login_required
def index():
    return render_template("inbox/index.html")


@inbox_bp.get("/send")
@login_required
def send():
    return render_template("inbox/send.html")
