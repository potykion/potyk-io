import html as html_module
import re

from potyk_io_back.feed.random_notes import iter_notes, note_url
from potyk_io_back.md_rendering import extract_h1, split_frontmatter, unquote_meta

SNIPPET_RADIUS = 80


def _plain_body(body: str) -> str:
    text = re.sub(r"^#+\s*", "", body, flags=re.MULTILINE)
    text = re.sub(r"[*`_~\[\]()#>|-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _snippet(text: str, query: str) -> str:
    lower = text.lower()
    idx = lower.find(query)
    if idx < 0:
        return text[: SNIPPET_RADIUS * 2].strip()
    start = max(0, idx - SNIPPET_RADIUS)
    end = min(len(text), idx + len(query) + SNIPPET_RADIUS)
    chunk = text[start:end].strip()
    if start > 0:
        chunk = "…" + chunk
    if end < len(text):
        chunk = chunk + "…"
    return chunk


def search_notes(query: str) -> list[dict]:
    q = query.strip().lower()
    if not q:
        return []

    title_hits: list[dict] = []
    body_hits: list[dict] = []

    for path in iter_notes():
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        title = extract_h1(body) or path.stem
        preview_meta = unquote_meta(meta.get("preview", ""))
        plain = _plain_body(body)

        in_title = q in title.lower() or q in path.stem.lower()
        in_preview = bool(preview_meta) and q in preview_meta.lower()
        in_body = q in plain.lower() or in_preview
        if not in_title and not in_body:
            continue

        if in_preview:
            snippet = preview_meta
        elif in_body:
            snippet = _snippet(plain, q)
        else:
            snippet = preview_meta or _snippet(plain, q)

        parts = [f"<h2>{html_module.escape(title)}</h2>"]
        if snippet:
            parts.append(f"<p>{html_module.escape(snippet)}</p>")

        card = {
            "url": note_url(path),
            "preview": "".join(parts),
            "name": path.name,
            "kind": "note",
            "external": False,
            "title": title,
        }
        if in_title:
            title_hits.append(card)
        else:
            body_hits.append(card)

    title_hits.sort(key=lambda c: c["title"].lower())
    body_hits.sort(key=lambda c: c["title"].lower())
    return title_hits + body_hits
