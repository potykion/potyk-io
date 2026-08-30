import re
from collections.abc import Callable
from datetime import date

import flask
import markdown
from markdown.extensions.toc import slugify_unicode

from potyk_io_back.potyk_io.md_rendering.created import (
    created_from_meta,
    format_created_ru,
)
from potyk_io_back.potyk_io.md_rendering.hashtags import linkify_hashtags

MD_EXTENSIONS = [
    "extra",
    "sane_lists",
    "nl2br",
    "pymdownx.magiclink",
    "pymdownx.mark",
    "pymdownx.tasklist",
]
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FALSEY = {"false", "0", "no", "off"}
TRUEY = {"true", "1", "yes", "on"}
H1_RE = re.compile(r"(<h1\b[^>]*>.*?</h1>)", re.IGNORECASE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"`([^`]*)`")
CREATED_RE = re.compile(
    r'(<time\s+class="note-created"[^>]*>.*?</time>)',
    re.IGNORECASE | re.DOTALL,
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
TOC_CONFIG = {"toc_depth": "2-4", "slugify": slugify_unicode}


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


def plain_h1(title: str) -> str:
    return INLINE_CODE_RE.sub(r"\1", title).strip()


def ensure_h1(body: str, title: str) -> str:
    if extract_h1(body):
        return body
    return f"# {title}\n\n{body}"


def inject_created(html: str, created: date, title: str | None) -> str:
    created_iso = created.isoformat()
    if title and title == created_iso:
        return html
    stamp = (
        f'<time class="note-created" datetime="{created_iso}">'
        f"{format_created_ru(created)}</time>"
    )
    if H1_RE.search(html):
        return H1_RE.sub(rf"\1\n{stamp}", html, count=1)
    return f"{stamp}\n{html}"


def meta_flag(meta: dict[str, str], key: str, *, default: bool = False) -> bool:
    raw = unquote_meta(str(meta.get(key, "")))
    if not raw:
        return default
    value = raw.strip().lower()
    if value in TRUEY:
        return True
    if value in FALSEY:
        return False
    return default


def inject_toc(html: str, toc: str) -> str:
    if "<li>" not in toc:
        return html
    block = toc.replace('class="toc"', 'class="toc md-toc"', 1)
    if CREATED_RE.search(html):
        return CREATED_RE.sub(rf"\1\n{block}", html, count=1)
    if H1_RE.search(html):
        return H1_RE.sub(rf"\1\n{block}", html, count=1)
    return f"{block}\n{html}"


def rewrite_markdown_links(
    body: str, link_rewriter: Callable[[str], str | None]
) -> str:
    def replace(match: re.Match[str]) -> str:
        label, url = match.groups()
        rewritten = link_rewriter(url)
        if not rewritten or rewritten == url:
            return match.group(0)
        return f"[{label}]({rewritten})"

    return MARKDOWN_LINK_RE.sub(replace, body)


def render_body_html(
    body: str,
    meta: dict[str, str],
    title: str | None = None,
    created: date | None = None,
    base_href: str | None = None,
    link_rewriter: Callable[[str], str | None] | None = None,
    template: str = "potyk-io/page.html",
) -> str:
    if title:
        body = ensure_h1(body, title)
    page_title = plain_h1(extract_h1(body) or title or "")
    if link_rewriter is not None:
        body = rewrite_markdown_links(body, link_rewriter)

    show_toc = meta_flag(meta, "toc")
    extensions = list(MD_EXTENSIONS)
    extension_configs: dict = {}
    if show_toc:
        extensions.append("toc")
        extension_configs["toc"] = TOC_CONFIG

    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=extension_configs,
        output_format="html",
    )
    content = md.convert(linkify_hashtags(body))

    if created is None:
        created = created_from_meta(meta)
    if created is not None:
        content = inject_created(content, created, title)
    if show_toc:
        content = inject_toc(content, md.toc)

    show_header = str(meta.get("header", "true")).strip().lower() not in FALSEY
    return flask.render_template(
        template,
        content=content,
        show_header=show_header,
        base_href=base_href,
        page_title=page_title,
    )
