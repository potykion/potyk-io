"""book_reading_progress: pages_read by book slug

Revision ID: book_prog_c1853c
Revises: game_hp_20261006
Create Date: 2026-10-09 18:40:00.000000
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "book_prog_c1853c"
down_revision: Union[str, Sequence[str], None] = "game_hp_20261006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_PAGES_READ_RE = re.compile(r"(?m)^pages_read:\s*(.+?)\s*$")


def _seed_from_markdown() -> dict[str, int]:
    """Собрать pages_read из md, если проп ещё не убрали (локально / старый checkout)."""
    root = Path(__file__).resolve().parents[2] / "templates" / "potyk-reads"
    rows: dict[str, int] = {}
    if not root.is_dir():
        return rows
    for path in sorted(root.glob("*.md")):
        if path.name.startswith(("_", ".")):
            continue
        text = path.read_text(encoding="utf-8-sig")
        m = _FRONTMATTER_RE.match(text)
        if not m:
            continue
        pr = _PAGES_READ_RE.search(m.group(1))
        if not pr:
            continue
        raw = pr.group(1).strip().strip("\"'")
        try:
            pages_read = int(raw)
        except ValueError:
            continue
        if pages_read < 0:
            continue
        rows[path.stem] = pages_read
    return rows


def upgrade() -> None:
    op.create_table(
        "book_reading_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("pages_read", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_book_reading_progress_slug"),
        "book_reading_progress",
        ["slug"],
        unique=True,
    )

    # Зашито: к моменту upgrade pages_read уже может быть убран из md.
    seed: dict[str, int] = {"if-all-cats-disappear": 200}
    seed.update(_seed_from_markdown())

    bind = op.get_bind()
    for slug, pages_read in seed.items():
        bind.execute(
            sa.text(
                "INSERT INTO book_reading_progress (slug, pages_read) "
                "VALUES (:slug, :pages_read)"
            ),
            {"slug": slug, "pages_read": pages_read},
        )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_book_reading_progress_slug"),
        table_name="book_reading_progress",
    )
    op.drop_table("book_reading_progress")
