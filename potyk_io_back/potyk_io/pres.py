from datetime import date, datetime, timedelta
from itertools import groupby
from pathlib import Path, PurePosixPath

import flask
import markdown
from flask import Blueprint, abort, flash, redirect, request, render_template, send_file, url_for
from flask_login import login_required
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.feed import BATCH_SIZE, random_note_batch, search_notes
from potyk_io_back.potyk_io.findings import Finding
from potyk_io_back.potyk_io.findings.forms import (
    AddFindingForm,
    DeleteFindingForm,
    MarkWatchedForm,
)
from potyk_io_back.potyk_io.restaurants.entities import Restaurant, seed_restaurants_if_empty
from potyk_io_back.potyk_io.restaurants.forms import RestaurantForm
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
    return flask.render_template(
        "potyk-io/index.html",
        notes=notes,
        has_more=has_more,
        exclude=[n.get("id", n["url"]) for n in notes],
        more_url="/feed/more",
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


@potyk_io_bp.route("/search")
def search():
    q = flask.request.args.get("q", "").strip()
    results = search_notes(q) if q else []
    return flask.render_template("potyk-io/search.html", q=q, results=results)


@potyk_io_bp.route("/collections/movies")
@potyk_io_bp.route("/collections/movies/<path:_rest>")
def movies_collection_redirect(_rest=None):
    if _rest:
        return redirect(f"/cinema/{_rest}", code=301)
    return redirect("/cinema/", code=301)


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


def _restaurant_vocab() -> tuple[list[str], list[str]]:
    restaurants = db.session.scalars(select(Restaurant)).all()
    metros: set[str] = set()
    tags: set[str] = set()
    for r in restaurants:
        if r.metro:
            metros.add(r.metro)
        for tag in r.tags or []:
            if tag:
                tags.add(tag)
    return sorted(metros, key=str.casefold), sorted(tags, key=str.casefold)


def _normalize_tags(raw: list[str] | None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in raw or []:
        tag = (item or "").strip()
        if not tag:
            continue
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(tag)
    return result


@potyk_io_bp.get("/food/rest")
@potyk_io_bp.get("/food/rest/")
def restaurants():
    seed_restaurants_if_empty()
    items = db.session.scalars(
        select(Restaurant).order_by(Restaurant.name.asc(), Restaurant.id.asc())
    ).all()
    _, all_tags = _restaurant_vocab()
    return render_template(
        "potyk-food/rest.html",
        restaurants=items,
        all_tags=all_tags,
    )


@potyk_io_bp.get("/food/rest/admin")
@login_required
def restaurants_admin():
    seed_restaurants_if_empty()
    metros, tags = _restaurant_vocab()
    return render_template(
        "potyk-food/rest_admin.html",
        form=RestaurantForm(),
        metros=metros,
        tags=tags,
    )


@potyk_io_bp.post("/food/rest/admin")
@login_required
def restaurants_admin_add():
    form = RestaurantForm()
    metros, tags = _restaurant_vocab()
    if not form.validate_on_submit():
        _flash_form_errors(form)
        return render_template(
            "potyk-food/rest_admin.html",
            form=form,
            metros=metros,
            tags=tags,
        ), 400

    name = (form.name.data or "").strip()
    maps_url = (form.maps_url.data or "").strip()
    metro = (form.metro.data or "").strip()
    restaurant_tags = _normalize_tags(form.tags.data)

    if not name:
        flash("Укажи название", "error")
        return redirect(url_for("potyk_io.restaurants_admin"))
    if not maps_url:
        flash("Нужна ссылка на карту", "error")
        return redirect(url_for("potyk_io.restaurants_admin"))

    db.session.add(
        Restaurant(
            name=name,
            maps_url=maps_url,
            metro=metro,
            tags=restaurant_tags,
        )
    )
    db.session.commit()
    flash("Ресторан добавлен", "success")
    return redirect(url_for("potyk_io.restaurants"))


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
