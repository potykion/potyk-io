import json
from pathlib import Path, PurePosixPath

import flask
from flask import Blueprint, abort, request, send_file

from potyk_io_back.potyk_io.collections.movies import load_movies_data, movies_for_client
from potyk_io_back.potyk_io.feed import BATCH_SIZE, random_note_batch, search_notes
from potyk_io_back.potyk_io.md_rendering import (
    FOOD_TEMPLATES_DIR,
    TEMPLATES_DIR,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.menu import FOOD_MENU_GROUPS, MENU_GROUPS

potyk_io_bp = Blueprint("potyk_io", __name__)


@potyk_io_bp.context_processor
def inject_menu():
    is_food = request.path.startswith("/food")
    menu_groups = FOOD_MENU_GROUPS if is_food else MENU_GROUPS
    return {
        "menu_groups": menu_groups,
        "section_brand_title": "potyk-food" if is_food else "potyk.io",
        "section_brand_url": "/food" if is_food else "/",
    }


def food_page_url(path: PurePosixPath) -> str:
    if path.name == "index.md":
        parent = path.parent.as_posix()
        return "/food" if parent == "." else f"/food/{parent}"
    return f"/food/{path.with_suffix('').as_posix()}"


def make_food_link_rewriter(file: Path):
    root = FOOD_TEMPLATES_DIR.resolve()
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

        rewritten = food_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_food_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_food_link_rewriter(file),
    )


@potyk_io_bp.route("/")
def index():
    notes, has_more = random_note_batch(BATCH_SIZE)
    return flask.render_template(
        "potyk-io/index.html",
        notes=notes,
        has_more=has_more,
        exclude=[n.get("id", n["url"]) for n in notes],
    )


@potyk_io_bp.route("/feed/more")
def feed_more():
    exclude = {
        u for u in flask.request.args.get("exclude", "").split(",") if u
    }
    notes, has_more = random_note_batch(BATCH_SIZE, exclude=exclude)
    return flask.render_template(
        "potyk-io/_notes_batch.html",
        notes=notes,
        has_more=has_more,
        exclude=[*exclude, *(n.get("id", n["url"]) for n in notes)],
    )


@potyk_io_bp.route("/search")
def search():
    q = flask.request.args.get("q", "").strip()
    results = search_notes(q) if q else []
    return flask.render_template("potyk-io/search.html", q=q, results=results)


@potyk_io_bp.route("/collections/movies")
def movies_collection():
    page = load_movies_data()
    return flask.render_template(
        "potyk-io/collections/movies.html",
        collections=page.collections,
        watch_later=page.watch_later,
        movies_by_collection_json=json.dumps(movies_for_client(page), ensure_ascii=False),
    )


@potyk_io_bp.route("/food")
@potyk_io_bp.route("/food/")
def food_index():
    return render_food_markdown(FOOD_TEMPLATES_DIR / "index.md")


@potyk_io_bp.route("/food/<path:page_path>")
def food_page(page_path: str):
    file = resolve_page(page_path, root=FOOD_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_food_markdown(file)

    return send_file(file)


@potyk_io_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
        created = resolve_created(file, meta)
        return render_body_html(body, meta, title=file.stem, created=created)

    template_name = f"potyk-io/{file.relative_to(TEMPLATES_DIR).as_posix()}"
    ctx = {}
    if file == TEMPLATES_DIR / "index.html":
        notes, has_more = random_note_batch(BATCH_SIZE)
        ctx.update(
            notes=notes,
            has_more=has_more,
            exclude=[n.get("id", n["url"]) for n in notes],
        )
    return flask.render_template(template_name, **ctx)
