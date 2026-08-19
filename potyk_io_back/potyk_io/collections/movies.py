"""Кино-коллекции и рулетка: данные в SQL (2 таблицы)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from potyk_io_back.core.db import db

COLLECTIONS_DIR = Path(__file__).resolve().parents[3] / "templates" / "potyk-io" / "collections"
MOVIES_YAML = COLLECTIONS_DIR / "movies.yaml"


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.String(64), primary_key=True)
    title_ru = db.Column(db.String(255), nullable=False)
    title_en = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=True, index=True)
    cover = db.Column(db.String(512), nullable=True)
    kinopoisk = db.Column(db.String(512), nullable=False, default="", unique=True)


class MovieCollection(db.Model):
    __tablename__ = "movie_collections"

    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    quote = db.Column(db.Text, nullable=True)
    youtube = db.Column(db.Text, nullable=True)
    movie_ids = db.Column(db.JSON, nullable=False, default=list)
    sort_order = db.Column(db.Integer, nullable=False, default=0, index=True)


@dataclass
class MovieView:
    id: str
    title_ru: str
    title_en: str | None = None
    year: int | None = None
    cover: str | None = None
    kinopoisk: str = ""


@dataclass
class CollectionView:
    id: str
    title: str
    movies: list[MovieView] = field(default_factory=list)
    youtube: str | None = None
    quote: str | None = None


@dataclass
class MoviesPage:
    collections: list[CollectionView]


def _parse_movie_from_yaml(raw: dict) -> MovieView:
    year = raw.get("year")
    return MovieView(
        id=str(raw["id"]),
        title_ru=str(raw["title_ru"]),
        title_en=raw.get("title_en") or None,
        year=int(year) if year is not None else None,
        cover=raw.get("cover") or None,
        kinopoisk=str(raw.get("kinopoisk", "")),
    )


def _seed_from_yaml_if_needed() -> None:
    # Идемпотентная подстановка: если таблицы уже заполнены миграцией — ничего не делаем.
    if Movie.query.first() is not None:
        return

    if not MOVIES_YAML.exists():
        return

    text = MOVIES_YAML.read_text(encoding="utf-8-sig")
    data = yaml.safe_load(text) or {}

    collections_raw = data.get("collections", []) or []

    movies_by_id: dict[str, MovieView] = {}

    def add_movie(raw_movie: dict) -> None:
        movie = _parse_movie_from_yaml(raw_movie)
        movies_by_id.setdefault(movie.id, movie)

    collection_rows: list[dict] = []
    raw_watch_later = data.get("watch_later", []) or []
    if raw_watch_later:
        collections_raw = [
            {
                "id": "watch_later",
                "title": "Посмотреть позже",
                "movies": raw_watch_later,
            },
            *collections_raw,
        ]

    for idx, raw_col in enumerate(collections_raw):
        col_id = str(raw_col["id"])
        movie_ids: list[str] = []
        for raw_movie in raw_col.get("movies", []) or []:
            add_movie(raw_movie)
            movie_ids.append(str(raw_movie["id"]))

        collection_rows.append(
            dict(
                id=col_id,
                title=str(raw_col["title"]),
                quote=raw_col.get("quote") or None,
                youtube=raw_col.get("youtube") or None,
                movie_ids=movie_ids,
                sort_order=idx,
            )
        )

    # Перезаполняем только при первом заполнении (если Movie пустая).
    db.session.query(MovieCollection).delete()
    db.session.query(Movie).delete()

    db.session.bulk_insert_mappings(
        Movie.__table__,
        [m.__dict__ for m in movies_by_id.values()],
    )

    db.session.bulk_insert_mappings(MovieCollection.__table__, collection_rows)
    db.session.commit()


def _ordered_movies_by_ids(movie_ids: list[str]) -> list[MovieView]:
    if not movie_ids:
        return []
    rows = Movie.query.filter(Movie.id.in_(movie_ids)).all()
    by_id = {r.id: r for r in rows}
    result: list[MovieView] = []
    for mid in movie_ids:
        row = by_id.get(mid)
        if row is None:
            continue
        result.append(
            MovieView(
                id=row.id,
                title_ru=row.title_ru,
                title_en=row.title_en,
                year=row.year,
                cover=row.cover,
                kinopoisk=row.kinopoisk,
            )
        )
    return result


def load_movies_data() -> MoviesPage:
    _seed_from_yaml_if_needed()
    collections_rows = MovieCollection.query.order_by(MovieCollection.sort_order.asc(), MovieCollection.id.asc())

    collections: list[CollectionView] = []
    for col in collections_rows:
        collections.append(
            CollectionView(
                id=col.id,
                title=col.title,
                movies=_ordered_movies_by_ids((col.movie_ids if col.movie_ids else []) or []),
                youtube=col.youtube,
                quote=col.quote,
            )
        )
    return MoviesPage(collections=collections)


def movies_for_client(page: MoviesPage) -> dict:
    def movie_to_dict(m: MovieView) -> dict:
        return {
            "id": m.id,
            "title_ru": m.title_ru,
            "title_en": m.title_en,
            "year": m.year,
            "cover": m.cover,
            "kinopoisk": m.kinopoisk,
        }

    movies_by_collection: dict[str, list[dict]] = {}
    for col in page.collections:
        movies_by_collection[col.id] = [movie_to_dict(m) for m in col.movies]

    return {
        "defaultCollectionId": page.collections[0].id if page.collections else "",
        "moviesByCollection": movies_by_collection,
    }
