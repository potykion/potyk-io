from pathlib import Path

import yaml
from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import CULTURE_MENU_GROUPS

ART_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-art"
ART_PROJECTS_YML = ART_TEMPLATES_DIR / "projects.yml"

art_bp = Blueprint("art", __name__, url_prefix="/art")


@art_bp.context_processor
def art_nav_context():
    return {
        "menu_groups": CULTURE_MENU_GROUPS,
        "section_brand_title": "potyk-art",
        "section_brand_url": "/art",
    }


def list_art_projects() -> list[dict]:
    if not ART_PROJECTS_YML.is_file():
        return []

    try:
        data = yaml.safe_load(ART_PROJECTS_YML.read_text(encoding="utf-8-sig")) or {}
    except (OSError, yaml.YAMLError):
        return []

    projects: list[dict] = []
    for raw in data.get("projects") or []:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or "").strip()
        if not title:
            continue
        subtitle = str(raw.get("subtitle") or "").strip()
        images = []
        for url in raw.get("images") or []:
            url = str(url).strip()
            if not url:
                continue
            images.append(
                {
                    "url": url,
                    "alt": Path(url).stem,
                }
            )
        projects.append({"title": title, "subtitle": subtitle, "images": images})
    return projects


@art_bp.get("/")
def index():
    return render_template("potyk-art/index.html", projects=list_art_projects())
