"""Таблица дневных доходностей акций (MOEX TQBR)

Revision ID: invest_dret_95002c
Revises: health_stata_kind_20261101
Create Date: 2026-11-03 14:45:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "invest_dret_95002c"
down_revision: Union[str, Sequence[str], None] = "health_stata_kind_20261101"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invest_daily_returns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("pct", sa.Numeric(10, 4), nullable=False),
        sa.Column("value", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.Column("close", sa.Numeric(18, 6), nullable=True),
        sa.Column("sector", sa.String(length=255), nullable=False, server_default=""),
        sa.UniqueConstraint(
            "trade_date",
            "ticker",
            name="uq_invest_daily_returns_date_ticker",
        ),
    )
    op.create_index(
        "ix_invest_daily_returns_trade_date",
        "invest_daily_returns",
        ["trade_date"],
    )
    op.create_index(
        "ix_invest_daily_returns_ticker",
        "invest_daily_returns",
        ["ticker"],
    )
    op.create_index(
        "ix_invest_daily_returns_sector",
        "invest_daily_returns",
        ["sector"],
    )
    op.create_index(
        "ix_invest_daily_returns_pct",
        "invest_daily_returns",
        ["pct"],
    )


def downgrade() -> None:
    op.drop_index("ix_invest_daily_returns_pct", table_name="invest_daily_returns")
    op.drop_index("ix_invest_daily_returns_sector", table_name="invest_daily_returns")
    op.drop_index("ix_invest_daily_returns_ticker", table_name="invest_daily_returns")
    op.drop_index("ix_invest_daily_returns_trade_date", table_name="invest_daily_returns")
    op.drop_table("invest_daily_returns")
