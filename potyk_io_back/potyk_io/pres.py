import json
import re
from pathlib import Path, PurePosixPath

import flask
from flask import Blueprint, abort, flash, jsonify, redirect, request, render_template, send_file, url_for
from flask_login import login_required
import sqlalchemy as sa
from sqlalchemy import select

from potyk_io_back.potyk_io.collections.movies import (
    Movie,
    MovieCollection,
    load_movies_data,
    movies_for_client,
)
from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.feed import BATCH_SIZE, random_note_batch, search_notes
from potyk_io_back.potyk_io.md_rendering import (
    FOOD_TEMPLATES_DIR,
    TEMPLATES_DIR,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.menu import FOOD_MENU_GROUPS, MENU_GROUPS

potyk_io_bp = Blueprint("potyk_io", __name__)


@potyk_io_bp.context_processor
def inject_menu():
    is_food = request.path.startswith("/food")
    menu_groups = FOOD_MENU_GROUPS if is_food else MENU_GROUPS
    return {
        "menu_groups": menu_groups,
        "section_brand_title": "potyk-food" if is_food else "potyk.io",
        "section_brand_url": "/food" if is_food else "/",
    }


def food_page_url(path: PurePosixPath) -> str:
    if path.name == "index.md":
        parent = path.parent.as_posix()
        return "/food" if parent == "." else f"/food/{parent}"
    return f"/food/{path.with_suffix('').as_posix()}"


def make_food_link_rewriter(file: Path):
    root = FOOD_TEMPLATES_DIR.resolve()
    current_dir = file.parent.resolve()

    def rewrite(url: str) -> str | None:
        if url.startswith(("http://", "https://", "mailto:", "tel:", "#", "/")):
            return None

        raw_target, hash_sep, fragment = url.partition("#")
        target, query_sep, query = raw_target.partition("?")
        if not target.endswith(".md"):
            return None

        resolved = (current_dir / PurePosixPath(target)).resolve()
        try:
            relative = PurePosixPath(resolved.relative_to(root).as_posix())
        except ValueError:
            return None

        rewritten = food_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_food_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_food_link_rewriter(file),
    )


@potyk_io_bp.route("/")
def index():
    notes, has_more = random_note_batch(BATCH_SIZE)
    return flask.render_template(
        "potyk-io/index.html",
        notes=notes,
        has_more=has_more,
        exclude=[n.get("id", n["url"]) for n in notes],
    )


@potyk_io_bp.route("/feed/more")
def feed_more():
    exclude = {
        u for u in flask.request.args.get("exclude", "").split(",") if u
    }
    notes, has_more = random_note_batch(BATCH_SIZE, exclude=exclude)
    return flask.render_template(
        "potyk-io/_notes_batch.html",
        notes=notes,
        has_more=has_more,
        exclude=[*exclude, *(n.get("id", n["url"]) for n in notes)],
    )


@potyk_io_bp.route("/search")
def search():
    q = flask.request.args.get("q", "").strip()
    results = search_notes(q) if q else []
    return flask.render_template("potyk-io/search.html", q=q, results=results)


@potyk_io_bp.route("/collections/movies")
def movies_collection():
    page = load_movies_data()
    return flask.render_template(
        "potyk-io/collections/movies.html",
        collections=page.collections,
        watch_later=page.watch_later,
        roulette_collections=page.roulette_collections,
        movies_by_collection_json=json.dumps(movies_for_client(page), ensure_ascii=False),
    )


@potyk_io_bp.route("/collections/movies/admin")
@login_required
def movies_admin():
    movies = db.session.scalars(select(Movie).order_by(Movie.id.asc())).all()
    collections = db.session.scalars(
        select(MovieCollection).order_by(MovieCollection.watch_later.desc(), MovieCollection.sort_order.asc(), MovieCollection.id.asc())
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
                "watch_later": collection.watch_later,
                "movies": collection_movies,
            }
        )
    return render_template(
        "potyk-io/collections/movies_admin.html",
        movies=movies,
        collections=collections,
        collections_kanban_json=json.dumps(collections_kanban, ensure_ascii=False),
    )


def _parse_movie_ids(raw: str) -> list[str]:
    # Поддерживаем ввод: "1,2,3", "1 2 3" и переносы строк.
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


@potyk_io_bp.post("/collections/movies/admin/movie")
@login_required
def movies_admin_add_movie():
    movie_id = (request.form.get("id") or "").strip()
    title_ru = (request.form.get("title_ru") or "").strip()
    title_en = (request.form.get("title_en") or "").strip() or None
    cover = (request.form.get("cover") or "").strip() or None
    kinopoisk = (request.form.get("kinopoisk") or "").strip()

    year_raw = (request.form.get("year") or "").strip()
    year = None
    if year_raw:
        try:
            year = int(year_raw)
        except ValueError:
            flash("Год должен быть числом", "error")
            return redirect(url_for("potyk_io.movies_admin"))

    if not movie_id:
        flash("Укажите `id` фильма", "error")
        return redirect(url_for("potyk_io.movies_admin"))
    if not title_ru:
        flash("Укажите `title_ru` фильма", "error")
        return redirect(url_for("potyk_io.movies_admin"))
    if not kinopoisk:
        flash("Укажите `kinopoisk` (URL)", "error")
        return redirect(url_for("potyk_io.movies_admin"))

    movie = db.session.get(Movie, movie_id)
    if movie is None:
        movie = Movie(id=movie_id)
        db.session.add(movie)

    movie.title_ru = title_ru
    movie.title_en = title_en
    movie.year = year
    movie.cover = cover
    movie.kinopoisk = kinopoisk

    db.session.commit()
    flash("Фильм сохранён", "success")
    return redirect(url_for("potyk_io.movies_admin"))


@potyk_io_bp.post("/collections/movies/admin/collection")
@login_required
def movies_admin_create_collection():
    title = (request.form.get("title") or "").strip()
    youtube = (request.form.get("youtube") or "").strip() or None
    quote = (request.form.get("quote") or "").strip() or None
    watch_later = (request.form.get("watch_later") or "") == "on"
    movie_ids_raw = request.form.get("movie_ids") or ""
    movie_ids = _parse_movie_ids(movie_ids_raw)

    if not title:
        flash("Укажите `title` коллекции", "error")
        return redirect(url_for("potyk_io.movies_admin"))

    col_id = _collection_slug_from_title(title)

    # Проверяем, что фильмы существуют.
    if movie_ids:
        existing = set(db.session.scalars(select(Movie.id).where(Movie.id.in_(movie_ids))).all())
        missing = [mid for mid in movie_ids if mid not in existing]
        if missing:
            flash(f"Не найдено фильмов: {', '.join(missing[:10])}", "error")
            return redirect(url_for("potyk_io.movies_admin"))

    col = db.session.get(MovieCollection, col_id)
    if col is None:
        # sort_order: в конец среди non-watch_later коллекций.
        max_sort = db.session.scalar(
            select(sa.func.max(MovieCollection.sort_order)).where(MovieCollection.watch_later.is_(False))
        )
        col = MovieCollection(id=col_id, sort_order=(max_sort or 0) + 1)
        db.session.add(col)

    col.title = title
    col.youtube = youtube
    col.quote = quote

    col.movie_ids = movie_ids

    # Ограничиваем “ровно одну watch_later-коллекцию”, чтобы рулетка не зависела от порядка.
    if watch_later:
        db.session.query(MovieCollection).filter(MovieCollection.id != col_id).update({"watch_later": False})
        col.watch_later = True
    else:
        # Не даём выключить watch_later у последней коллекции.
        if col.watch_later:
            only_watch_later = db.session.scalar(
                select(sa.func.count(MovieCollection.id)).where(MovieCollection.watch_later.is_(True))
            )
            if only_watch_later == 1:
                flash("Нельзя выключить watch_later у единственной коллекции — сначала включите его в другую.", "error")
                db.session.rollback()
                return redirect(url_for("potyk_io.movies_admin"))
        col.watch_later = False

    db.session.commit()
    flash("Коллекция сохранена", "success")
    return redirect(url_for("potyk_io.movies_admin"))


@potyk_io_bp.post("/collections/movies/admin/collection/add-movie")
@login_required
def movies_admin_add_movie_to_collection():
    col_id = (request.form.get("collection_id") or "").strip()
    movie_id = (request.form.get("movie_id") or "").strip()

    if not col_id or not movie_id:
        flash("Укажите `collection_id` и `movie_id`", "error")
        return redirect(url_for("potyk_io.movies_admin"))

    col = db.session.get(MovieCollection, col_id)
    if col is None:
        flash("Коллекция не найдена", "error")
        return redirect(url_for("potyk_io.movies_admin"))

    movie = db.session.get(Movie, movie_id)
    if movie is None:
        flash("Фильм не найден", "error")
        return redirect(url_for("potyk_io.movies_admin"))

    movie_ids = list(col.movie_ids or [])
    if movie_id not in movie_ids:
        movie_ids.append(movie_id)
        col.movie_ids = movie_ids

    db.session.commit()
    flash("Фильм добавлен в коллекцию", "success")
    return redirect(url_for("potyk_io.movies_admin"))


@potyk_io_bp.post("/collections/movies/admin/collection/move-movie")
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


@potyk_io_bp.post("/collections/movies/admin/movie/delete")
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


@potyk_io_bp.route("/food")
@potyk_io_bp.route("/food/")
def food_index():
    return render_food_markdown(FOOD_TEMPLATES_DIR / "index.md")


@potyk_io_bp.route("/food/<path:page_path>")
def food_page(page_path: str):
    file = resolve_page(page_path, root=FOOD_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_food_markdown(file)

    return send_file(file)


@potyk_io_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
        created = resolve_created(file, meta)
        return render_body_html(body, meta, title=file.stem, created=created)

    template_name = f"potyk-io/{file.relative_to(TEMPLATES_DIR).as_posix()}"
    ctx = {}
    if file == TEMPLATES_DIR / "index.html":
        notes, has_more = random_note_batch(BATCH_SIZE)
        ctx.update(
            notes=notes,
            has_more=has_more,
            exclude=[n.get("id", n["url"]) for n in notes],
        )
    return flask.render_template(template_name, **ctx)
