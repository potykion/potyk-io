"""Переиспользуемая лента markdown-карточек."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from potyk_io_back.potyk_io.feed.random_notes import (
    BATCH_SIZE,
    HIDDEN_NOTE_DIRS,
    HIDDEN_NOTE_STEMS,
    PREVIEW_LEN,
    card_id,
    is_diary_note,
    menu_link_cards,
    note_card_html,
    note_cover,
    split_diary_entries,
)
from potyk_io_back.potyk_io.md_rendering import TEMPLATES_DIR, split_frontmatter
from potyk_io_back.potyk_io.md_rendering.created import (
    created_from_filename,
    created_from_meta,
)

SortMode = Literal["random", "date_desc", "date_asc", "name"]


@dataclass(frozen=True)
class FeedSpec:
    """Описание одной ленты: откуда брать страницы и как упорядочивать."""

    id: str
    root: Path
    url_prefix: str
    sort: SortMode = "date_desc"
    recursive: bool = True
    mix_menu_links: bool = False
    expand_diary: bool = False
    hidden_dirs: frozenset[str] = frozenset(HIDDEN_NOTE_DIRS)
    hidden_stems: frozenset[str] = frozenset(HIDDEN_NOTE_STEMS)


def note_url(path: Path, *, root: Path, url_prefix: str) -> str:
    rel = path.relative_to(root).with_suffix("").as_posix()
    if rel.endswith("/index"):
        rel = rel[: -len("/index")]
    prefix = url_prefix.rstrip("/")
    if not rel or rel == ".":
        return prefix or "/"
    return f"{prefix}/{rel}" if prefix else f"/{rel}"


def iter_note_paths(spec: FeedSpec) -> list[Path]:
    root = spec.root
    if not root.is_dir():
        return []
    paths = root.rglob("*.md") if spec.recursive else root.glob("*.md")
    notes: list[Path] = []
    for path in paths:
        try:
            rel_parts = path.relative_to(root).parts
        except ValueError:
            continue
        if any(part.startswith(".") or part.startswith("_") for part in path.parts):
            continue
        if path.name.startswith(".") or path.name.startswith("_"):
            continue
        if path.name == "index.md":
            continue
        if any(part in spec.hidden_dirs for part in rel_parts):
            continue
        if path.stem in spec.hidden_stems:
            continue
        notes.append(path)
    return notes


def _sort_date(path: Path, meta: dict[str, str]) -> date | None:
    return created_from_meta(meta) or created_from_filename(path.stem)


def _expand_entries(
    path: Path, spec: FeedSpec
) -> list[tuple[str, str, dict[str, str], str]]:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
    base_url = note_url(path, root=spec.root, url_prefix=spec.url_prefix)

    if not spec.expand_diary:
        return [(base_url, base_url, meta, body)]

    try:
        path.relative_to(TEMPLATES_DIR)
    except ValueError:
        return [(base_url, base_url, meta, body)]

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


def list_feed_cards(spec: FeedSpec, *, limit: int = PREVIEW_LEN) -> list[dict]:
    result: list[dict] = []
    for path in iter_note_paths(spec):
        for cid, url, meta, body in _expand_entries(path, spec):
            preview = note_card_html(path, limit, meta=meta, body=body)
            if not preview:
                continue
            card: dict = {
                "id": cid,
                "url": url,
                "preview": preview,
                "name": path.name,
                "kind": "note",
                "external": False,
                "_sort_date": _sort_date(path, meta),
            }
            cover = note_cover(meta)
            if cover:
                card["cover"] = cover
            result.append(card)
    return result


def _ordered_cards(spec: FeedSpec, cards: list[dict]) -> list[dict]:
    if spec.sort == "random":
        shuffled = list(cards)
        random.shuffle(shuffled)
        return shuffled
    if spec.sort == "date_desc":
        return sorted(
            cards,
            key=lambda c: c.get("_sort_date") or date.min,
            reverse=True,
        )
    if spec.sort == "date_asc":
        return sorted(
            cards,
            key=lambda c: c.get("_sort_date") or date.max,
        )
    if spec.sort == "name":
        return sorted(cards, key=lambda c: (c.get("name") or "").lower())
    return list(cards)


def _public_card(card: dict) -> dict:
    return {k: v for k, v in card.items() if not k.startswith("_")}


def feed_batch(
    spec: FeedSpec,
    count: int = BATCH_SIZE,
    *,
    limit: int = PREVIEW_LEN,
    exclude: set[str] | frozenset[str] | None = None,
) -> tuple[list[dict], bool]:
    skip = set(exclude or ())
    notes = [
        c
        for c in _ordered_cards(spec, list_feed_cards(spec, limit=limit))
        if card_id(c) not in skip
    ]

    if spec.sort == "random" and spec.mix_menu_links:
        for note in notes:
            note.setdefault("kind", "note")
            note.setdefault("external", False)
        links = menu_link_cards(exclude=skip)
        random.shuffle(links)
        link_budget = max(1, (count + 1) // 2) if links else 0
        pool = notes + links[:link_budget]
        random.shuffle(pool)
        batch = [_public_card(item) for item in pool[:count]]
        used = {card_id(item) for item in batch}
        has_more = any(card_id(n) not in used for n in notes) or any(
            card_id(link) not in used for link in links
        )
        return batch, has_more

    batch = [_public_card(c) for c in notes[:count]]
    has_more = len(notes) > count
    return batch, has_more


def feed_more_url(feed_id: str, *, endpoint: str) -> str:
    sep = "&" if "?" in endpoint else "?"
    return f"{endpoint}{sep}feed={feed_id}"
