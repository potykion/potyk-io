"""findings watch-later bookmarks

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-08-20 15:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "findings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("watched_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_findings_url"), "findings", ["url"], unique=True)
    op.create_index(op.f("ix_findings_created_at"), "findings", ["created_at"], unique=False)
    op.create_index(op.f("ix_findings_watched_at"), "findings", ["watched_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_findings_watched_at"), table_name="findings")
    op.drop_index(op.f("ix_findings_created_at"), table_name="findings")
    op.drop_index(op.f("ix_findings_url"), table_name="findings")
    op.drop_table("findings")
