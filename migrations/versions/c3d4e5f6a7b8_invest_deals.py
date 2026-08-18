"""invest deposit changes and deals

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-18 15:20:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invest_deposit_changes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_invest_deposit_changes_date"),
        "invest_deposit_changes",
        ["date"],
        unique=False,
    )
    op.create_table(
        "invest_deals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("opened_at", sa.DateTime(), nullable=False),
        sa.Column("volume", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("buy_price", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("qty", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("entry_level", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("exit_level", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("take_profit_raw", sa.String(length=32), nullable=False),
        sa.Column("take_profit_price", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("stop_loss_raw", sa.String(length=32), nullable=False),
        sa.Column("stop_loss_price", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("thoughts", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invest_deals_ticker"), "invest_deals", ["ticker"], unique=False)
    op.create_index(
        op.f("ix_invest_deals_opened_at"),
        "invest_deals",
        ["opened_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_invest_deals_opened_at"), table_name="invest_deals")
    op.drop_index(op.f("ix_invest_deals_ticker"), table_name="invest_deals")
    op.drop_table("invest_deals")
    op.drop_index(
        op.f("ix_invest_deposit_changes_date"),
        table_name="invest_deposit_changes",
    )
    op.drop_table("invest_deposit_changes")
