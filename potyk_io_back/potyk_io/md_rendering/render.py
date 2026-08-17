import re

import flask
import markdown

from potyk_io_back.potyk_io.md_rendering.hashtags import linkify_hashtags

MD_EXTENSIONS = ["extra", "sane_lists", "nl2br", "pymdownx.magiclink"]
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FALSEY = {"false", "0", "no", "off"}


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


def ensure_h1(body: str, title: str) -> str:
    if extract_h1(body):
        return body
    return f"# {title}\n\n{body}"


def render_body_html(body: str, meta: dict[str, str], title: str | None = None) -> str:
    if title:
        body = ensure_h1(body, title)
    content = markdown.markdown(
        linkify_hashtags(body),
        extensions=MD_EXTENSIONS,
        output_format="html",
    )
    show_header = str(meta.get("header", "true")).strip().lower() not in FALSEY
    return flask.render_template(
        "potyk-io/page.html", content=content, show_header=show_header
    )
