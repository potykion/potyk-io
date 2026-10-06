"""game_state, game_foods, game_meals for /game HP

Revision ID: game_hp_20261006
Revises: dns_20260925
Create Date: 2026-10-06 14:40:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "game_hp_20261006"
down_revision: Union[str, Sequence[str], None] = "dns_20260925"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "game_state",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hp", sa.Integer(), nullable=False),
        sa.Column("game_day", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "game_foods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_game_foods_name"), "game_foods", ["name"], unique=True)
    op.create_table(
        "game_meals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("eaten_at", sa.DateTime(), nullable=False),
        sa.Column("meal_type", sa.String(length=32), nullable=False),
        sa.Column("game_day", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_game_meals_eaten_at"), "game_meals", ["eaten_at"], unique=False)
    op.create_index(op.f("ix_game_meals_game_day"), "game_meals", ["game_day"], unique=False)
    op.create_table(
        "game_meal_foods",
        sa.Column("meal_id", sa.Integer(), nullable=False),
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["food_id"], ["game_foods.id"]),
        sa.ForeignKeyConstraint(["meal_id"], ["game_meals.id"]),
        sa.PrimaryKeyConstraint("meal_id", "food_id"),
    )


def downgrade() -> None:
    op.drop_table("game_meal_foods")
    op.drop_index(op.f("ix_game_meals_game_day"), table_name="game_meals")
    op.drop_index(op.f("ix_game_meals_eaten_at"), table_name="game_meals")
    op.drop_table("game_meals")
    op.drop_index(op.f("ix_game_foods_name"), table_name="game_foods")
    op.drop_table("game_foods")
    op.drop_table("game_state")
