from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.feed.notes_feed import FeedSpec, iter_note_paths, note_url
from potyk_io_back.potyk_io.md_rendering import (
    demote_headings,
    extract_h1,
    html_text,
    main_inner_html,
    render_body_html,
    split_frontmatter,
)
from potyk_io_back.potyk_io.note_votes.entities import NoteVote

VOTE_LIKE = "like"
VOTE_DISLIKE = "dislike"
VALID_VOTES = frozenset({VOTE_LIKE, VOTE_DISLIKE})

SELF_TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates" / "potyk-self"

_SELF_SWIPE_SPEC = FeedSpec(
    id="self-swipe",
    root=SELF_TEMPLATES_DIR,
    url_prefix="/self",
    sort="random",
    recursive=True,
)


def _swipe_candidates() -> list[dict]:
    """Лёгкий список кандидатов без рендера HTML.

    Источник — заметки potyk-self (личные). Целый md-файл = одна заметка
    (дневник — весь день, без нарезки по ---).
    """
    entries: list[dict] = []
    for path in iter_note_paths(_SELF_SWIPE_SPEC):
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        url = note_url(path, root=SELF_TEMPLATES_DIR, url_prefix="/self")
        title = extract_h1(body) or path.stem
        if not body.strip() and not title:
            continue
        entries.append(
            {
                "id": url,
                "url": url,
                "title": title,
                "meta": meta,
                "body": body,
            }
        )
    return entries


def _render_swipe_note(entry: dict) -> dict | None:
    page_html = render_body_html(entry["body"], entry["meta"], title=entry["title"])
    html = demote_headings(main_inner_html(page_html), levels=1)
    if not html_text(html):
        return None
    return {
        "id": entry["id"],
        "url": entry["url"],
        "title": entry["title"],
        "html": html,
    }


def random_swipe_note(
    exclude: set[str] | frozenset[str] | None = None,
) -> dict | None:
    skip = set(exclude or ())
    pool = _swipe_candidates()
    unused = [e for e in pool if e["id"] not in skip]
    candidates = unused or pool
    if not candidates:
        return None

    random.shuffle(candidates)
    for entry in candidates:
        rendered = _render_swipe_note(entry)
        if rendered is not None:
            return rendered
    return None


def save_note_vote(
    *,
    note_id: str,
    note_url: str,
    title: str,
    vote: str,
) -> NoteVote:
    row = NoteVote(
        note_id=note_id[:512],
        note_url=note_url[:1024],
        title=(title or "")[:512],
        vote=vote,
        created_at=datetime.now(),
    )
    db.session.add(row)
    db.session.commit()
    return row


def list_note_votes() -> list[NoteVote]:
    return list(
        db.session.scalars(
            select(NoteVote).order_by(NoteVote.created_at.desc(), NoteVote.id.desc())
        ).all()
    )
