"""health_stata_items.kind + seed achievement

Revision ID: health_stata_kind_20261101
Revises: health_stata_20261031
Create Date: 2026-11-01 12:20:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "health_stata_kind_20261101"
down_revision: Union[str, Sequence[str], None] = "health_stata_20261031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ACHIEVEMENT_FACE = "Не трогал лицо"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("health_stata_items")}
    if "kind" not in cols:
        with op.batch_alter_table("health_stata_items") as batch:
            batch.add_column(
                sa.Column(
                    "kind",
                    sa.String(length=32),
                    nullable=False,
                    server_default="deed",
                )
            )
            batch.create_index("ix_health_stata_items_kind", ["kind"], unique=False)

    items = sa.table(
        "health_stata_items",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("kind", sa.String),
    )
    existing = bind.execute(
        sa.select(items.c.id).where(items.c.name == ACHIEVEMENT_FACE)
    ).first()
    if existing is None:
        bind.execute(items.insert().values(name=ACHIEVEMENT_FACE, kind="achievement"))


def downgrade() -> None:
    bind = op.get_bind()
    items = sa.table(
        "health_stata_items",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("kind", sa.String),
    )
    face_id = bind.execute(
        sa.select(items.c.id).where(items.c.name == ACHIEVEMENT_FACE)
    ).scalar()
    if face_id is not None:
        entries = sa.table(
            "health_stata_entries",
            sa.column("id", sa.Integer),
            sa.column("item_id", sa.Integer),
        )
        bind.execute(entries.delete().where(entries.c.item_id == face_id))
        bind.execute(items.delete().where(items.c.id == face_id))

    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("health_stata_items")}
    if "kind" in cols:
        with op.batch_alter_table("health_stata_items") as batch:
            batch.drop_index("ix_health_stata_items_kind")
            batch.drop_column("kind")
