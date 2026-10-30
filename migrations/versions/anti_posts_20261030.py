"""anti_posts for potyk-anti feed

Revision ID: anti_posts_20261030
Revises: d7507f4e3872
Create Date: 2026-10-30 12:20:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "anti_posts_20261030"
down_revision: Union[str, Sequence[str], None] = "d7507f4e3872"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "anti_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_anti_posts_created_at"),
        "anti_posts",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_anti_posts_created_at"), table_name="anti_posts")
    op.drop_table("anti_posts")
