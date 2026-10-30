"""health_meditations: log of meditation sessions

Revision ID: health_med_20261030
Revises: anti_posts_20261030
Create Date: 2026-10-30 12:20:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "health_med_20261030"
down_revision: Union[str, Sequence[str], None] = "anti_posts_20261030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "health_meditations" not in inspector.get_table_names():
        op.create_table(
            "health_meditations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("done_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    existing = {idx["name"] for idx in inspector.get_indexes("health_meditations")}
    idx_name = op.f("ix_health_meditations_done_at")
    if idx_name not in existing:
        op.create_index(
            idx_name,
            "health_meditations",
            ["done_at"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "health_meditations" not in inspector.get_table_names():
        return
    existing = {idx["name"] for idx in inspector.get_indexes("health_meditations")}
    idx_name = op.f("ix_health_meditations_done_at")
    if idx_name in existing:
        op.drop_index(idx_name, table_name="health_meditations")
    op.drop_table("health_meditations")
