"""Книги potyk-reads: карточки из markdown + frontmatter."""

from __future__ import annotations

import html as html_module
from dataclasses import dataclass
from pathlib import Path

from potyk_io_back.potyk_io.md_rendering import extract_h1, split_frontmatter, unquote_meta

READS_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-reads"
BOOK_COVER_PLACEHOLDER = "/static/potyk-io/img/books/cover-placeholder.svg"

_BOOK_PROP_FIELDS: tuple[tuple[str, str], ...] = (
    ("author", "Автор"),
    ("subtitle", "Подзаголовок"),
    ("pages", "Всего страниц"),
    ("pages_read", "Прочитано страниц"),
)


@dataclass(frozen=True)
class BookCard:
    title: str
    subtitle: str
    author: str
    cover: str
    url: str


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
