from pathlib import Path

from flask import Blueprint, abort, render_template, send_file

from potyk_io_back.potyk_io.menu import ART_MENU_GROUPS

ART_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-art"

art_bp = Blueprint("art", __name__, url_prefix="/art")


@art_bp.context_processor
def art_nav_context():
    return {
        "menu_groups": ART_MENU_GROUPS,
        "section_brand_title": "potyk-art",
        "section_brand_url": "/art",
    }


def list_art_projects() -> list[dict]:
    if not ART_TEMPLATES_DIR.is_dir():
        return []

    projects: list[dict] = []
    for folder in sorted(ART_TEMPLATES_DIR.iterdir(), key=lambda p: p.name.casefold()):
        if not folder.is_dir():
            continue
        images = [
            {
                "url": f"/art/{folder.name}/{image.name}",
                "alt": image.stem,
            }
            for image in sorted(folder.iterdir(), key=lambda p: p.name.casefold())
            if image.is_file() and image.suffix.casefold() == ".jpg"
        ]
        projects.append(
            {
                "title": folder.name.replace("-", " "),
                "images": images,
            }
        )
    return projects


@art_bp.get("/")
def index():
    return render_template("potyk-art/index.html", projects=list_art_projects())


@art_bp.get("/<path:asset_path>")
def asset(asset_path: str):
    file = (ART_TEMPLATES_DIR / asset_path).resolve()
    try:
        file.relative_to(ART_TEMPLATES_DIR.resolve())
    except ValueError:
        abort(404)
    if not file.is_file() or file.suffix.casefold() != ".jpg":
        abort(404)
    return send_file(file)
