import os

import flask
from flask import Flask, abort

from potyk_io_back.feed import BATCH_SIZE, random_note_batch, search_notes
from potyk_io_back.md_rendering import (
    TEMPLATES_DIR,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.menu import MENU_GROUPS, MENU_QUICK


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["FLASK_SECRET"]

    @app.context_processor
    def inject_menu():
        return {
            "menu_quick": MENU_QUICK,
            "menu_groups": MENU_GROUPS,
        }

    @app.route("/")
    def index():
        notes, has_more = random_note_batch(BATCH_SIZE)
        return flask.render_template(
            "index.html",
            notes=notes,
            has_more=has_more,
            exclude=[n["url"] for n in notes],
        )

    @app.route("/feed/more")
    def feed_more():
        exclude = {
            u for u in flask.request.args.get("exclude", "").split(",") if u
        }
        notes, has_more = random_note_batch(BATCH_SIZE, exclude=exclude)
        return flask.render_template(
            "_notes_batch.html",
            notes=notes,
            has_more=has_more,
            exclude=[*exclude, *(n["url"] for n in notes)],
        )

    @app.route("/search")
    def search():
        q = flask.request.args.get("q", "").strip()
        results = search_notes(q) if q else []
        return flask.render_template("search.html", q=q, results=results)

    @app.route("/<path:page_path>")
    def page(page_path: str):
        file = resolve_page(page_path)
        if file is None:
            abort(404)

        if file.suffix == ".md":
            meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
            return render_body_html(body, meta, title=file.stem)

        template_name = str(file.relative_to(TEMPLATES_DIR)).replace("\\", "/")
        ctx = {}
        if template_name == "index.html":
            notes, has_more = random_note_batch(BATCH_SIZE)
            ctx.update(
                notes=notes,
                has_more=has_more,
                exclude=[n["url"] for n in notes],
            )
        return flask.render_template(template_name, **ctx)

    return app
