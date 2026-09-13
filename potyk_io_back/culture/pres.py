from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, render_template, request, send_file
from sqlalchemy import select

from potyk_io_back.culture.entities import CultureVisit, seed_culture_visits_if_empty
from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.md_rendering import (
    list_folder_pages,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.menu import CULTURE_MENU_GROUPS

CULTURE_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-culture"

culture_bp = Blueprint("culture", __name__, url_prefix="/culture")


@culture_bp.context_processor
def culture_nav_context():
    return {
        "menu_groups": CULTURE_MENU_GROUPS,
        "section_brand_title": "potyk-culture",
        "section_brand_url": "/culture",
    }


def culture_page_url(path: PurePosixPath) -> str:
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        return "/culture" if parent == "." else f"/culture/{parent}"
    return f"/culture/{path.with_suffix('').as_posix()}"


def make_culture_link_rewriter(file: Path):
    root = CULTURE_TEMPLATES_DIR.resolve()
    current_dir = file.parent.resolve()

    def rewrite(url: str) -> str | None:
        if url.startswith(("http://", "https://", "mailto:", "tel:", "#", "/")):
            return None

        raw_target, hash_sep, fragment = url.partition("#")
        target, query_sep, query = raw_target.partition("?")
        if not target.endswith(".md"):
            return None

        resolved = (current_dir / PurePosixPath(target)).resolve()
        try:
            relative = PurePosixPath(resolved.relative_to(root).as_posix())
        except ValueError:
            return None

        rewritten = culture_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_culture_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_culture_link_rewriter(file),
    )


def _visits():
    seed_culture_visits_if_empty()
    return db.session.scalars(
        select(CultureVisit).order_by(CultureVisit.visited_at.desc(), CultureVisit.id.desc())
    ).all()


@culture_bp.get("/")
def index():
    pages = list_folder_pages(CULTURE_TEMPLATES_DIR, url_prefix="/culture")
    return render_template("potyk-culture/index.html", pages=pages)


@culture_bp.get("/teatr")
@culture_bp.get("/teatr/")
def teatr():
    return render_template("potyk-culture/teatr.html", visits=_visits())


@culture_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path, root=CULTURE_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_culture_markdown(file)

    if file.suffix == ".html":
        template_name = f"potyk-culture/{file.relative_to(CULTURE_TEMPLATES_DIR).as_posix()}"
        ctx = {}
        if file.name == "index.html":
            ctx["pages"] = list_folder_pages(
                file.parent,
                url_prefix=culture_page_url(
                    PurePosixPath(file.relative_to(CULTURE_TEMPLATES_DIR).as_posix())
                ),
            )
        elif file.stem == "teatr":
            ctx["visits"] = _visits()
        return render_template(template_name, **ctx)

    return send_file(file)
