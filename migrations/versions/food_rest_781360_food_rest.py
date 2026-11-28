"""food_rest table + seed from md restaurants

Revision ID: food_rest_781360
Revises: wret_power_a7c3e1
Create Date: 2026-11-28 15:10:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "food_rest_781360"
down_revision: Union[str, Sequence[str], None] = "wret_power_a7c3e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEED = [
    {
        "name": "KU:",
        "cuisine": "Рамен",
        "tier": "C",
        "logo": "/static/potyk-io/img/restaurants/ku.png",
        "maps_url": "",
    },
    {
        "name": "CVC",
        "cuisine": "Китайская",
        "tier": "B",
        "logo": "/static/potyk-io/img/restaurants/cvc.png",
        "maps_url": "",
    },
    {
        "name": "Mimi",
        "cuisine": "Грузия",
        "tier": "B",
        "logo": "/static/potyk-io/img/restaurants/mimi.jpg",
        "maps_url": "https://yandex.ru/maps/org/mimi/110948331824",
    },
    {
        "name": "Душа лаваша",
        "cuisine": "Чайхона",
        "tier": "",
        "logo": "/static/potyk-io/img/restaurants/dusha-lavasha-interior.jpg",
        "maps_url": "https://yandex.ru/maps/-/CXEBIQ60",
    },
]


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("food_rest"):
        op.create_table(
            "food_rest",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("cuisine", sa.String(length=128), nullable=False),
            sa.Column("tier", sa.String(length=1), nullable=False),
            sa.Column("logo", sa.String(length=1024), nullable=False),
            sa.Column("maps_url", sa.String(length=1024), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_food_rest_cuisine"), "food_rest", ["cuisine"], unique=False)

    count = bind.execute(sa.text("SELECT COUNT(*) FROM food_rest")).scalar() or 0
    if count:
        return

    food_rest = sa.table(
        "food_rest",
        sa.column("name", sa.String),
        sa.column("cuisine", sa.String),
        sa.column("tier", sa.String),
        sa.column("logo", sa.String),
        sa.column("maps_url", sa.String),
    )
    op.bulk_insert(food_rest, SEED)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("food_rest"):
        return
    existing_indexes = {idx["name"] for idx in insp.get_indexes("food_rest")}
    if "ix_food_rest_cuisine" in existing_indexes:
        op.drop_index(op.f("ix_food_rest_cuisine"), table_name="food_rest")
    op.drop_table("food_rest")
