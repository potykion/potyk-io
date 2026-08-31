from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, request, render_template, send_file, url_for

from potyk_io_back.mu.albums import album_props_html, is_album_page
from potyk_io_back.mu.artists import albums_for_artist, is_artist_page
from potyk_io_back.mu.menu import MU_MENU_ITEMS, is_mu_link_active
from potyk_io_back.potyk_io.feed import BATCH_SIZE, FeedSpec, feed_batch, feed_more_url
from potyk_io_back.potyk_io.md_rendering import render_body_html, resolve_page, split_frontmatter
from potyk_io_back.potyk_io.md_rendering.created import resolve_created

MU_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-mu"

mu_bp = Blueprint("mu", __name__, url_prefix="/mu")

MU_FEEDS: dict[str, FeedSpec] = {
    "blog": FeedSpec(
        id="blog",
        root=MU_TEMPLATES_DIR / "blog",
        url_prefix="/mu/blog",
        sort="date_desc",
        recursive=True,
    ),
    "albums": FeedSpec(
        id="albums",
        root=MU_TEMPLATES_DIR / "albums",
        url_prefix="/mu/albums",
        sort="date_desc",
        recursive=True,
    ),
    "artists": FeedSpec(
        id="artists",
        root=MU_TEMPLATES_DIR / "artists",
        url_prefix="/mu/artists",
        sort="name",
        recursive=True,
    ),
}


@mu_bp.context_processor
def inject_mu_menu():
    items = [
        {
            "icon": item["icon"],
            "title": item["title"],
            "url": item["url"],
            "active": is_mu_link_active(item["url"], request.path),
        }
        for item in MU_MENU_ITEMS
    ]
    return {"mu_menu_items": items}


def mu_page_url(path: PurePosixPath) -> str:
    if path.name == "index.md":
        parent = path.parent.as_posix()
        return "/mu" if parent == "." else f"/mu/{parent}"
    return f"/mu/{path.with_suffix('').as_posix()}"


def make_mu_link_rewriter(file: Path):
    root = MU_TEMPLATES_DIR.resolve()
    current_dir = file.parent.resolve()

    def rewrite(url: str) -> str | None:
        if url.startswith(("http://", "https://", "mailto:", "tel:", "#", "/")):
            return None

        raw_target, hash_sep, fragment = url.partition("#")
        target, query_sep, query = raw_target.partition("?")

        resolved = (current_dir / PurePosixPath(target)).resolve()
        if not target.endswith(".md"):
            md_candidate = resolved.with_suffix(".md") if resolved.suffix == "" else Path(f"{resolved}.md")
            if md_candidate.is_file():
                resolved = md_candidate
            elif not resolved.is_file():
                return None
        try:
            relative = PurePosixPath(resolved.relative_to(root).as_posix())
        except ValueError:
            return None
        if relative.suffix != ".md":
            return None

        rewritten = mu_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_mu_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    link_rewriter = make_mu_link_rewriter(file)
    extra: dict = {}
    after_h1_html: str | None = None
    artists_dir = MU_TEMPLATES_DIR / "artists"
    albums_dir = MU_TEMPLATES_DIR / "albums"
    if is_artist_page(file, artists_dir=artists_dir):
        extra["artist_albums"] = albums_for_artist(file, albums_spec=MU_FEEDS["albums"])
    if is_album_page(file, albums_dir=albums_dir):
        after_h1_html = album_props_html(meta, link_rewriter=link_rewriter)
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=link_rewriter,
        template="potyk-mu/page.html",
        after_h1_html=after_h1_html,
        **extra,
    )


def _render_feed_batch(spec: FeedSpec, *, exclude: set[str] | None = None):
    skip = exclude or set()
    notes, has_more = feed_batch(spec, BATCH_SIZE, exclude=skip)
    more = feed_more_url(spec.id, endpoint=url_for("mu.feed_more"))
    return render_template(
        "jinja/_notes_batch.html",
        notes=notes,
        has_more=has_more,
        exclude=[*skip, *(n.get("id", n["url"]) for n in notes)],
        more_url=more,
    )


@mu_bp.route("/")
def index():
    blog = MU_FEEDS["blog"]
    notes, has_more = feed_batch(blog, BATCH_SIZE)
    return render_template(
        "potyk-mu/index.html",
        notes=notes,
        has_more=has_more,
        exclude=[n.get("id", n["url"]) for n in notes],
        more_url=feed_more_url(blog.id, endpoint=url_for("mu.feed_more")),
    )


@mu_bp.route("/feed/more")
def feed_more():
    feed_id = request.args.get("feed", "blog")
    spec = MU_FEEDS.get(feed_id)
    if spec is None:
        abort(404)
    exclude = {u for u in request.args.get("exclude", "").split(",") if u}
    return _render_feed_batch(spec, exclude=exclude)


def _feed_index_context(file: Path) -> dict:
    folder = file.parent.relative_to(MU_TEMPLATES_DIR).as_posix()
    spec = MU_FEEDS.get(folder)
    if spec is None:
        return {}
    notes, has_more = feed_batch(spec, BATCH_SIZE)
    return {
        "notes": notes,
        "has_more": has_more,
        "exclude": [n.get("id", n["url"]) for n in notes],
        "more_url": feed_more_url(spec.id, endpoint=url_for("mu.feed_more")),
    }


@mu_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path, root=MU_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_mu_markdown(file)

    if file.suffix == ".html":
        template_name = f"potyk-mu/{file.relative_to(MU_TEMPLATES_DIR).as_posix()}"
        ctx = _feed_index_context(file) if file.name == "index.html" else {}
        return render_template(template_name, **ctx)

    return send_file(file)
