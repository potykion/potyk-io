"""Магаз + Товары → Ритейл

Revision ID: retail_sec_7c3a91
Revises: gche_magaz_56b04a
Create Date: 2026-11-03 16:05:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "retail_sec_7c3a91"
down_revision: Union[str, Sequence[str], None] = "gche_magaz_56b04a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW = "Ритейл"
OLD = ("Магаз", "Товары")

# Downgrade: restore by ticker (Магаз vs Товары)
MAGAZ_TICKERS = ("MGNT", "X5", "LENT", "MVID", "BELU", "FIXP", "GCHE")
TOVARY_TICKERS = ("OZON", "RAGR", "RAGN", "AQUA", "ABRD")


def upgrade() -> None:
    bind = op.get_bind()
    for table in ("invest_tickers", "invest_daily_returns"):
        bind.execute(
            sa.text(
                f"UPDATE {table} SET sector = :new "
                "WHERE sector IN (:a, :b)"
            ),
            {"new": NEW, "a": OLD[0], "b": OLD[1]},
        )


def downgrade() -> None:
    bind = op.get_bind()
    for table in ("invest_tickers", "invest_daily_returns"):
        for ticker in MAGAZ_TICKERS:
            bind.execute(
                sa.text(
                    f"UPDATE {table} SET sector = :sector "
                    "WHERE ticker = :t AND sector = :new"
                ),
                {"sector": "Магаз", "t": ticker, "new": NEW},
            )
        for ticker in TOVARY_TICKERS:
            bind.execute(
                sa.text(
                    f"UPDATE {table} SET sector = :sector "
                    "WHERE ticker = :t AND sector = :new"
                ),
                {"sector": "Товары", "t": ticker, "new": NEW},
            )
