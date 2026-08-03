import html as html_module
import os
import random
import re
from html.parser import HTMLParser
from pathlib import Path

import flask
import markdown
from flask import Flask, abort

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
MD_EXTENSIONS = ["extra", "sane_lists", "nl2br", "pymdownx.magiclink"]
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FALSEY = {"false", "0", "no", "off"}
PREVIEW_LEN = 200
MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.DOTALL | re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE
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

    @app.route("/menu")
    def menu():
        return flask.render_template("menu.html")

    @app.route("/<path:page_path>")
    def page(page_path: str):
        file = resolve_page(page_path)
        if file is None:
            abort(404)

        if file.suffix == ".md":
            meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
            content = markdown.markdown(
                body,
                extensions=MD_EXTENSIONS,
                output_format="html",
            )
            show_header = str(meta.get("header", "true")).strip().lower() not in FALSEY
            return flask.render_template(
                "page.html", content=content, show_header=show_header
            )

        template_name = str(file.relative_to(TEMPLATES_DIR)).replace("\\", "/")
        ctx = {}
        if template_name == "index.html":
            ctx["random_notes"] = random_note_previews(3)
        return flask.render_template(template_name, **ctx)

    return app


def iter_notes() -> list[Path]:
    notes: list[Path] = []
    for path in TEMPLATES_DIR.rglob("*.md"):
        if any(part.startswith(".") or part.startswith("_") for part in path.parts):
            continue
        if path.name.startswith(".") or path.name.startswith("_"):
            continue
        if path.name == "index.md":
            continue
        notes.append(path)
    return notes


def note_url(path: Path) -> str:
    rel = path.relative_to(TEMPLATES_DIR).with_suffix("").as_posix()
    if rel.endswith("/index"):
        rel = rel[: -len("/index")]
    return f"/{rel}"


class _HtmlPreviewTruncator(HTMLParser):
    def __init__(self, limit: int):
        super().__init__(convert_charrefs=False)
        self.limit = limit
        self.count = 0
        self.parts: list[str] = []
        self.open_tags: list[str] = []
        self.done = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.done:
            return
        attr_html = "".join(
            f" {name}"
            if value is None
            else f' {name}="{html_module.escape(value, quote=True)}"'
            for name, value in attrs
        )
        self.parts.append(f"<{tag}{attr_html}>")
        if tag not in {"br", "hr", "img", "meta", "input", "source", "wbr"}:
            self.open_tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.done:
            return
        self.parts.append(f"</{tag}>")
        for i in range(len(self.open_tags) - 1, -1, -1):
            if self.open_tags[i] == tag:
                del self.open_tags[i:]
                break

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.done:
            return
        attr_html = "".join(
            f" {name}"
            if value is None
            else f' {name}="{html_module.escape(value, quote=True)}"'
            for name, value in attrs
        )
        self.parts.append(f"<{tag}{attr_html} />")

    def handle_data(self, data: str) -> None:
        if self.done:
            return
        remaining = self.limit - self.count
        if len(data) <= remaining:
            self.parts.append(html_module.escape(data))
            self.count += len(data)
            return
        self.parts.append(html_module.escape(data[:remaining]) + "…")
        self.count = self.limit
        self.done = True
        while self.open_tags:
            self.parts.append(f"</{self.open_tags.pop()}>")

    def handle_entityref(self, name: str) -> None:
        if self.done:
            return
        if self.count >= self.limit:
            self.parts.append("…")
            self.done = True
            while self.open_tags:
                self.parts.append(f"</{self.open_tags.pop()}>")
            return
        self.parts.append(f"&{name};")
        self.count += 1

    def handle_charref(self, name: str) -> None:
        if self.done:
            return
        if self.count >= self.limit:
            self.parts.append("…")
            self.done = True
            while self.open_tags:
                self.parts.append(f"</{self.open_tags.pop()}>")
            return
        self.parts.append(f"&#{name};")
        self.count += 1


def unquote_meta(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1].strip()
    return value


def extract_h1(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def main_inner_html(page_html: str) -> str:
    match = MAIN_RE.search(page_html)
    if not match:
        return ""
    return SCRIPT_STYLE_RE.sub("", match.group(1)).strip()


def html_text(fragment: str) -> str:
    text = TAG_RE.sub(" ", fragment)
    text = html_module.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def truncate_html(fragment: str, limit: int) -> str:
    truncator = _HtmlPreviewTruncator(limit)
    truncator.feed(fragment)
    truncator.close()
    return "".join(truncator.parts)


def render_body_html(body: str, meta: dict[str, str]) -> str:
    content = markdown.markdown(
        body,
        extensions=MD_EXTENSIONS,
        output_format="html",
    )
    show_header = str(meta.get("header", "true")).strip().lower() not in FALSEY
    return flask.render_template("page.html", content=content, show_header=show_header)


def note_card_html(path: Path, limit: int = PREVIEW_LEN) -> str | None:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
    preview_meta = unquote_meta(meta.get("preview", ""))

    if preview_meta:
        parts: list[str] = []
        h1 = extract_h1(body)
        if h1:
            parts.append(f"<h1>{html_module.escape(h1)}</h1>")
        parts.append(f"<p>{html_module.escape(preview_meta)}</p>")
        return "".join(parts)

    inner = main_inner_html(render_body_html(body, meta))
    if not html_text(inner):
        return None
    return truncate_html(inner, limit)


def random_note_previews(
    count: int = 3, limit: int = PREVIEW_LEN
) -> list[dict[str, str]]:
    notes = iter_notes()
    random.shuffle(notes)

    result: list[dict[str, str]] = []
    for path in notes:
        if len(result) >= count:
            break
        preview = note_card_html(path, limit)
        if not preview:
            continue
        result.append(
            {
                "url": note_url(path),
                "preview": preview,
                "name": path.name,
            }
        )
    return result


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
        TEMPLATES_DIR / page_path / "menu.html",
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
