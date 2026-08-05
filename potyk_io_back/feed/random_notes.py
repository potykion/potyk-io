import html as html_module
import random
import re
from pathlib import Path

from potyk_io_back.md_rendering import (
    TEMPLATES_DIR,
    demote_headings,
    extract_h1,
    html_text,
    main_inner_html,
    render_body_html,
    split_frontmatter,
    truncate_html,
    unquote_meta,
    unwrap_links,
)
from potyk_io_back.menu import is_external_url, iter_menu_items

PREVIEW_LEN = 200
BATCH_SIZE = 9

# Разделитель записей внутри дневника (после frontmatter): строка ---
DIARY_ENTRY_SEP_RE = re.compile(r"\r?\n---\s*\r?\n")

HIDDEN_NOTE_DIRS = {"Шаблоны", "tasks"}
HIDDEN_NOTE_STEMS = {"toc"}


def iter_notes() -> list[Path]:
    notes: list[Path] = []
    for path in TEMPLATES_DIR.rglob("*.md"):
        rel_parts = path.relative_to(TEMPLATES_DIR).parts
        if any(part.startswith(".") or part.startswith("_") for part in path.parts):
            continue
        if path.name.startswith(".") or path.name.startswith("_"):
            continue
        if path.name == "index.md":
            continue
        if any(part in HIDDEN_NOTE_DIRS for part in rel_parts):
            continue
        if path.stem in HIDDEN_NOTE_STEMS:
            continue
        notes.append(path)
    return notes


def note_url(path: Path) -> str:
    rel = path.relative_to(TEMPLATES_DIR).with_suffix("").as_posix()
    if rel.endswith("/index"):
        rel = rel[: -len("/index")]
    return f"/{rel}"


def is_diary_note(path: Path) -> bool:
    return path.relative_to(TEMPLATES_DIR).parts[:1] == ("diary",)


def split_diary_entries(body: str) -> list[str]:
    return [part.strip() for part in DIARY_ENTRY_SEP_RE.split(body) if part.strip()]


def expand_note_entries(path: Path) -> list[tuple[str, str, dict[str, str], str]]:
    """Один файл → карточки ленты. Diary режется по --- на отдельные записи.

    Возвращает (card_id, url, meta, body): url — ссылка на день/страницу,
    card_id — уникальный ключ для exclude в ленте.
    """
    meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
    base_url = note_url(path)
    if not is_diary_note(path):
        return [(base_url, base_url, meta, body)]

    entries = split_diary_entries(body)
    if not entries:
        return []
    if len(entries) == 1:
        return [(base_url, base_url, meta, entries[0])]
    return [
        (f"{base_url}~{i}", base_url, meta, entry) for i, entry in enumerate(entries)
    ]


def card_id(card: dict) -> str:
    return card.get("id", card["url"])


def note_cover(meta: dict[str, str]) -> str:
    return unquote_meta(meta.get("cover", ""))


def note_card_html(
    path: Path,
    limit: int = PREVIEW_LEN,
    *,
    meta: dict[str, str] | None = None,
    body: str | None = None,
) -> str | None:
    if meta is None or body is None:
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
    preview_meta = unquote_meta(meta.get("preview", ""))
    title = path.stem

    if preview_meta:
        parts: list[str] = []
        h1 = extract_h1(body) or title
        parts.append(f"<h2>{html_module.escape(h1)}</h2>")
        parts.append(f"<p>{html_module.escape(preview_meta)}</p>")
        return "".join(parts)

    inner = main_inner_html(render_body_html(body, meta, title=title))
    if not html_text(inner):
        return None
    return unwrap_links(demote_headings(truncate_html(inner, limit)))


def random_note_previews(
    count: int = BATCH_SIZE,
    limit: int = PREVIEW_LEN,
    exclude: set[str] | frozenset[str] | None = None,
) -> list[dict]:
    skip = exclude or set()
    candidates: list[tuple[Path, str, str, dict[str, str], str]] = []
    for path in iter_notes():
        for cid, url, meta, body in expand_note_entries(path):
            if cid in skip:
                continue
            candidates.append((path, cid, url, meta, body))
    random.shuffle(candidates)

    result: list[dict] = []
    for path, cid, url, meta, body in candidates:
        if len(result) >= count:
            break
        preview = note_card_html(path, limit, meta=meta, body=body)
        if not preview:
            continue
        card = {
            "id": cid,
            "url": url,
            "preview": preview,
            "name": path.name,
        }
        cover = note_cover(meta)
        if cover:
            card["cover"] = cover
        result.append(card)
    return result


def menu_link_cards(
    exclude: set[str] | frozenset[str] | None = None,
) -> list[dict]:
    skip = set(exclude or ())
    skip.update(note_url(path) for path in iter_notes())
    cards: list[dict] = []
    for item in iter_menu_items():
        url = item["url"]
        if url in skip:
            continue
        title = html_module.escape(item["title"])
        parts = [f"<h2>{title}</h2>"]
        if item.get("description"):
            parts.append(f"<p>{html_module.escape(item['description'])}</p>")
        cards.append(
            {
                "id": url,
                "url": url,
                "preview": "".join(parts),
                "name": item["title"],
                "kind": "link",
                "external": is_external_url(url),
            }
        )
    return cards


def random_note_batch(
    count: int = BATCH_SIZE,
    limit: int = PREVIEW_LEN,
    exclude: set[str] | frozenset[str] | None = None,
) -> tuple[list[dict], bool]:
    skip = set(exclude or ())
    notes = random_note_previews(count + 1, limit=limit, exclude=skip)
    for note in notes:
        note.setdefault("kind", "note")
        note.setdefault("external", False)

    links = menu_link_cards(exclude=skip)
    random.shuffle(links)
    # ~1 link на 2 слота, чтобы заметки оставались основой ленты
    link_budget = max(1, (count + 1) // 2) if links else 0
    pool = notes + links[:link_budget]
    random.shuffle(pool)

    batch = pool[:count]
    used = {card_id(item) for item in batch}
    has_more = any(card_id(n) not in used for n in notes) or any(
        card_id(link) not in used for link in links
    )
    return batch, has_more
