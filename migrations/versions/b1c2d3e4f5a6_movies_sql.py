"""movies and collections (SQL instead of YAML)."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
import yaml
from alembic import op

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "0a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

WATCH_LATER_COLLECTION_ID = "watch_later"
WATCH_LATER_COLLECTION_TITLE = "Посмотреть позже"

MOVIES_YAML = (
    Path(__file__).resolve().parents[2]
    / "templates"
    / "potyk-io"
    / "collections"
    / "movies.yaml"
)


def parse_movie(raw: dict) -> dict[str, object]:
    year = raw.get("year")
    return {
        "id": str(raw["id"]),
        "title_ru": str(raw["title_ru"]),
        "title_en": raw.get("title_en") or None,
        "year": int(year) if year is not None else None,
        "cover": raw.get("cover") or None,
        "kinopoisk": str(raw.get("kinopoisk", "")),
    }


def load_seed_data() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    text = MOVIES_YAML.read_text(encoding="utf-8-sig")
    data = yaml.safe_load(text) or {}

    watch_later_raw = data.get("watch_later", []) or []
    collections_raw = data.get("collections", []) or []

    movies_by_id: dict[str, dict[str, object]] = {}

    def add_movie(raw_movie: dict) -> None:
        movie = parse_movie(raw_movie)
        movies_by_id.setdefault(movie["id"], movie)

    movie_ids_watch_later: list[str] = []
    for raw_movie in watch_later_raw:
        add_movie(raw_movie)
        movie_ids_watch_later.append(str(raw_movie["id"]))

    collection_rows: list[dict[str, object]] = []
    for idx, raw_col in enumerate(collections_raw):
        movie_ids: list[str] = []
        for raw_movie in raw_col.get("movies", []) or []:
            add_movie(raw_movie)
            movie_ids.append(str(raw_movie["id"]))

        collection_rows.append(
            {
                "id": str(raw_col["id"]),
                "title": str(raw_col["title"]),
                "quote": raw_col.get("quote") or None,
                "youtube": raw_col.get("youtube") or None,
                "movie_ids": movie_ids,
                "watch_later": False,
                "sort_order": idx,
            }
        )

    watch_later_row = {
        "id": WATCH_LATER_COLLECTION_ID,
        "title": WATCH_LATER_COLLECTION_TITLE,
        "quote": None,
        "youtube": None,
        "movie_ids": movie_ids_watch_later,
        "watch_later": True,
        "sort_order": 0,
    }

    movies_rows = list(movies_by_id.values())
    return movies_rows, [watch_later_row, *collection_rows]


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    movies_table = sa.table(
        "movies",
        sa.column("id", sa.String(length=64)),
        sa.column("title_ru", sa.String(length=255)),
        sa.column("title_en", sa.String(length=255)),
        sa.column("year", sa.Integer()),
        sa.column("cover", sa.String(length=512)),
        sa.column("kinopoisk", sa.String(length=512)),
    )

    collections_table = sa.table(
        "movie_collections",
        sa.column("id", sa.String(length=64)),
        sa.column("title", sa.String(length=255)),
        sa.column("quote", sa.Text()),
        sa.column("youtube", sa.Text()),
        sa.column("movie_ids", sa.JSON()),
        sa.column("watch_later", sa.Boolean()),
        sa.column("sort_order", sa.Integer()),
    )

    movies_exists = insp.has_table("movies")
    collections_exists = insp.has_table("movie_collections")

    if not movies_exists:
        op.create_table(
            "movies",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("title_ru", sa.String(length=255), nullable=False),
            sa.Column("title_en", sa.String(length=255), nullable=True),
            sa.Column("year", sa.Integer(), nullable=True),
            sa.Column("cover", sa.String(length=512), nullable=True),
            sa.Column("kinopoisk", sa.String(length=512), nullable=False, server_default=""),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_movies_year"), "movies", ["year"], unique=False)

    if not collections_exists:
        op.create_table(
            "movie_collections",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("quote", sa.Text(), nullable=True),
            sa.Column("youtube", sa.Text(), nullable=True),
            sa.Column("movie_ids", sa.JSON(), nullable=False, server_default="[]"),
            sa.Column(
                "watch_later",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "sort_order",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_movie_collections_watch_later"),
            "movie_collections",
            ["watch_later"],
            unique=False,
        )
        op.create_index(
            op.f("ix_movie_collections_sort_order"),
            "movie_collections",
            ["sort_order"],
            unique=False,
        )

    movies_rows, collections_rows = load_seed_data()

    if movies_rows:
        op.execute(sa.text("DELETE FROM movie_collections"))
        op.execute(sa.text("DELETE FROM movies"))
        op.bulk_insert(movies_table, movies_rows)
        op.bulk_insert(collections_table, collections_rows)


def downgrade() -> None:
    op.drop_index(op.f("ix_movie_collections_sort_order"), table_name="movie_collections")
    op.drop_index(op.f("ix_movie_collections_watch_later"), table_name="movie_collections")
    op.drop_table("movie_collections")

    op.drop_index(op.f("ix_movies_year"), table_name="movies")
    op.drop_table("movies")

