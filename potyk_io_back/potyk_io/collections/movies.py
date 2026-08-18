"""Загрузка кино-подборок из YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

COLLECTIONS_DIR = Path(__file__).resolve().parents[3] / "templates" / "potyk-io" / "collections"
MOVIES_YAML = COLLECTIONS_DIR / "movies.yaml"


@dataclass
class Movie:
    id: str
    title_ru: str
    title_en: str | None = None
    year: int | None = None
    cover: str | None = None
    kinopoisk: str = ""
    watched: bool = False


@dataclass
class WatchLaterItem:
    title: str
    kinopoisk: str | None = None


@dataclass
class Collection:
    id: str
    title: str
    movies: list[Movie] = field(default_factory=list)
    youtube: str | None = None
    quote: str | None = None
    watch_later: list[WatchLaterItem | str] = field(default_factory=list)


@dataclass
class MoviesPage:
    created: date | None
    collections: list[Collection]
    watch_later: list[Movie]


def _parse_movie(raw: dict) -> Movie:
    year = raw.get("year")
    return Movie(
        id=str(raw["id"]),
        title_ru=str(raw["title_ru"]),
        title_en=raw.get("title_en") or None,
        year=int(year) if year is not None else None,
        cover=raw.get("cover") or None,
        kinopoisk=str(raw.get("kinopoisk", "")),
        watched=bool(raw.get("watched", False)),
    )


def _parse_watch_later(raw) -> WatchLaterItem | str:
    if isinstance(raw, str):
        return raw
    return WatchLaterItem(
        title=str(raw.get("title", "")),
        kinopoisk=raw.get("kinopoisk") or None,
    )


def _parse_collection(raw: dict) -> Collection:
    return Collection(
        id=str(raw["id"]),
        title=str(raw["title"]),
        movies=[_parse_movie(m) for m in raw.get("movies", [])],
        youtube=raw.get("youtube") or None,
        quote=raw.get("quote") or None,
        watch_later=[_parse_watch_later(w) for w in raw.get("watch_later", [])],
    )


def load_movies_data() -> MoviesPage:
    text = MOVIES_YAML.read_text(encoding="utf-8-sig")
    data = yaml.safe_load(text) or {}
    created_raw = data.get("created")
    created = date.fromisoformat(str(created_raw)) if created_raw else None
    collections = [_parse_collection(c) for c in data.get("collections", [])]
    watch_later = [_parse_movie(m) for m in data.get("watch_later", [])]
    return MoviesPage(created=created, collections=collections, watch_later=watch_later)


def movies_for_client(page: MoviesPage) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []
    for movie in [*page.watch_later, *(m for col in page.collections for m in col.movies)]:
        if movie.id in seen:
            continue
        seen.add(movie.id)
        result.append(
            {
                "id": movie.id,
                "title_ru": movie.title_ru,
                "title_en": movie.title_en,
                "year": movie.year,
                "cover": movie.cover,
                "kinopoisk": movie.kinopoisk,
                "watched": movie.watched,
            }
        )
    return result
