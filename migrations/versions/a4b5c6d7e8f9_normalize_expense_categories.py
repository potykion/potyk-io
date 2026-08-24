"""Normalize expense category names (title case, merge case variants).

Revision ID: a4b5c6d7e8f9
Revises: f3a4b5c6d7e8
Create Date: 2026-08-24 16:20:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a4b5c6d7e8f9"
down_revision: Union[str, Sequence[str], None] = "f3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _normalize_category(category: str) -> str:
    text = (category or "").strip()
    if not text:
        return text
    return text[0].upper() + text[1:].casefold()


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, category FROM expenses")).fetchall()
    for expense_id, category in rows:
        normalized = _normalize_category(category)
        if normalized != category:
            conn.execute(
                sa.text("UPDATE expenses SET category = :category WHERE id = :id"),
                {"category": normalized, "id": expense_id},
            )


def downgrade() -> None:
    pass
