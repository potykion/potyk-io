import json
import re
from datetime import date, datetime, timedelta
from itertools import groupby
from pathlib import Path, PurePosixPath

import flask
import markdown
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
from potyk_io_back.potyk_io.findings import Finding
from potyk_io_back.potyk_io.findings.forms import (
    AddFindingForm,
    DeleteFindingForm,
    MarkWatchedForm,
)
from potyk_io_back.potyk_io.md_rendering import (
    FOOD_TEMPLATES_DIR,
    TEMPLATES_DIR,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.hashtags import linkify_hashtags
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.md_rendering.render import MD_EXTENSIONS
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
        movies_by_collection_json=json.dumps(movies_for_client(page), ensure_ascii=False),
    )


@potyk_io_bp.route("/collections/movies/admin")
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
        max_sort = db.session.scalar(
            select(sa.func.max(MovieCollection.sort_order))
        )
        col = MovieCollection(id=col_id, sort_order=(max_sort or 0) + 1)
        db.session.add(col)

    col.title = title
    col.youtube = youtube
    col.quote = quote

    col.movie_ids = movie_ids

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


def _findings_archive_html() -> str:
    archive = TEMPLATES_DIR / "findings.md"
    if not archive.is_file():
        return ""
    _, body = split_frontmatter(archive.read_text(encoding="utf-8-sig"))
    return markdown.markdown(
        linkify_hashtags(body),
        extensions=MD_EXTENSIONS,
        output_format="html",
    )


def _flash_form_errors(form) -> None:
    for messages in form.errors.values():
        for message in messages:
            flash(message, "error")


def _week_label(day: date) -> str:
    start = day - timedelta(days=day.weekday())
    end = start + timedelta(days=6)
    return f"{start.isoformat()} — {end.isoformat()}"


def _group_watched_by_week(items: list[Finding]) -> list[dict]:
    groups: list[dict] = []
    for label, grouped in groupby(
        items, key=lambda f: _week_label(f.watched_at.date())
    ):
        groups.append({"title": label, "entries": list(grouped)})
    return groups


@potyk_io_bp.get("/findings")
def findings():
    unwatched = db.session.scalars(
        select(Finding)
        .where(Finding.watched_at.is_(None))
        .order_by(Finding.created_at.desc(), Finding.id.desc())
    ).all()
    watched = db.session.scalars(
        select(Finding)
        .where(Finding.watched_at.is_not(None))
        .order_by(Finding.watched_at.desc(), Finding.id.desc())
    ).all()
    return render_template(
        "potyk-io/findings.html",
        unwatched=unwatched,
        watched_weeks=_group_watched_by_week(list(watched)),
        add_form=AddFindingForm(),
        mark_form=MarkWatchedForm(),
        delete_form=DeleteFindingForm(),
        archive_html=_findings_archive_html(),
    )


@potyk_io_bp.post("/findings")
@login_required
def findings_add():
    form = AddFindingForm()
    if not form.validate_on_submit():
        _flash_form_errors(form)
        return redirect(url_for("potyk_io.findings"))

    url = form.url.data.strip()
    existing = db.session.scalar(select(Finding).where(Finding.url == url))
    if existing is not None:
        flash("Такая ссылка уже есть", "error")
        return redirect(url_for("potyk_io.findings"))

    kind = (form.kind.data or "").strip()
    raw_title = (form.title.data or "").strip() or url
    title = f"{kind} {raw_title}".strip() if kind else raw_title

    db.session.add(
        Finding(
            url=url,
            title=title[:512],
            created_at=datetime.now(),
        )
    )
    db.session.commit()
    flash("Добавлено", "success")
    return redirect(url_for("potyk_io.findings"))


@potyk_io_bp.post("/findings/<int:finding_id>/watched")
@login_required
def findings_mark_watched(finding_id: int):
    form = MarkWatchedForm()
    if not form.validate_on_submit():
        _flash_form_errors(form)
        return redirect(url_for("potyk_io.findings"))

    finding = db.session.get(Finding, finding_id)
    if finding is None:
        abort(404)
    if finding.watched_at is None:
        finding.watched_at = datetime.now()
        db.session.commit()
        flash("Отмечено как просмотренное", "success")
    return redirect(url_for("potyk_io.findings"))


@potyk_io_bp.post("/findings/<int:finding_id>/delete")
@login_required
def findings_delete(finding_id: int):
    form = DeleteFindingForm()
    if not form.validate_on_submit():
        _flash_form_errors(form)
        return redirect(url_for("potyk_io.findings"))

    finding = db.session.get(Finding, finding_id)
    if finding is None:
        abort(404)
    db.session.delete(finding)
    db.session.commit()
    flash("Удалено", "success")
    return redirect(url_for("potyk_io.findings"))


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
