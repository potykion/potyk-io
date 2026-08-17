import flask
from flask import Blueprint, abort

from potyk_io_back.potyk_io.feed import BATCH_SIZE, random_note_batch, search_notes
from potyk_io_back.potyk_io.md_rendering import (
    TEMPLATES_DIR,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.menu import MENU_GROUPS

potyk_io_bp = Blueprint("potyk_io", __name__)


@potyk_io_bp.context_processor
def inject_menu():
    return {
        "menu_groups": MENU_GROUPS,
    }


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
