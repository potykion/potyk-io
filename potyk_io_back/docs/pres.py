from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, render_template, request, send_file

from potyk_io_back.potyk_io.md_rendering import (
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.md_rendering.render import extract_h1
from potyk_io_back.potyk_io.menu import MENU_GROUPS

DOCS_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "docs"

docs_bp = Blueprint("docs", __name__, url_prefix="/docs")


@docs_bp.context_processor
def docs_nav_context():
    return {
        "menu_groups": MENU_GROUPS,
        "section_brand_title": "potyk.io",
        "section_brand_url": "/",
    }


def docs_page_url(path: PurePosixPath) -> str:
    if path.name in ("index.md", "index.html"):
        parent = path.parent.as_posix()
        return "/docs" if parent == "." else f"/docs/{parent}"
    return f"/docs/{path.with_suffix('').as_posix()}"


def make_docs_link_rewriter(file: Path):
    root = DOCS_TEMPLATES_DIR.resolve()
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

        rewritten = docs_page_url(relative)
        if query_sep:
            rewritten = f"{rewritten}?{query}"
        if hash_sep:
            rewritten = f"{rewritten}#{fragment}"
        return rewritten

    return rewrite


def render_docs_markdown(file: Path):
    meta, body = split_frontmatter(file.read_text(encoding="utf-8-sig"))
    created = resolve_created(file, meta)
    base_href = request.path if request.path.endswith("/") else f"{request.path}/"
    return render_body_html(
        body,
        meta,
        title=file.stem,
        created=created,
        base_href=base_href,
        link_rewriter=make_docs_link_rewriter(file),
    )


def _doc_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return path.stem
    _, body = split_frontmatter(text)
    return extract_h1(body) or path.stem


def _safe_docs_subdir(rel: str) -> Path | None:
    rel = rel.strip("/")
    if not rel or ".." in Path(rel).parts:
        return None
    folder = (DOCS_TEMPLATES_DIR / rel).resolve()
    try:
        folder.relative_to(DOCS_TEMPLATES_DIR.resolve())
    except ValueError:
        return None
    if not folder.is_dir():
        return None
    return folder


def build_docs_tree(
    folder: Path,
    *,
    url_prefix: str = "/docs",
) -> list[dict]:
    """Вложенное дерево папок и статей из templates/docs."""
    nodes: list[dict] = []
    entries = sorted(folder.iterdir(), key=lambda p: p.name.casefold())
    for path in entries:
        if path.name.startswith(("_", ".")):
            continue

        if path.is_dir():
            child_prefix = f"{url_prefix.rstrip('/')}/{path.name}"
            children = build_docs_tree(path, url_prefix=child_prefix)
            index = path / "index.md"
            if index.is_file():
                nodes.append(
                    {
                        "title": _doc_title(index),
                        "url": child_prefix,
                        "children": children,
                    }
                )
            elif children:
                nodes.append(
                    {
                        "title": path.name,
                        "url": child_prefix,
                        "children": children,
                    }
                )
            continue

        if path.suffix.lower() != ".md" or path.name == "index.md":
            continue
        nodes.append(
            {
                "title": _doc_title(path),
                "url": f"{url_prefix.rstrip('/')}/{path.stem}",
                "children": [],
            }
        )
    return nodes


def render_docs_tree(*, folder: Path, title: str, url_prefix: str) -> str:
    tree = build_docs_tree(folder, url_prefix=url_prefix)
    lead = (
        "Спеки и описание поведения."
        if url_prefix.rstrip("/") == "/docs"
        else None
    )
    return render_template(
        "docs/tree.html",
        tree=tree,
        page_title=title,
        lead=lead,
    )


@docs_bp.get("/")
def index():
    return render_docs_tree(
        folder=DOCS_TEMPLATES_DIR,
        title="docs",
        url_prefix="/docs",
    )


@docs_bp.route("/<path:page_path>")
def page(page_path: str):
    file = resolve_page(page_path, root=DOCS_TEMPLATES_DIR, allow_assets=True)
    if file is not None:
        if file.suffix == ".md":
            return render_docs_markdown(file)
        return send_file(file)

    folder = _safe_docs_subdir(page_path)
    if folder is not None:
        return render_docs_tree(
            folder=folder,
            title=folder.name,
            url_prefix=f"/docs/{page_path.strip('/')}",
        )

    abort(404)
