import re
from datetime import date
from pathlib import Path

from potyk_io_back.potyk_io.md_rendering.created import created_from_meta, parse_iso_date

TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates" / "potyk-io"
FOOD_TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "templates" / "potyk-food"

_INDEX_NAMES = {"index.md", "index.html"}
_SKIP_PAGE_NAMES = _INDEX_NAMES | {"menu.html"}
_H1_HTML_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")
_CREATED_HTML_RE = re.compile(r"<!--\s*created:\s*(\d{4}-\d{2}-\d{2})\s*-->", re.I)


def resolve_page(
    page_path: str, root: Path | None = None, allow_assets: bool = False
) -> Path | None:
    root = root or TEMPLATES_DIR
    page_path = page_path.strip("/")
    if not page_path or ".." in Path(page_path).parts:
        return None

    name = Path(page_path).name
    if name.startswith("_") or name.startswith("."):
        return None

    candidates = [
        root / f"{page_path}.md",
        root / page_path / "index.md",
        root / f"{page_path}.html",
        root / page_path / "index.html",
        root / page_path / "menu.html",
    ]
    if allow_assets:
        candidates.append(root / page_path)

    templates_root = root.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(templates_root)
        except (ValueError, OSError):
            continue
        if resolved.is_file() and not resolved.name.startswith("_"):
            return resolved

    return None


def _page_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return path.stem

    if path.suffix.lower() == ".md":
        from potyk_io_back.potyk_io.md_rendering.render import (
            extract_h1,
            split_frontmatter,
        )

        _, body = split_frontmatter(text)
        return extract_h1(body) or path.stem

    match = _H1_HTML_RE.search(text)
    if match:
        title = _TAG_RE.sub("", match.group(1)).strip()
        if title:
            return title
    return path.stem


def _page_created(path: Path) -> date | None:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return None

    if path.suffix.lower() == ".md":
        from potyk_io_back.potyk_io.md_rendering.render import split_frontmatter

        meta, _ = split_frontmatter(text)
        return created_from_meta(meta)

    match = _CREATED_HTML_RE.search(text)
    if match:
        return parse_iso_date(match.group(1))
    return None


def list_folder_pages(
    folder: Path,
    *,
    url_prefix: str,
    sort: str = "name",
) -> list[dict[str, str | date | None]]:
    """Список страниц папки (title + url) для index.html-оглавлений."""
    prefix = url_prefix.rstrip("/")
    pages: list[dict[str, str | date | None]] = []
    for path in folder.iterdir():
        if not path.is_file():
            continue
        if path.name.startswith(("_", ".")) or path.name in _SKIP_PAGE_NAMES:
            continue
        if path.suffix.lower() not in {".md", ".html"}:
            continue
        pages.append(
            {
                "title": _page_title(path),
                "url": f"{prefix}/{path.stem}",
                "created": _page_created(path),
            }
        )

    if sort == "date_desc":
        pages.sort(
            key=lambda page: (
                page.get("created") is not None,
                page.get("created") or date.min,
                str(page["title"]).casefold(),
            ),
            reverse=True,
        )
    elif sort == "date_asc":
        pages.sort(
            key=lambda page: (
                page.get("created") is None,
                page.get("created") or date.max,
                str(page["title"]).casefold(),
            )
        )
    else:
        pages.sort(key=lambda page: str(page["title"]).casefold())
    return pages
