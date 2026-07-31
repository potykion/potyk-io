import os
import re
from pathlib import Path

import flask
import markdown
from flask import Flask, abort

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
MD_EXTENSIONS = ["extra", "sane_lists", "nl2br"]
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FALSEY = {"false", "0", "no", "off"}


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ["FLASK_SECRET"]

    @app.route("/")
    def index():
        return flask.render_template("index.html")

    @app.route("/<path:page_path>")
    def page(page_path: str):
        file = resolve_page(page_path)
        if file is None:
            abort(404)

        if file.suffix == ".md":
            meta, body = split_frontmatter(file.read_text(encoding="utf-8"))
            content = markdown.markdown(
                body,
                extensions=MD_EXTENSIONS,
                output_format="html",
            )
            show_header = str(meta.get("header", "true")).strip().lower() not in FALSEY
            return flask.render_template(
                "page.html", content=content, show_header=show_header
            )

        return flask.render_template(str(file.relative_to(TEMPLATES_DIR)).replace("\\", "/"))

    return app


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line[:1].isspace():
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key:
            meta[key] = value.strip()
    return meta, text[match.end() :]


def resolve_page(page_path: str) -> Path | None:
    page_path = page_path.strip("/")
    if not page_path or ".." in Path(page_path).parts:
        return None

    name = Path(page_path).name
    if name.startswith("_") or name.startswith("."):
        return None

    candidates = [
        TEMPLATES_DIR / f"{page_path}.md",
        TEMPLATES_DIR / page_path / "index.md",
        TEMPLATES_DIR / f"{page_path}.html",
        TEMPLATES_DIR / page_path / "index.html",
    ]

    templates_root = TEMPLATES_DIR.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(templates_root)
        except (ValueError, OSError):
            continue
        if resolved.is_file() and not resolved.name.startswith("_"):
            return resolved

    return None
