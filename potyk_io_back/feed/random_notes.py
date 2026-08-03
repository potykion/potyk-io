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
)

PREVIEW_LEN = 200


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
    return demote_headings(truncate_html(inner, limit))


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
