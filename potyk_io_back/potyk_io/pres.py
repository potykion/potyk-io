import json
from datetime import date, datetime, timedelta
from itertools import groupby
from pathlib import Path, PurePosixPath

import flask
import markdown
from flask import Blueprint, abort, flash, jsonify, redirect, request, render_template, send_file, url_for
from flask_login import login_required
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.collections.movies import load_movies_data, movies_for_client
from potyk_io_back.potyk_io.feed import BATCH_SIZE, random_note_batch, search_notes
from potyk_io_back.potyk_io.findings import Finding
from potyk_io_back.potyk_io.findings.forms import (
    AddFindingForm,
    DeleteFindingForm,
    MarkWatchedForm,
)
from potyk_io_back.potyk_io.note_votes import (
    random_swipe_note,
    save_note_vote,
)
from potyk_io_back.potyk_io.note_votes.service import VALID_VOTES
from potyk_io_back.potyk_io.restaurants.entities import (
    Restaurant,
    restaurant_vocab,
    seed_restaurants_if_empty,
)
from potyk_io_back.potyk_io.md_rendering import (
    FOOD_TEMPLATES_DIR,
    TEMPLATES_DIR,
    list_folder_pages,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.hashtags import linkify_hashtags
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.md_rendering.render import MD_EXTENSIONS, MD_EXTENSION_CONFIGS
from potyk_io_back.potyk_io.menu import FOOD_MENU_GROUPS, MENU_GROUPS

potyk_io_bp = Blueprint("potyk_io", __name__)

WATCH_LATER_COLLECTION_ID = "watch_later"


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
    if path.name in ("index.md", "index.html"):
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
        recipe_ui=True,
    )


@potyk_io_bp.route("/")
def index():
    notes, has_more = random_note_batch(BATCH_SIZE)
    movies_page = load_movies_data()
    movies_client = movies_for_client(movies_page)
    watch_later_movies = movies_client.get("moviesByCollection", {}).get(WATCH_LATER_COLLECTION_ID, [])
    movies_payload = {
        "defaultCollectionId": WATCH_LATER_COLLECTION_ID,
        "moviesByCollection": {WATCH_LATER_COLLECTION_ID: watch_later_movies},
    }
    return flask.render_template(
        "potyk-io/index.html",
        notes=notes,
        has_more=has_more,
        exclude=[n.get("id", n["url"]) for n in notes],
        more_url="/feed/more",
        movies_by_collection_json=json.dumps(movies_payload, ensure_ascii=False),
    )


@potyk_io_bp.route("/feed/more")
def feed_more():
    exclude = {
        u for u in flask.request.args.get("exclude", "").split(",") if u
    }
    notes, has_more = random_note_batch(BATCH_SIZE, exclude=exclude)
    return flask.render_template(
        "jinja/_notes_batch.html",
        notes=notes,
        has_more=has_more,
        exclude=[*exclude, *(n.get("id", n["url"]) for n in notes)],
        more_url="/feed/more",
    )


@potyk_io_bp.get("/activity/notes/random")
def activity_notes_random():
    exclude = {
        u for u in flask.request.args.get("exclude", "").split(",") if u
    }
    note = random_swipe_note(exclude=exclude)
    if note is None:
        return jsonify({"ok": False, "error": "empty"}), 404
    return jsonify({"ok": True, "note": note})


@potyk_io_bp.post("/activity/notes/vote")
def activity_notes_vote():
    payload = flask.request.get_json(silent=True) or {}
    note_id = str(payload.get("id") or "").strip()
    note_url = str(payload.get("url") or "").strip()
    title = str(payload.get("title") or "").strip()
    vote = str(payload.get("vote") or "").strip()

    if not note_id or not note_url or vote not in VALID_VOTES:
        return jsonify({"ok": False, "error": "missing fields"}), 400

    save_note_vote(note_id=note_id, note_url=note_url, title=title, vote=vote)
    return jsonify({"ok": True})


@potyk_io_bp.route("/search")
def search():
    q = flask.request.args.get("q", "").strip()
    results = search_notes(q) if q else []
    return flask.render_template("potyk-io/search.html", q=q, results=results)


@potyk_io_bp.route("/collections/devices")
@potyk_io_bp.route("/collections/devices/")
def devices_moved():
    return redirect("/tech/devices", code=301)


@potyk_io_bp.route("/n/cv")
@potyk_io_bp.route("/n/cv/")
def cv_moved():
    return redirect("/tech/cv", code=301)


@potyk_io_bp.route("/code")
@potyk_io_bp.route("/code/")
def code_moved():
    return redirect("/tech/my-code", code=301)


@potyk_io_bp.route("/code/<path:page_path>")
def code_page_moved(page_path: str):
    return redirect(f"/tech/{page_path}", code=301)


@potyk_io_bp.route("/guides/passive-income")
@potyk_io_bp.route("/guides/passive-income/")
def passive_income_moved():
    return redirect("/invest/passive-income", code=301)


@potyk_io_bp.route("/notes/tea")
@potyk_io_bp.route("/notes/tea/")
def notes_tea_moved():
    return redirect("/food/thoughts/tea", code=301)


@potyk_io_bp.route("/collections/movies")
@potyk_io_bp.route("/collections/movies/<path:_rest>")
def movies_collection_redirect(_rest=None):
    if _rest:
        return redirect(f"/cinema/{_rest}", code=301)
    return redirect("/cinema/", code=301)


@potyk_io_bp.route("/thoughts/food")
@potyk_io_bp.route("/thoughts/food/")
@potyk_io_bp.route("/thoughts/food/<path:_rest>")
def food_thoughts_redirect(_rest=None):
    if _rest:
        return redirect(f"/food/thoughts/{_rest}", code=301)
    return redirect("/food", code=301)


@potyk_io_bp.route("/food/thoughts")
@potyk_io_bp.route("/food/thoughts/")
def food_thoughts_index_redirect():
    return redirect("/food", code=301)


def _findings_archive_html() -> str:
    archive = TEMPLATES_DIR / "findings.md"
    if not archive.is_file():
        return ""
    _, body = split_frontmatter(archive.read_text(encoding="utf-8-sig"))
    return markdown.markdown(
        linkify_hashtags(body),
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
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


@potyk_io_bp.get("/food/rest")
@potyk_io_bp.get("/food/rest/")
def restaurants():
    seed_restaurants_if_empty()
    items = db.session.scalars(
        select(Restaurant).order_by(Restaurant.name.asc(), Restaurant.id.asc())
    ).all()
    _, all_tags = restaurant_vocab()
    return render_template(
        "potyk-food/rest.html",
        restaurants=items,
        all_tags=all_tags,
    )


@potyk_io_bp.get("/food/rest/admin")
@potyk_io_bp.post("/food/rest/admin")
@login_required
def restaurants_admin_redirect():
    return redirect(url_for("admin.restaurants"), code=301)


@potyk_io_bp.route("/food/<path:page_path>")
def food_page(page_path: str):
    file = resolve_page(page_path, root=FOOD_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_food_markdown(file)

    if file.suffix == ".html":
        template_name = f"potyk-food/{file.relative_to(FOOD_TEMPLATES_DIR).as_posix()}"
        ctx = {}
        if file.name == "index.html":
            ctx["pages"] = list_folder_pages(
                file.parent,
                url_prefix=food_page_url(
                    PurePosixPath(file.relative_to(FOOD_TEMPLATES_DIR).as_posix())
                ),
            )
        return render_template(template_name, **ctx)

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
            more_url="/feed/more",
        )
    return flask.render_template(template_name, **ctx)
