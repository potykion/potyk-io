"""invest ticker levels

Revision ID: a5b6c7d8e9f0
Revises: a4b5c6d7e8f9
Create Date: 2026-09-02 13:50:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a5b6c7d8e9f0"
down_revision: Union[str, Sequence[str], None] = "a4b5c6d7e8f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invest_ticker_levels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("entry_level", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("exit_level", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker"),
    )
    op.create_index(
        op.f("ix_invest_ticker_levels_ticker"),
        "invest_ticker_levels",
        ["ticker"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_invest_ticker_levels_ticker"), table_name="invest_ticker_levels")
    op.drop_table("invest_ticker_levels")
