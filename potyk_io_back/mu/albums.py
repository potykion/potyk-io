"""Страницы альбомов potyk-mu: свойства из frontmatter."""

from __future__ import annotations

import html as html_module
from collections.abc import Callable
from pathlib import Path

from potyk_io_back.potyk_io.md_rendering import unquote_meta
from potyk_io_back.potyk_io.md_rendering.created import format_created_ru, parse_iso_date

_ALBUM_FIELDS: tuple[tuple[str, str], ...] = (
    ("artist", "Исполнитель"),
    ("album", "Альбом"),
    ("year", "Год"),
    ("listened", "Прослушано"),
    ("rate", "Оценка"),
    ("yandex", "Яндекс.Музыка"),
    ("rym", "RYM"),
)


def is_album_page(file: Path, *, albums_dir: Path) -> bool:
    try:
        rel = file.relative_to(albums_dir)
    except ValueError:
        return False
    return file.suffix == ".md" and rel.stem != "index"


def _format_value(key: str, raw: str) -> str:
    if key == "listened":
        parsed = parse_iso_date(raw)
        if parsed:
            return format_created_ru(parsed)
    return raw


def _format_cell(
    key: str,
    raw: str,
    *,
    meta: dict[str, str],
    link_rewriter: Callable[[str], str | None] | None,
) -> str:
    if key == "artist" and link_rewriter is not None:
        link_raw = unquote_meta(meta.get("artist-link", ""))
        if link_raw:
            href = link_rewriter(link_raw)
            if href:
                return (
                    f'<a href="{html_module.escape(href)}">'
                    f"{html_module.escape(raw)}</a>"
                )

    if key == "yandex":
        return (
            f'<a href="{html_module.escape(raw)}" target="_blank" rel="noopener">'
            "Слушать</a>"
        )

    if key == "rym":
        return (
            f'<a href="{html_module.escape(raw)}" target="_blank" rel="noopener">'
            "Открыть</a>"
        )

    return html_module.escape(_format_value(key, raw))


def album_props_html(
    meta: dict[str, str],
    *,
    link_rewriter: Callable[[str], str | None] | None = None,
) -> str | None:
    rows: list[str] = []
    for key, label in _ALBUM_FIELDS:
        raw = unquote_meta(meta.get(key, ""))
        if not raw:
            continue
        cell = _format_cell(key, raw, meta=meta, link_rewriter=link_rewriter)
        rows.append(
            f'<div class="album-props-row">'
            f"<dt>{html_module.escape(label)}</dt>"
            f"<dd>{cell}</dd>"
            f"</div>"
        )

    if not rows:
        return None
    return f'<dl class="album-props">{"".join(rows)}</dl>'
