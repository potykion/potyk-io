from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, redirect, render_template, request, send_file

from potyk_io_back.potyk_io.md_rendering import (
    list_folder_pages,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.menu import TECH_MENU_GROUPS

TECH_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-tech"

tech_bp = Blueprint("tech", __name__, url_prefix="/tech")


@tech_bp.context_processor
def tech_nav_context():
    return {
        "menu_groups": TECH_MENU_GROUPS,
        "section_brand_title": "potyk-tech",
        "section_brand_url": "/tech",
    }


def tech_page_url(path: PurePosixPath) -> str:
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        return "/tech" if parent == "." else f"/tech/{parent}"
    return f"/tech/{path.with_suffix('').as_posix()}"


def make_tech_link_rewriter(file: Path):
    root = TECH_TEMPLATES_DIR.resolve()
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

        rewritten = tech_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_tech_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_tech_link_rewriter(file),
    )


@tech_bp.get("/")
def index():
    return render_template("potyk-tech/index.html")


@tech_bp.get("/my-code/ai")
@tech_bp.get("/my-code/ai/")
def my_code_ai_moved():
    return redirect("/tech/ai", code=301)


@tech_bp.get("/my-code/ai-coding")
@tech_bp.get("/my-code/ai-coding/")
def my_code_ai_coding_moved():
    return redirect("/tech/ai-coding", code=301)


@tech_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path, root=TECH_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_tech_markdown(file)

    if file.suffix == ".html":
        template_name = f"potyk-tech/{file.relative_to(TECH_TEMPLATES_DIR).as_posix()}"
        ctx = {}
        if file.name == "index.html":
            ctx["pages"] = list_folder_pages(
                file.parent,
                url_prefix=tech_page_url(
                    PurePosixPath(file.relative_to(TECH_TEMPLATES_DIR).as_posix())
                ),
            )
        return render_template(template_name, **ctx)

    return send_file(file)
