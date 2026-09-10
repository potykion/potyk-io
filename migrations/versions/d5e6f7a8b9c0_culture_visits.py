"""culture_visits table + seed from Театры_Мюзиклы.xlsx

Revision ID: d5e6f7a8b9c0
Revises: c1d2e3f4a5b6
Create Date: 2026-09-10 16:00:00.000000

"""
from datetime import date
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEED = [
    {
        "title": "Ничего не бойся, я с тобой",
        "title_url": None,
        "kind": "Мюзикл",
        "author": None,
        "venue": "Мдм",
        "venue_url": None,
        "duration_hours": 3.0,
        "has_intermission": True,
        "visited_at": date(2026, 5, 14),
        "comment": None,
    },
    {
        "title": "Женитьба Бальзаминова",
        "title_url": None,
        "kind": "Спектакль",
        "author": "Островский",
        "venue": "Театр Комедии",
        "venue_url": "https://yandex.ru/maps/org/teatr_komedii/31217187029?si=potyk-io",
        "duration_hours": 2.0,
        "has_intermission": True,
        "visited_at": date(2026, 3, 28),
        "comment": "Простая комедия",
    },
    {
        "title": "Смерть комивояжера",
        "title_url": None,
        "kind": "Спектакль",
        "author": "Артур Миллер",
        "venue": "Воронежский Камерный театр",
        "venue_url": "https://yandex.ru/maps/org/voronezhskiy_kamerny_teatr/1312757484?si=potyk-io",
        "duration_hours": 3.0,
        "has_intermission": True,
        "visited_at": date(2026, 4, 18),
        "comment": None,
    },
    {
        "title": "Мама мимо",
        "title_url": None,
        "kind": "Мюзикл",
        "author": None,
        "venue": "Театр Маска",
        "venue_url": "https://yandex.ru/maps/-/CPgX4GIw",
        "duration_hours": 2.0,
        "has_intermission": False,
        "visited_at": date(2026, 3, 20),
        "comment": None,
    },
    {
        "title": "Машенька",
        "title_url": "https://mossoveta.ru/performance/Mashenka/",
        "kind": "Спектакль",
        "author": None,
        "venue": "Театр Моссовета",
        "venue_url": None,
        "duration_hours": 3.0,
        "has_intermission": True,
        "visited_at": date(2026, 7, 22),
        "comment": None,
    },
]


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("culture_visits"):
        op.create_table(
            "culture_visits",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("title_url", sa.String(length=1024), nullable=True),
            sa.Column("kind", sa.String(length=64), nullable=False),
            sa.Column("author", sa.String(length=255), nullable=True),
            sa.Column("venue", sa.String(length=255), nullable=False),
            sa.Column("venue_url", sa.String(length=1024), nullable=True),
            sa.Column("duration_hours", sa.Float(), nullable=False),
            sa.Column("has_intermission", sa.Boolean(), nullable=False),
            sa.Column("visited_at", sa.Date(), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_culture_visits_kind"), "culture_visits", ["kind"], unique=False)
        op.create_index(
            op.f("ix_culture_visits_visited_at"),
            "culture_visits",
            ["visited_at"],
            unique=False,
        )

    count = bind.execute(sa.text("SELECT COUNT(*) FROM culture_visits")).scalar() or 0
    if count:
        return

    visits = sa.table(
        "culture_visits",
        sa.column("title", sa.String),
        sa.column("title_url", sa.String),
        sa.column("kind", sa.String),
        sa.column("author", sa.String),
        sa.column("venue", sa.String),
        sa.column("venue_url", sa.String),
        sa.column("duration_hours", sa.Float),
        sa.column("has_intermission", sa.Boolean),
        sa.column("visited_at", sa.Date),
        sa.column("comment", sa.Text),
    )
    op.bulk_insert(visits, SEED)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("culture_visits"):
        return
    existing_indexes = {idx["name"] for idx in insp.get_indexes("culture_visits")}
    if "ix_culture_visits_visited_at" in existing_indexes:
        op.drop_index(op.f("ix_culture_visits_visited_at"), table_name="culture_visits")
    if "ix_culture_visits_kind" in existing_indexes:
        op.drop_index(op.f("ix_culture_visits_kind"), table_name="culture_visits")
    op.drop_table("culture_visits")
