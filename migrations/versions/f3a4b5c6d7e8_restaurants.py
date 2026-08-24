"""restaurants table + seed from potyk-food/rest guide

Revision ID: f3a4b5c6d7e8
Revises: e1f2a3b4c5d6
Create Date: 2026-08-24 13:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEED = [
    {
        "name": "Суп-кафе",
        "maps_url": "https://yandex.ru/maps/-/CPF~MEj8",
        "metro": "Белорусская",
        "tags": ["супчики"],
    },
    {
        "name": "She",
        "maps_url": "https://yandex.ru/maps/-/CPF~MEj8",
        "metro": "Белорусская",
        "tags": ["азия", "средиземноморская"],
    },
    {
        "name": "Torro",
        "maps_url": "https://yandex.ru/maps/-/CPF~M6OK",
        "metro": "Белорусская",
        "tags": ["мясо"],
    },
    {
        "name": "Boston",
        "maps_url": "https://yandex.ru/maps/-/CPF~MWnR",
        "metro": "Белорусская",
        "tags": ["креветки"],
    },
    {
        "name": "Steak it easy",
        "maps_url": "https://yandex.ru/maps/-/CPF~MDP8",
        "metro": "Белорусская",
        "tags": ["мясо"],
    },
    {
        "name": "The Бык",
        "maps_url": "https://yandex.ru/maps/-/CPF~QKiA",
        "metro": "Белорусская",
        "tags": ["мясо"],
    },
    {
        "name": "Ломи",
        "maps_url": "https://yandex.ru/maps/-/CPF~UAL2",
        "metro": "Белорусская",
        "tags": ["грузия"],
    },
    {
        "name": "Тхали и карри",
        "maps_url": "https://yandex.ru/maps/-/CPF~IA2Q",
        "metro": "Пушкинская / Тверская / Чеховская",
        "tags": ["индийка"],
    },
]


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("restaurants"):
        op.create_table(
            "restaurants",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("maps_url", sa.String(length=1024), nullable=False),
            sa.Column("metro", sa.String(length=128), nullable=False, server_default=""),
            sa.Column("tags", sa.JSON(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_restaurants_metro"), "restaurants", ["metro"], unique=False)

    count = bind.execute(sa.text("SELECT COUNT(*) FROM restaurants")).scalar() or 0
    if count:
        return

    restaurants = sa.table(
        "restaurants",
        sa.column("name", sa.String),
        sa.column("maps_url", sa.String),
        sa.column("metro", sa.String),
        sa.column("tags", sa.JSON),
    )
    op.bulk_insert(restaurants, SEED)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("restaurants"):
        return
    existing_indexes = {idx["name"] for idx in insp.get_indexes("restaurants")}
    if "ix_restaurants_metro" in existing_indexes:
        op.drop_index(op.f("ix_restaurants_metro"), table_name="restaurants")
    op.drop_table("restaurants")
