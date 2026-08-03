import os

import flask
from flask import Flask, abort

from potyk_io_back.feed import random_note_previews
from potyk_io_back.md_rendering import (
    TEMPLATES_DIR,
    render_body_html,
    resolve_page,
    split_frontmatter,
)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["FLASK_SECRET"]

    @app.route("/")
    def index():
        return flask.render_template(
            "index.html",
            random_notes=random_note_previews(3),
        )

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
            ctx["random_notes"] = random_note_previews(3)
        return flask.render_template(template_name, **ctx)

    return app
