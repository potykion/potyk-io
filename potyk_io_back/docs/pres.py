from pathlib import Path, PurePosixPath

from flask import Blueprint, abort, request, send_file

from potyk_io_back.potyk_io.md_rendering import (
    render_body_html,
    resolve_page,
    split_frontmatter,
)
from potyk_io_back.potyk_io.md_rendering.created import resolve_created
from potyk_io_back.potyk_io.md_rendering.render import extract_h1
from potyk_io_back.potyk_io.menu import MenuGroup, MenuItem

DOCS_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "docs"

docs_bp = Blueprint("docs", __name__, url_prefix="/docs")


def _top_level_folders() -> list[MenuItem]:
    items: list[MenuItem] = [
        {
            "icon": "📑",
            "title": "Все статьи",
            "url": "/docs/",
            "description": "",
        }
    ]
    if not DOCS_TEMPLATES_DIR.is_dir():
        return items
    for path in sorted(DOCS_TEMPLATES_DIR.iterdir(), key=lambda p: p.name.casefold()):
        if not path.is_dir() or path.name.startswith(("_", ".")):
            continue
        items.append(
            {
                "icon": "📁",
                "title": path.name,
                "url": f"/docs/{path.name}",
                "description": "",
            }
        )
    return items


def docs_menu_groups() -> list[MenuGroup]:
    return [
        {"title": "docs", "links": _top_level_folders()},
        {
            "title": "",
            "links": [
                {
                    "icon": "←",
                    "title": "potyk-io",
                    "url": "/",
                    "description": "",
                }
            ],
        },
    ]


@docs_bp.context_processor
def docs_nav_context():
    return {
        "menu_groups": docs_menu_groups(),
        "section_brand_title": "docs",
        "section_brand_url": "/docs",
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


def build_docs_tree_markdown(
    folder: Path,
    *,
    url_prefix: str = "/docs",
    heading_level: int = 2,
) -> str:
    """Markdown-оглавление из папок и .md на диске (на каждый запрос)."""
    lines: list[str] = []
    entries = sorted(
        folder.iterdir(),
        key=lambda p: (not p.is_dir(), p.name.casefold()),
    )
    for path in entries:
        if path.name.startswith(("_", ".")):
            continue
        if path.is_dir():
            child_prefix = f"{url_prefix.rstrip('/')}/{path.name}"
            nested = build_docs_tree_markdown(
                path,
                url_prefix=child_prefix,
                heading_level=min(heading_level + 1, 6),
            )
            if not nested.strip():
                continue
            level = min(max(heading_level, 2), 6)
            lines.append(f'{"#" * level} [{path.name}]({child_prefix})')
            lines.append("")
            lines.append(nested.rstrip())
            lines.append("")
            continue
        if path.suffix.lower() != ".md" or path.name in {"index.md"}:
            continue
        title = _doc_title(path)
        url = f"{url_prefix.rstrip('/')}/{path.stem}"
        lines.append(f"- [{title}]({url})")
    return "\n".join(lines).rstrip() + ("\n" if lines else "")


def render_docs_tree(*, folder: Path, title: str, url_prefix: str) -> str:
    tree_md = build_docs_tree_markdown(folder, url_prefix=url_prefix)
    if not tree_md.strip():
        body = f"# {title}\n\nПока пусто.\n"
    else:
        lead = "Спеки и описание поведения.\n\n" if url_prefix.rstrip("/") == "/docs" else ""
        body = f"# {title}\n\n{lead}{tree_md}"
    return render_body_html(body, {}, title=title)


@docs_bp.get("/")
def index():
    return render_docs_tree(
        folder=DOCS_TEMPLATES_DIR,
        title="docs",
        url_prefix="/docs",
    )


@docs_bp.route("/<path:page_path>")
def page(page_path: str):
    folder = _safe_docs_subdir(page_path)
    if folder is not None:
        return render_docs_tree(
            folder=folder,
            title=folder.name,
            url_prefix=f"/docs/{page_path.strip('/')}",
        )

    file = resolve_page(page_path, root=DOCS_TEMPLATES_DIR, allow_assets=True)
    if file is None:
        abort(404)

    if file.suffix == ".md":
        return render_docs_markdown(file)

    return send_file(file)
