from pathlib import Path

from flask import Blueprint, request

from potyk_io_back.mu.menu import MU_MENU_ITEMS, is_mu_link_active
from potyk_io_back.potyk_io.md_rendering import render_body_html, split_frontmatter
from potyk_io_back.potyk_io.md_rendering.created import resolve_created

MU_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-mu"

mu_bp = Blueprint("mu", __name__, url_prefix="/mu")


@mu_bp.context_processor
def inject_mu_menu():
    items = [
        {
            "icon": item["icon"],
            "title": item["title"],
            "url": item["url"],
            "active": is_mu_link_active(item["url"], request.path),
        }
        for item in MU_MENU_ITEMS
    ]
    return {"mu_menu_items": items}


def render_mu_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        template="potyk-mu/page.html",
    )


@mu_bp.route("/")
def index():
    return render_mu_markdown(MU_TEMPLATES_DIR / "index.md")
