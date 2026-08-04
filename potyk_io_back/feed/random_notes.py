import html as html_module
import random
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

PREVIEW_LEN = 200


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


def note_card_html(path: Path, limit: int = PREVIEW_LEN) -> str | None:
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
    count: int = 3,
    limit: int = PREVIEW_LEN,
    exclude: set[str] | frozenset[str] | None = None,
) -> list[dict[str, str]]:
    skip = exclude or set()
    notes = iter_notes()
    random.shuffle(notes)

    result: list[dict[str, str]] = []
    for path in notes:
        if len(result) >= count:
            break
        url = note_url(path)
        if url in skip:
            continue
        preview = note_card_html(path, limit)
        if not preview:
            continue
        result.append(
            {
                "url": url,
                "preview": preview,
                "name": path.name,
            }
        )
    return result


def random_note_batch(
    count: int = 3,
    limit: int = PREVIEW_LEN,
    exclude: set[str] | frozenset[str] | None = None,
) -> tuple[list[dict[str, str]], bool]:
    skip = set(exclude or ())
    batch = random_note_previews(count + 1, limit=limit, exclude=skip)
    notes = batch[:count]
    has_more = len(batch) > count
    return notes, has_more
