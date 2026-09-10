import json
import re

import sqlalchemy as sa
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.collections.movies import (
    Movie,
    MovieCollection,
    load_movies_data,
    movies_for_client,
)
from potyk_io_back.potyk_io.menu import CINEMA_MENU_GROUPS

cinema_bp = Blueprint("cinema", __name__, url_prefix="/cinema")


@cinema_bp.context_processor
def cinema_nav_context():
    return {
        "menu_groups": CINEMA_MENU_GROUPS,
        "section_brand_title": "potyk-cinema",
        "section_brand_url": "/cinema",
    }


def _parse_movie_ids(raw: str) -> list[str]:
    tokens = [t.strip() for t in raw.replace(",", " ").split()]
    seen: set[str] = set()
    result: list[str] = []
    for t in tokens:
        if not t or t in seen:
            continue
        seen.add(t)
        result.append(t)
    return result


def _collection_slug_from_title(title: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower(), flags=re.UNICODE)
    slug = re.sub(r"[-\s]+", "-", slug, flags=re.UNICODE).strip("-")
    return slug or "collection"


def _movie_id_from_kinopoisk(url: str) -> str | None:
    match = re.search(r"/film/(\d+)/?", url)
    return match.group(1) if match else None


def _parse_title_and_year(title: str, year_raw: str) -> tuple[str, int | None, str | None]:
    parsed_year: int | None = None
    match = re.match(r"^(.+?)\s*\((\d{4})\)\s*$", title.strip())
    if match:
        title = match.group(1).strip()
        parsed_year = int(match.group(2))

    year = parsed_year
    if year_raw:
        try:
            year = int(year_raw)
        except ValueError:
            return title, None, "Год должен быть числом"
    return title, year, None


@cinema_bp.get("/")
def index():
    page = load_movies_data()
    return render_template(
        "potyk-cinema/index.html",
        collections=page.collections,
        movies_by_collection_json=json.dumps(movies_for_client(page), ensure_ascii=False),
    )


@cinema_bp.get("/admin")
@login_required
def movies_admin():
    movies = db.session.scalars(select(Movie).order_by(Movie.id.asc())).all()
    collections = db.session.scalars(
        select(MovieCollection).order_by(MovieCollection.sort_order.asc(), MovieCollection.id.asc())
    ).all()
    movies_by_id = {movie.id: movie for movie in movies}
    collections_kanban = []
    for collection in collections:
        collection_movies = []
        for movie_id in collection.movie_ids or []:
            movie = movies_by_id.get(movie_id)
            if movie is None:
                continue
            collection_movies.append(
                {
                    "id": movie.id,
                    "title_ru": movie.title_ru,
                    "title_en": movie.title_en,
                    "year": movie.year,
                    "cover": movie.cover,
                    "kinopoisk": movie.kinopoisk,
                }
            )
        collections_kanban.append(
            {
                "id": collection.id,
                "title": collection.title,
                "movies": collection_movies,
            }
        )
    return render_template(
        "potyk-cinema/admin.html",
        movies=movies,
        collections=collections,
        collections_kanban_json=json.dumps(collections_kanban, ensure_ascii=False),
    )


@cinema_bp.post("/admin/movie")
@login_required
def movies_admin_add_movie():
    title_ru = (request.form.get("title_ru") or "").strip()
    title_en = (request.form.get("title_en") or "").strip() or None
    cover = (request.form.get("cover") or "").strip() or None
    kinopoisk = (request.form.get("kinopoisk") or "").strip()
    collection_id = (request.form.get("collection_id") or "").strip()
    year_raw = (request.form.get("year") or "").strip()

    title_ru, year, year_error = _parse_title_and_year(title_ru, year_raw)
    if year_error:
        flash(year_error, "error")
        return redirect(url_for("cinema.movies_admin"))

    if not title_ru:
        flash("Укажите `title_ru` фильма", "error")
        return redirect(url_for("cinema.movies_admin"))
    if not kinopoisk:
        flash("Укажите `kinopoisk` (URL)", "error")
        return redirect(url_for("cinema.movies_admin"))

    movie_id = _movie_id_from_kinopoisk(kinopoisk)
    if not movie_id:
        flash("Не удалось извлечь id фильма из Kinopoisk URL", "error")
        return redirect(url_for("cinema.movies_admin"))

    movie = db.session.get(Movie, movie_id)
    if movie is None:
        existing_by_kp = db.session.scalars(select(Movie).where(Movie.kinopoisk == kinopoisk)).first()
        if existing_by_kp is not None:
            movie = existing_by_kp
        else:
            movie = Movie(id=movie_id)
            db.session.add(movie)

    movie.title_ru = title_ru
    movie.title_en = title_en
    movie.year = year
    movie.cover = cover
    movie.kinopoisk = kinopoisk

    added_to_collection = False
    if collection_id:
        col = db.session.get(MovieCollection, collection_id)
        if col is None:
            flash("Коллекция не найдена", "error")
            return redirect(url_for("cinema.movies_admin"))

        movie_ids = list(col.movie_ids or [])
        if movie.id not in movie_ids:
            movie_ids.append(movie.id)
            col.movie_ids = movie_ids
            added_to_collection = True

    db.session.commit()
    if added_to_collection:
        flash("Фильм сохранён и добавлен в коллекцию", "success")
    else:
        flash("Фильм сохранён", "success")
    return redirect(url_for("cinema.movies_admin"))


@cinema_bp.post("/admin/collection")
@login_required
def movies_admin_create_collection():
    title = (request.form.get("title") or "").strip()
    youtube = (request.form.get("youtube") or "").strip() or None
    quote = (request.form.get("quote") or "").strip() or None
    movie_ids_raw = request.form.get("movie_ids") or ""
    movie_ids = _parse_movie_ids(movie_ids_raw)

    if not title:
        flash("Укажите `title` коллекции", "error")
        return redirect(url_for("cinema.movies_admin"))

    col_id = _collection_slug_from_title(title)

    if movie_ids:
        existing = set(db.session.scalars(select(Movie.id).where(Movie.id.in_(movie_ids))).all())
        missing = [mid for mid in movie_ids if mid not in existing]
        if missing:
            flash(f"Не найдено фильмов: {', '.join(missing[:10])}", "error")
            return redirect(url_for("cinema.movies_admin"))

    col = db.session.get(MovieCollection, col_id)
    if col is None:
        max_sort = db.session.scalar(select(sa.func.max(MovieCollection.sort_order)))
        col = MovieCollection(id=col_id, sort_order=(max_sort or 0) + 1)
        db.session.add(col)

    col.title = title
    col.youtube = youtube
    col.quote = quote
    col.movie_ids = movie_ids

    db.session.commit()
    flash("Коллекция сохранена", "success")
    return redirect(url_for("cinema.movies_admin"))


@cinema_bp.post("/admin/collection/add-movie")
@login_required
def movies_admin_add_movie_to_collection():
    col_id = (request.form.get("collection_id") or "").strip()
    movie_id = (request.form.get("movie_id") or "").strip()

    if not col_id or not movie_id:
        flash("Укажите `collection_id` и `movie_id`", "error")
        return redirect(url_for("cinema.movies_admin"))

    col = db.session.get(MovieCollection, col_id)
    if col is None:
        flash("Коллекция не найдена", "error")
        return redirect(url_for("cinema.movies_admin"))

    movie = db.session.get(Movie, movie_id)
    if movie is None:
        flash("Фильм не найден", "error")
        return redirect(url_for("cinema.movies_admin"))

    movie_ids = list(col.movie_ids or [])
    if movie_id not in movie_ids:
        movie_ids.append(movie_id)
        col.movie_ids = movie_ids

    db.session.commit()
    flash("Фильм добавлен в коллекцию", "success")
    return redirect(url_for("cinema.movies_admin"))


@cinema_bp.post("/admin/collection/move-movie")
@login_required
def movies_admin_move_movie_between_collections():
    payload = request.get_json(silent=True) or {}
    source_id = str(payload.get("sourceCollectionId") or "").strip()
    target_id = str(payload.get("targetCollectionId") or "").strip()
    movie_id = str(payload.get("movieId") or "").strip()

    if not source_id or not target_id or not movie_id:
        return jsonify({"ok": False, "error": "missing fields"}), 400
    if source_id == target_id:
        return jsonify({"ok": True}), 200

    source = db.session.get(MovieCollection, source_id)
    target = db.session.get(MovieCollection, target_id)
    movie = db.session.get(Movie, movie_id)

    if source is None or target is None or movie is None:
        return jsonify({"ok": False, "error": "not found"}), 404

    source_movie_ids = list(source.movie_ids or [])
    target_movie_ids = list(target.movie_ids or [])

    if movie_id not in source_movie_ids:
        return jsonify({"ok": False, "error": "movie not in source"}), 400

    source.movie_ids = [mid for mid in source_movie_ids if mid != movie_id]
    if movie_id not in target_movie_ids:
        target_movie_ids.append(movie_id)
    target.movie_ids = target_movie_ids

    db.session.commit()
    return jsonify({"ok": True})


@cinema_bp.post("/admin/movie/delete")
@login_required
def movies_admin_delete_movie():
    payload = request.get_json(silent=True) or {}
    movie_id = str(payload.get("movieId") or "").strip()
    collection_id = str(payload.get("collectionId") or "").strip()

    if not movie_id or not collection_id:
        return jsonify({"ok": False, "error": "missing fields"}), 400

    collection = db.session.get(MovieCollection, collection_id)
    movie = db.session.get(Movie, movie_id)
    if collection is None or movie is None:
        return jsonify({"ok": False, "error": "not found"}), 404

    movie_ids = list(collection.movie_ids or [])
    if movie_id not in movie_ids:
        return jsonify({"ok": False, "error": "movie not in collection"}), 400

    collection.movie_ids = [mid for mid in movie_ids if mid != movie_id]
    db.session.commit()
    return jsonify({"ok": True})
