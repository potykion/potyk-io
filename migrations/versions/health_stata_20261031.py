"""health_stata_items/entries; migrate health_meditations

Revision ID: health_stata_20261031
Revises: health_med_20261030
Create Date: 2026-10-31 15:10:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "health_stata_20261031"
down_revision: Union[str, Sequence[str], None] = "health_med_20261030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MEDITATION_NAME = "Медитация"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "health_stata_items" not in tables:
        op.create_table(
            "health_stata_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
        op.create_index(
            op.f("ix_health_stata_items_name"),
            "health_stata_items",
            ["name"],
            unique=True,
        )

    if "health_stata_entries" not in tables:
        op.create_table(
            "health_stata_entries",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("item_id", sa.Integer(), nullable=False),
            sa.Column("done_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["item_id"], ["health_stata_items.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_health_stata_entries_item_id"),
            "health_stata_entries",
            ["item_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_health_stata_entries_done_at"),
            "health_stata_entries",
            ["done_at"],
            unique=False,
        )

    items = sa.table(
        "health_stata_items",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    entries = sa.table(
        "health_stata_entries",
        sa.column("id", sa.Integer),
        sa.column("item_id", sa.Integer),
        sa.column("done_at", sa.DateTime),
    )

    existing = bind.execute(sa.select(items.c.id).where(items.c.name == MEDITATION_NAME)).first()
    if existing is None:
        bind.execute(items.insert().values(name=MEDITATION_NAME))
        meditation_id = bind.execute(
            sa.select(items.c.id).where(items.c.name == MEDITATION_NAME)
        ).scalar_one()
    else:
        meditation_id = existing[0]

    if "health_meditations" in tables:
        meditations = sa.table(
            "health_meditations",
            sa.column("id", sa.Integer),
            sa.column("done_at", sa.DateTime),
        )
        rows = bind.execute(sa.select(meditations.c.done_at).order_by(meditations.c.id)).fetchall()
        if rows:
            bind.execute(
                entries.insert(),
                [{"item_id": meditation_id, "done_at": row[0]} for row in rows],
            )
        existing_idx = {idx["name"] for idx in inspector.get_indexes("health_meditations")}
        idx_name = op.f("ix_health_meditations_done_at")
        if idx_name in existing_idx:
            op.drop_index(idx_name, table_name="health_meditations")
        op.drop_table("health_meditations")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "health_meditations" not in tables:
        op.create_table(
            "health_meditations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("done_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_health_meditations_done_at"),
            "health_meditations",
            ["done_at"],
            unique=False,
        )

    if "health_stata_items" in tables and "health_stata_entries" in tables:
        items = sa.table(
            "health_stata_items",
            sa.column("id", sa.Integer),
            sa.column("name", sa.String),
        )
        entries = sa.table(
            "health_stata_entries",
            sa.column("id", sa.Integer),
            sa.column("item_id", sa.Integer),
            sa.column("done_at", sa.DateTime),
        )
        meditation_id = bind.execute(
            sa.select(items.c.id).where(items.c.name == MEDITATION_NAME)
        ).scalar()
        if meditation_id is not None:
            meditations = sa.table(
                "health_meditations",
                sa.column("id", sa.Integer),
                sa.column("done_at", sa.DateTime),
            )
            rows = bind.execute(
                sa.select(entries.c.done_at)
                .where(entries.c.item_id == meditation_id)
                .order_by(entries.c.id)
            ).fetchall()
            if rows:
                bind.execute(
                    meditations.insert(),
                    [{"done_at": row[0]} for row in rows],
                )

    if "health_stata_entries" in tables:
        for idx in inspector.get_indexes("health_stata_entries"):
            op.drop_index(idx["name"], table_name="health_stata_entries")
        op.drop_table("health_stata_entries")

    if "health_stata_items" in tables:
        for idx in inspector.get_indexes("health_stata_items"):
            op.drop_index(idx["name"], table_name="health_stata_items")
        op.drop_table("health_stata_items")
