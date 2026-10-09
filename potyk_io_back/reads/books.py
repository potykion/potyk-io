"""Книги potyk-reads: карточки из markdown + frontmatter."""

from __future__ import annotations

import html as html_module
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.game import BookReadingProgress
from potyk_io_back.potyk_io.md_rendering import extract_h1, split_frontmatter, unquote_meta

READS_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-reads"
BOOK_COVER_PLACEHOLDER = "/static/potyk-io/img/books/cover-placeholder.svg"

_BOOK_PROP_FIELDS: tuple[tuple[str, str], ...] = (
    ("author", "Автор"),
    ("subtitle", "Подзаголовок"),
    ("pages", "Всего страниц"),
)


@dataclass(frozen=True)
class BookCard:
    title: str
    subtitle: str
    author: str
    cover: str
    url: str


@dataclass(frozen=True)
class InventoryBook:
    slug: str
    title: str
    author: str
    cover: str
    pages: int
    pages_read: int
    progress_pct: int


def _book_paths(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        (
            path
            for path in root.glob("*.md")
            if path.is_file() and not path.name.startswith(("_", "."))
        ),
        key=lambda path: path.stem.casefold(),
    )


def _parse_positive_int(raw: str) -> int | None:
    text = unquote_meta(raw).strip()
    if not text:
        return None
    try:
        value = int(text)
    except ValueError:
        return None
    return value if value > 0 else None


def book_props_html(meta: dict[str, str]) -> str | None:
    """Блок свойств книги под заголовком страницы ревью."""
    rows: list[str] = []
    for key, label in _BOOK_PROP_FIELDS:
        raw = unquote_meta(meta.get(key, ""))
        if not raw:
            continue
        rows.append(
            f'<div class="album-props-row">'
            f"<dt>{html_module.escape(label)}</dt>"
            f"<dd>{html_module.escape(raw)}</dd>"
            f"</div>"
        )
    if not rows:
        return None
    return f'<dl class="album-props">{"".join(rows)}</dl>'


def load_books(*, root: Path | None = None) -> list[BookCard]:
    """Список книг для сетки `/reads/`: title / subtitle / author / cover из YAML."""
    books_root = root or READS_TEMPLATES_DIR
    books: list[BookCard] = []
    for path in _book_paths(books_root):
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        title = unquote_meta(meta.get("title", "")) or extract_h1(body) or path.stem
        subtitle = unquote_meta(meta.get("subtitle", ""))
        author = unquote_meta(meta.get("author", ""))
        cover = unquote_meta(meta.get("cover", "")) or BOOK_COVER_PLACEHOLDER
        books.append(
            BookCard(
                title=title,
                subtitle=subtitle,
                author=author,
                cover=cover,
                url=f"/reads/{path.stem}",
            )
        )
    return books


def load_inventory_books(*, root: Path | None = None) -> list[InventoryBook]:
    """Книги в инвентаре: есть прогресс в SQL и он меньше total pages из md."""
    books_root = root or READS_TEMPLATES_DIR
    progress_by_slug = {
        row.slug: int(row.pages_read)
        for row in db.session.scalars(select(BookReadingProgress)).all()
    }
    result: list[InventoryBook] = []
    for path in _book_paths(books_root):
        if path.stem not in progress_by_slug:
            continue
        meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
        pages = _parse_positive_int(meta.get("pages", ""))
        if pages is None:
            continue
        pages_read = progress_by_slug[path.stem]
        if pages_read >= pages:
            continue
        title = unquote_meta(meta.get("title", "")) or extract_h1(body) or path.stem
        author = unquote_meta(meta.get("author", ""))
        cover = unquote_meta(meta.get("cover", "")) or BOOK_COVER_PLACEHOLDER
        progress_pct = int(round(100 * pages_read / pages)) if pages else 0
        result.append(
            InventoryBook(
                slug=path.stem,
                title=title,
                author=author,
                cover=cover,
                pages=pages,
                pages_read=pages_read,
                progress_pct=progress_pct,
            )
        )
    return result


def load_book_by_slug(slug: str, *, root: Path | None = None) -> InventoryBook | None:
    """Метаданные книги из md + текущий прогресс из SQL (если есть)."""
    books_root = root or READS_TEMPLATES_DIR
    path = books_root / f"{slug}.md"
    if not path.is_file():
        return None
    meta, body = split_frontmatter(path.read_text(encoding="utf-8-sig"))
    pages = _parse_positive_int(meta.get("pages", ""))
    if pages is None:
        return None
    row = db.session.scalar(
        select(BookReadingProgress).where(BookReadingProgress.slug == slug)
    )
    pages_read = int(row.pages_read) if row is not None else 0
    title = unquote_meta(meta.get("title", "")) or extract_h1(body) or path.stem
    author = unquote_meta(meta.get("author", ""))
    cover = unquote_meta(meta.get("cover", "")) or BOOK_COVER_PLACEHOLDER
    progress_pct = int(round(100 * pages_read / pages)) if pages else 0
    return InventoryBook(
        slug=path.stem,
        title=title,
        author=author,
        cover=cover,
        pages=pages,
        pages_read=pages_read,
        progress_pct=progress_pct,
    )


def set_book_pages_read(slug: str, pages_read: int) -> BookReadingProgress:
    """Создать или обновить прогресс чтения по слагу книги."""
    row = db.session.scalar(
        select(BookReadingProgress).where(BookReadingProgress.slug == slug)
    )
    if row is None:
        row = BookReadingProgress(slug=slug, pages_read=pages_read)
        db.session.add(row)
    else:
        row.pages_read = pages_read
    db.session.commit()
    return row
