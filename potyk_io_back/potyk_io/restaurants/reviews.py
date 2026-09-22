"""Отзывы о ресторанах (markdown в potyk-food/restaurants)."""

from __future__ import annotations

import html as html_module
from pathlib import Path

from potyk_io_back.potyk_io.md_rendering import split_frontmatter, unquote_meta
from potyk_io_back.potyk_io.md_rendering.created import format_created_ru, parse_iso_date

_PROP_FIELDS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("tags", "Теги", ("tags",)),
    ("maps", "Я.Карты", ("maps", "ЯКарты")),
    ("prices", "Цены", ("prices", "Цены")),
    ("visited", "Дата посещения", ("visited",)),
)


def is_restaurant_review(file: Path, *, restaurants_dir: Path) -> bool:
    try:
        rel = file.relative_to(restaurants_dir)
    except ValueError:
        return False
    return file.suffix == ".md" and rel.stem != "index"


def parse_restaurant_tags(meta: dict[str, str]) -> list[str]:
    raw = unquote_meta(meta.get("tags", ""))
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def _meta_value(meta: dict[str, str], keys: tuple[str, ...]) -> str:
    for key in keys:
        raw = unquote_meta(meta.get(key, ""))
        if raw:
            return raw
    return ""


def _format_cell(key: str, raw: str) -> str:
    if key == "maps":
        return (
            f'<a href="{html_module.escape(raw)}" target="_blank" rel="noopener">'
            "Открыть</a>"
        )
    if key == "visited":
        parsed = parse_iso_date(raw)
        if parsed:
            return html_module.escape(format_created_ru(parsed))
    if key == "tags":
        tags = [part.strip() for part in raw.split(",") if part.strip()]
        return html_module.escape(", ".join(tags)) if tags else html_module.escape(raw)
    return html_module.escape(raw)


def restaurant_props_html(meta: dict[str, str]) -> str | None:
    rows: list[str] = []
    for key, label, aliases in _PROP_FIELDS:
        raw = _meta_value(meta, aliases)
        if not raw:
            continue
        rows.append(
            f'<div class="album-props-row">'
            f"<dt>{html_module.escape(label)}</dt>"
            f"<dd>{_format_cell(key, raw)}</dd>"
            f"</div>"
        )
    if not rows:
        return None
    return f'<dl class="album-props">{"".join(rows)}</dl>'


def enrich_restaurant_cards(
    notes: list[dict],
    *,
    root: Path,
    url_prefix: str,
) -> list[str]:
    """Добавляет note['tags']; возвращает отсортированный список всех тегов."""
    prefix = url_prefix.rstrip("/")
    all_tags: set[str] = set()
    for note in notes:
        url = str(note.get("url") or "")
        if not url.startswith(prefix + "/") and url != prefix:
            continue
        rel = url[len(prefix) :].lstrip("/")
        if not rel:
            continue
        path = root / f"{rel}.md"
        if not path.is_file():
            continue
        meta, _ = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        tags = parse_restaurant_tags(meta)
        note["tags"] = tags
        all_tags.update(tags)
    return sorted(all_tags, key=str.casefold)
