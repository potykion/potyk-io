import html as html_module
import re

from potyk_io_back.feed.random_notes import expand_note_entries, iter_notes, note_cover
from potyk_io_back.md_rendering import extract_h1, unquote_meta

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


def _highlight(text: str, query: str) -> str:
    if not query:
        return html_module.escape(text)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    parts: list[str] = []
    last = 0
    for match in pattern.finditer(text):
        parts.append(html_module.escape(text[last : match.start()]))
        parts.append(f"<mark>{html_module.escape(match.group())}</mark>")
        last = match.end()
    parts.append(html_module.escape(text[last:]))
    return "".join(parts)


def search_notes(query: str) -> list[dict]:
    q = query.strip().lower()
    if not q:
        return []

    title_hits: list[dict] = []
    body_hits: list[dict] = []

    for path in iter_notes():
        for cid, url, meta, body in expand_note_entries(path):
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

            parts = [f"<h2>{_highlight(title, q)}</h2>"]
            if snippet:
                parts.append(f"<p>{_highlight(snippet, q)}</p>")

            card = {
                "id": cid,
                "url": url,
                "preview": "".join(parts),
                "name": path.name,
                "kind": "note",
                "external": False,
                "title": title,
            }
            cover = note_cover(meta)
            if cover:
                card["cover"] = cover
            if in_title:
                title_hits.append(card)
            else:
                body_hits.append(card)

    title_hits.sort(key=lambda c: c["title"].lower())
    body_hits.sort(key=lambda c: c["title"].lower())
    return title_hits + body_hits
