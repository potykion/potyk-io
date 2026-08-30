from datetime import date
from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, render_template, request, send_file

from potyk_io_back.potyk_io.md_rendering import (
    list_folder_pages,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.travel.menu import TRAVEL_MENU_ITEMS, is_travel_link_active

TRAVEL_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-travel"

travel_bp = Blueprint("travel", __name__, url_prefix="/travel")


@travel_bp.context_processor
def inject_travel_menu():
    items = [
        {
            "icon": item["icon"],
            "title": item["title"],
            "url": item["url"],
            "active": is_travel_link_active(item["url"], request.path),
        }
        for item in TRAVEL_MENU_ITEMS
    ]
    return {"travel_menu_items": items}


def travel_page_url(path: PurePosixPath) -> str:
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        return "/travel" if parent == "." else f"/travel/{parent}"
    return f"/travel/{path.with_suffix('').as_posix()}"


def make_travel_link_rewriter(file: Path):
    root = TRAVEL_TEMPLATES_DIR.resolve()
    current_dir = file.parent.resolve()

    def rewrite(url: str) -> str | None:
        if url.startswith(("http://", "https://", "mailto:", "tel:", "#", "/")):
            return None

        raw_target, hash_sep, fragment = url.partition("#")
        target, query_sep, query = raw_target.partition("?")

        resolved = (current_dir / PurePosixPath(target)).resolve()
        if not target.endswith(".md"):
            md_candidate = resolved.with_suffix(".md") if resolved.suffix == "" else Path(f"{resolved}.md")
            if md_candidate.is_file():
                resolved = md_candidate
            elif not resolved.is_file():
                return None
        try:
            relative = PurePosixPath(resolved.relative_to(root).as_posix())
        except ValueError:
            return None
        if relative.suffix != ".md":
            return None

        rewritten = travel_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_travel_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_travel_link_rewriter(file),
        template="potyk-travel/page.html",
    )


def _folder_pages(folder: str, *, sort: str = "name") -> list[dict[str, str | date | None]]:
    return list_folder_pages(
        TRAVEL_TEMPLATES_DIR / folder,
        url_prefix=f"/travel/{folder}",
        sort=sort,
    )


@travel_bp.route("/")
def index():
    return render_template(
        "potyk-travel/index.html",
        memories=_folder_pages("memories", sort="date_desc"),
        plans=_folder_pages("plans"),
    )


@travel_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path, root=TRAVEL_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_travel_markdown(file)

    if file.suffix == ".html":
        if file.name == "index.html":
            rel = PurePosixPath(file.relative_to(TRAVEL_TEMPLATES_DIR).as_posix())
            template_name = f"potyk-travel/{rel.as_posix()}"
            sort = "date_desc" if file.parent.name == "memories" else "name"
            return render_template(
                template_name,
                pages=list_folder_pages(
                    file.parent,
                    url_prefix=travel_page_url(rel),
                    sort=sort,
                ),
            )
        return send_file(file)

    return send_file(file)
