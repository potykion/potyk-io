from pathlib import Path

import yaml
from flask import Blueprint, render_template

from potyk_io_back.potyk_io.menu import CULTURE_MENU_GROUPS

ART_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-art"
ART_PROJECTS_YML = ART_TEMPLATES_DIR / "projects.yml"

art_bp = Blueprint("art", __name__, url_prefix="/art")

_WIP_STATUSES = {"wip", "in_progress", "в работе"}


@art_bp.context_processor
def art_nav_context():
    return {
        "menu_groups": CULTURE_MENU_GROUPS,
        "section_brand_title": "potyk-art",
        "section_brand_url": "/art",
    }


def _parse_project(raw: dict) -> dict | None:
    title = str(raw.get("title") or "").strip()
    if not title:
        return None
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
    return {"title": title, "subtitle": subtitle, "images": images}


def load_art_project_sections() -> tuple[list[dict], list[dict]]:
    """Возвращает (готовые, в работе)."""
    if not ART_PROJECTS_YML.is_file():
        return [], []

    try:
        data = yaml.safe_load(ART_PROJECTS_YML.read_text(encoding="utf-8-sig")) or {}
    except (OSError, yaml.YAMLError):
        return [], []

    done: list[dict] = []
    wip: list[dict] = []

    for raw in data.get("in_progress") or data.get("wip") or []:
        if not isinstance(raw, dict):
            continue
        parsed = _parse_project(raw)
        if parsed:
            wip.append(parsed)

    for raw in data.get("projects") or []:
        if not isinstance(raw, dict):
            continue
        parsed = _parse_project(raw)
        if not parsed:
            continue
        status = str(raw.get("status") or "").strip().lower()
        if status in _WIP_STATUSES:
            wip.append(parsed)
        else:
            done.append(parsed)

    return done, wip


def list_art_projects() -> list[dict]:
    """Готовые проекты (обратная совместимость)."""
    done, _wip = load_art_project_sections()
    return done


@art_bp.get("/")
def index():
    projects, in_progress = load_art_project_sections()
    return render_template(
        "potyk-art/index.html",
        projects=projects,
        in_progress=in_progress,
    )
