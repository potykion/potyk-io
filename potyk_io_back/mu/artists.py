"""Исполнители potyk-mu: slug, привязка альбомов к странице артиста."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from potyk_io_back.potyk_io.feed.notes_feed import FeedSpec, iter_note_paths, note_url
from potyk_io_back.potyk_io.feed.random_notes import note_card_html, note_cover
from potyk_io_back.potyk_io.md_rendering import split_frontmatter, unquote_meta

_ARTIST_SLUG_RE = re.compile(r"[^\w\s-]", flags=re.UNICODE)
_ARTIST_SLUG_SPACES_RE = re.compile(r"[-\s]+", flags=re.UNICODE)


def artist_slug(name: str) -> str:
    slug = _ARTIST_SLUG_RE.sub("", name.lower())
    slug = _ARTIST_SLUG_SPACES_RE.sub("-", slug).strip("-")
    return slug


def is_artist_page(file: Path, *, artists_dir: Path) -> bool:
    try:
        rel = file.relative_to(artists_dir)
    except ValueError:
        return False
    return file.suffix == ".md" and rel.stem != "index"


def _resolve_artist_link(album_file: Path, link: str) -> Path | None:
    raw = unquote_meta(link).strip()
    if not raw:
        return None
    target = PurePosixPath(raw)
    if target.is_absolute():
        return None
    resolved = (album_file.parent / target).resolve()
    return resolved if resolved.is_file() else None


def album_belongs_to_artist(
    album_file: Path,
    meta: dict[str, str],
    *,
    artist_file: Path,
) -> bool:
    artist_stem = artist_file.stem
    linked = _resolve_artist_link(album_file, meta.get("artist-link", ""))
    if linked is not None:
        return linked.resolve() == artist_file.resolve()

    artist_name = unquote_meta(meta.get("artist", ""))
    if artist_name:
        return artist_slug(artist_name) == artist_stem
    return False


def _album_sort_date(meta: dict[str, str]) -> str:
    for key in ("listened", "year"):
        value = unquote_meta(meta.get(key, ""))
        if value:
            return value
    return ""


def albums_for_artist(artist_file: Path, *, albums_spec: FeedSpec) -> list[dict]:
    cards: list[dict] = []
    for path in iter_note_paths(albums_spec):
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        if not album_belongs_to_artist(path, meta, artist_file=artist_file):
            continue
        preview = note_card_html(path, meta=meta, body=body)
        if not preview:
            continue
        card: dict = {
            "url": note_url(path, root=albums_spec.root, url_prefix=albums_spec.url_prefix),
            "preview": preview,
            "name": path.name,
            "kind": "note",
            "external": False,
            "_sort_key": _album_sort_date(meta),
        }
        cover = note_cover(meta)
        if cover:
            card["cover"] = cover
        cards.append(card)

    return sorted(cards, key=lambda c: c.get("_sort_key") or "", reverse=True)
