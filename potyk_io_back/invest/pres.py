from flask import Blueprint, abort, render_template

from potyk_io_back.invest.dashboard import build_dashboard, load_news_page

invest_bp = Blueprint("invest", __name__, url_prefix="/invest")


@invest_bp.route("/")
def index():
    return render_template("potyk-invest/index.html", sectors=build_dashboard())


@invest_bp.route("/Новости/<path:slug>")
def news(slug: str):
    page = load_news_page(slug)
    if page is None:
        abort(404)
    return render_template("potyk-invest/news.html", page=page)
