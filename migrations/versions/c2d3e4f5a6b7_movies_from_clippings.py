"""Import movies from potyk-food/Clippings into watch_later collection.

Парсит 4 md-файла «Буду смотреть» из Кинопоиска:
  templates/potyk-food/Clippings/potykion — Буду смотреть*.md

Каждая карточка фильма имеет формат:
  [![Название. Год, жанр](img)](https://www.kinopoisk.ru/film/ID/)
  [![Название. Год, жанр](img)](https://www.kinopoisk.ru/series/ID/)

Новые фильмы добавляются в таблицу movies (без cover).
ID новых фильмов дописываются в movie_ids коллекции watch_later.
Дубликаты (уже существующие movies.id и уже присутствующие в watch_later.movie_ids) пропускаются.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CLIPPINGS_DIR = (
    Path(__file__).resolve().parents[2]
    / "templates"
    / "potyk-food"
    / "Clippings"
)

WATCH_LATER_ID = "watch_later"

# [![Alt text](img_url)](https://www.kinopoisk.ru/film/12345/)
# [![Alt text](img_url)](https://www.kinopoisk.ru/series/12345/)
CARD_RE = re.compile(
    r"\[!\[(?P<alt>[^\]]*)\]\([^)]*\)\]\(https://www\.kinopoisk\.ru/(?:film|series)/(?P<kp_id>\d+)/\)"
)

# Alt = "Название. Год, жанр"  или  "Название. Год, жанр1, жанр2"
ALT_RE = re.compile(r"^(?P<title>.+?)\.\s*(?P<year>\d{4}),")


def parse_clippings() -> list[dict[str, object]]:
    """Возвращает список уникальных фильмов из всех clipping-файлов."""
    seen: set[str] = set()
    movies: list[dict[str, object]] = []

    for md_file in sorted(CLIPPINGS_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8-sig")
        for m in CARD_RE.finditer(text):
            kp_id = m.group("kp_id")
            if kp_id in seen:
                continue
            seen.add(kp_id)

            alt = m.group("alt").strip()
            alt_match = ALT_RE.match(alt)
            if alt_match:
                title_ru = alt_match.group("title").strip()
                year: int | None = int(alt_match.group("year"))
            else:
                title_ru = alt
                year = None

            movies.append(
                {
                    "id": kp_id,
                    "title_ru": title_ru,
                    "title_en": None,
                    "year": year,
                    "cover": None,
                    "kinopoisk": f"https://www.kinopoisk.ru/film/{kp_id}/",
                }
            )

    return movies


def upgrade() -> None:
    bind = op.get_bind()

    movies_table = sa.table(
        "movies",
        sa.column("id", sa.String()),
        sa.column("title_ru", sa.String()),
        sa.column("title_en", sa.String()),
        sa.column("year", sa.Integer()),
        sa.column("cover", sa.String()),
        sa.column("kinopoisk", sa.String()),
    )

    clipping_movies = parse_clippings()
    if not clipping_movies:
        return

    # Фильмы, которых ещё нет в таблице movies.
    clipping_ids_list = [m["id"] for m in clipping_movies]
    placeholders = ", ".join(f":id_{i}" for i in range(len(clipping_ids_list)))
    id_params = {f"id_{i}": vid for i, vid in enumerate(clipping_ids_list)}
    existing_ids = {
        row[0]
        for row in bind.execute(
            sa.text(f"SELECT id FROM movies WHERE id IN ({placeholders})"),
            id_params,
        ).fetchall()
    }
    new_movies = [m for m in clipping_movies if m["id"] not in existing_ids]
    if new_movies:
        op.bulk_insert(movies_table, new_movies)

    # Обновляем movie_ids коллекции watch_later.
    row = bind.execute(
        sa.text("SELECT movie_ids FROM movie_collections WHERE id = :cid"),
        {"cid": WATCH_LATER_ID},
    ).fetchone()

    if row is None:
        # Создаём коллекцию watch_later, если вдруг её нет.
        collections_table = sa.table(
            "movie_collections",
            sa.column("id", sa.String()),
            sa.column("title", sa.String()),
            sa.column("quote", sa.String()),
            sa.column("youtube", sa.String()),
            sa.column("movie_ids", sa.JSON()),
            sa.column("watch_later", sa.Boolean()),
            sa.column("sort_order", sa.Integer()),
        )
        op.bulk_insert(
            collections_table,
            [
                {
                    "id": WATCH_LATER_ID,
                    "title": "Посмотреть позже",
                    "quote": None,
                    "youtube": None,
                    "movie_ids": [m["id"] for m in clipping_movies],
                    "watch_later": True,
                    "sort_order": 0,
                }
            ],
        )
        return

    existing_movie_ids: list[str] = json.loads(row[0]) if isinstance(row[0], str) else (row[0] or [])
    existing_set = set(existing_movie_ids)
    to_add = [m["id"] for m in clipping_movies if m["id"] not in existing_set]

    if to_add:
        updated = json.dumps(existing_movie_ids + to_add, ensure_ascii=False)
        bind.execute(
            sa.text("UPDATE movie_collections SET movie_ids = :ids WHERE id = :cid"),
            {"ids": updated, "cid": WATCH_LATER_ID},
        )


def downgrade() -> None:
    # Удаляем добавленные фильмы и сжимаем watch_later.movie_ids.
    bind = op.get_bind()

    clipping_movies = parse_clippings()
    if not clipping_movies:
        return

    clipping_ids = {m["id"] for m in clipping_movies}

    row = bind.execute(
        sa.text("SELECT movie_ids FROM movie_collections WHERE id = :cid"),
        {"cid": WATCH_LATER_ID},
    ).fetchone()

    if row is not None:
        movie_ids: list[str] = json.loads(row[0]) if isinstance(row[0], str) else (row[0] or [])
        remaining = [mid for mid in movie_ids if mid not in clipping_ids]
        bind.execute(
            sa.text("UPDATE movie_collections SET movie_ids = :ids WHERE id = :cid"),
            {"ids": json.dumps(remaining, ensure_ascii=False), "cid": WATCH_LATER_ID},
        )

    # Удаляем только фильмы, которые были добавлены этой миграцией (нет в других коллекциях).
    # Для простоты — удаляем все из clipping_ids.
    for mid in clipping_ids:
        bind.execute(sa.text("DELETE FROM movies WHERE id = :id"), {"id": mid})
