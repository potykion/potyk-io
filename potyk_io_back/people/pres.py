from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, render_template, request, send_file
from flask_login import login_required

from potyk_io_back.potyk_io.md_rendering import (
    list_folder_pages,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.menu import PEOPLE_MENU_GROUPS

PEOPLE_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-people"

people_bp = Blueprint("people", __name__, url_prefix="/people")


@people_bp.before_request
@login_required
def require_login():
    pass


@people_bp.context_processor
def people_nav_context():
    return {
        "menu_groups": PEOPLE_MENU_GROUPS,
        "section_brand_title": "potyk-people",
        "section_brand_url": "/people",
    }


def people_page_url(path: PurePosixPath) -> str:
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        return "/people" if parent == "." else f"/people/{parent}"
    return f"/people/{path.with_suffix('').as_posix()}"


def make_people_link_rewriter(file: Path):
    root = PEOPLE_TEMPLATES_DIR.resolve()
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

        rewritten = people_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_people_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_people_link_rewriter(file),
    )


@people_bp.get("/")
def index():
    pages = list_folder_pages(
        PEOPLE_TEMPLATES_DIR,
        url_prefix="/people",
        sort="name",
    )
    return render_template("potyk-people/index.html", pages=pages)


@people_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path, root=PEOPLE_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_people_markdown(file)

    if file.suffix == ".html":
        template_name = f"potyk-people/{file.relative_to(PEOPLE_TEMPLATES_DIR).as_posix()}"
        ctx = {}
        if file.name == "index.html":
            ctx["pages"] = list_folder_pages(
                file.parent,
                url_prefix=people_page_url(
                    PurePosixPath(file.relative_to(PEOPLE_TEMPLATES_DIR).as_posix())
                ),
            )
        return render_template(template_name, **ctx)

    return send_file(file)
