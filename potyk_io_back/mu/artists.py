"""Исполнители potyk-mu: slug, привязка альбомов к странице артиста."""

from __future__ import annotations

import html
import re
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, urlparse

from potyk_io_back.potyk_io.feed.notes_feed import FeedSpec, iter_note_paths, note_url
from potyk_io_back.potyk_io.feed.random_notes import apply_cover, note_card_html
from potyk_io_back.potyk_io.md_rendering import split_frontmatter, unquote_meta

_ARTIST_SLUG_RE = re.compile(r"[^\w\s-]", flags=re.UNICODE)
_ARTIST_SLUG_SPACES_RE = re.compile(r"[-\s]+", flags=re.UNICODE)
_VIDEOS_SECTION_RE = re.compile(
    r"(?ms)^##\s+Videos\s*\n(.*?)(?=^##\s|\Z)",
)
_VIDEO_LINK_RE = re.compile(
    r"^\s*[-*]\s*\[([^\]]+)\]\(([^)]+)\)\s*$",
)
_VIDEO_DATE_TITLE_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s*:\s*(.+)$",
)
_YOUTUBE_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?.*?v=|embed/|shorts/|live/))([A-Za-z0-9_-]{11})",
)


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
        apply_cover(card, meta)
        cards.append(card)

    return sorted(cards, key=lambda c: c.get("_sort_key") or "", reverse=True)


def youtube_video_id(url: str) -> str | None:
    match = _YOUTUBE_ID_RE.search(url)
    if match:
        return match.group(1)
    parsed = urlparse(url)
    if "youtube.com" in (parsed.hostname or "").lower():
        vids = parse_qs(parsed.query).get("v")
        if vids and re.fullmatch(r"[A-Za-z0-9_-]{11}", vids[0]):
            return vids[0]
    return None


def youtube_hq_cover(url: str) -> str | None:
    video_id = youtube_video_id(url)
    if not video_id:
        return None
    return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"


def extract_artist_videos(body: str) -> tuple[str, list[dict]]:
    """Вырезать секцию ## Videos из тела и собрать карточки для сетки."""
    match = _VIDEOS_SECTION_RE.search(body)
    if not match:
        return body, []

    cards: list[dict] = []
    for line in match.group(1).splitlines():
        link = _VIDEO_LINK_RE.match(line)
        if not link:
            continue
        label, url = link.group(1).strip(), link.group(2).strip()
        if not url:
            continue
        dated = _VIDEO_DATE_TITLE_RE.match(label)
        if dated:
            subtitle, title = dated.group(1), dated.group(2).strip()
        else:
            title, subtitle = label, ""
        preview = f"<h3>{html.escape(title)}</h3>"
        if subtitle:
            preview += f'\n<p class="card-subtitle">{html.escape(subtitle)}</p>'
        card: dict = {
            "url": url,
            "preview": preview,
            "name": title,
            "kind": "note",
            "external": True,
            "_sort_key": subtitle,
        }
        cover = youtube_hq_cover(url)
        if cover:
            card["cover"] = cover
        cards.append(card)

    cards.sort(key=lambda c: c.get("_sort_key") or "", reverse=True)
    cleaned = (body[: match.start()] + body[match.end() :]).strip() + "\n"
    return cleaned, cards
