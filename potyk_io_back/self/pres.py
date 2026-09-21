from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, render_template, request, send_file, url_for
from flask_login import login_required

from potyk_io_back.potyk_io.feed import BATCH_SIZE, FeedSpec, feed_batch, feed_more_url
from potyk_io_back.potyk_io.md_rendering import (
    list_folder_pages,
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.menu import SELF_MENU_GROUPS

SELF_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-self"

self_bp = Blueprint("self", __name__, url_prefix="/self")

SELF_FEED = FeedSpec(
    id="self",
    root=SELF_TEMPLATES_DIR,
    url_prefix="/self",
    sort="random",
    recursive=True,
    expand_diary=True,
)


@self_bp.before_request
@login_required
def require_login():
    pass


@self_bp.context_processor
def self_nav_context():
    return {
        "menu_groups": SELF_MENU_GROUPS,
        "section_brand_title": "potyk-self",
        "section_brand_url": "/self",
    }


def self_page_url(path: PurePosixPath) -> str:
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        return "/self" if parent == "." else f"/self/{parent}"
    return f"/self/{path.with_suffix('').as_posix()}"


def make_self_link_rewriter(file: Path):
    root = SELF_TEMPLATES_DIR.resolve()
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

        rewritten = self_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_self_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_self_link_rewriter(file),
    )


@self_bp.get("/")
def index():
    notes, has_more = feed_batch(SELF_FEED, BATCH_SIZE)
    more = feed_more_url(SELF_FEED.id, endpoint=url_for("self.feed_more"))
    return render_template(
        "potyk-self/index.html",
        notes=notes,
        has_more=has_more,
        exclude=[n.get("id", n["url"]) for n in notes],
        more_url=more,
    )


@self_bp.get("/feed/more")
def feed_more():
    exclude = {u for u in request.args.get("exclude", "").split(",") if u}
    notes, has_more = feed_batch(SELF_FEED, BATCH_SIZE, exclude=exclude)
    more = feed_more_url(SELF_FEED.id, endpoint=url_for("self.feed_more"))
    return render_template(
        "jinja/_notes_batch.html",
        notes=notes,
        has_more=has_more,
        exclude=[*exclude, *(n.get("id", n["url"]) for n in notes)],
        more_url=more,
    )


@self_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path, root=SELF_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_self_markdown(file)

    if file.suffix == ".html":
        template_name = f"potyk-self/{file.relative_to(SELF_TEMPLATES_DIR).as_posix()}"
        ctx = {}
        if file.name == "index.html":
            ctx["pages"] = list_folder_pages(
                file.parent,
                url_prefix=self_page_url(
                    PurePosixPath(file.relative_to(SELF_TEMPLATES_DIR).as_posix())
                ),
            )
        return render_template(template_name, **ctx)

    return send_file(file)
