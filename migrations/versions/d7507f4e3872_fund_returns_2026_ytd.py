"""Обновить доходности фондов за 2026 (YTD по свечам T-Invest ~2026-10-23)

Revision ID: d7507f4e3872
Revises: dns_20261016
Create Date: 2026-10-23 15:30:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d7507f4e3872"
down_revision: Union[str, Sequence[str], None] = "dns_20261016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

YEAR = 2026

# ticker → return_pct; цена YE2025 → close ~2026-10-23 (TQBR; TLCN — NAV)
RETURNS_2026: list[tuple[str, str]] = [
    ("AKGD", "-6.7"),
    ("AKMB", "6.6"),
    ("AKME", "-6.9"),
    ("AKQU", "-6.5"),
    ("EQMX", "-4.7"),
    ("GOLD", "-2.6"),
    ("LQDT", "12.1"),
    ("OBLG", "11.5"),
    ("RU000A104172", "2.7"),
    ("RU000A109KH9", "3.4"),
    ("RU000A109KS6", "0.4"),
    ("SAFE", "12.4"),
    ("SBBY", "9.9"),
    ("SBCB", "1.0"),
    ("SBCN", "9.1"),
    ("SBFR", "12.9"),
    ("SBGB", "3.3"),
    ("SBGD", "-6.4"),
    ("SBMX", "-4.8"),
    ("SBRB", "9.8"),
    ("SBRI", "-10.1"),
    ("TBRU", "10.5"),
    ("TDIV", "-1.0"),
    ("TGLD", "-6.7"),
    ("TIND", "-2.1"),
    ("TITR", "-14.6"),
    ("TLCB", "5.4"),
    ("TLCN", "5.9"),
    ("TMON", "11.2"),
    ("TMOS", "-4.5"),
    ("TOFZ", "2.3"),
    ("TPAY", "2.0"),
    ("TRND", "-7.7"),
]

# значения из исходного seed (b6c7d8e9f0a1) — для downgrade
PREVIOUS_2026: list[tuple[str, str]] = [
    ("AKMB", "6.30"),
    ("AKME", "-17.30"),
    ("AKQU", "-16.20"),
    ("EQMX", "-16.00"),
    ("GOLD", "8.40"),
    ("LQDT", "9.80"),
    ("OBLG", "8.80"),
    ("RU000A104172", "-7.00"),
    ("RU000A109KH9", "-0.10"),
    ("RU000A109KS6", "-4.50"),
    ("SAFE", "9.50"),
    ("SBBY", "12.70"),
    ("SBCB", "5.80"),
    ("SBCN", "14.00"),
    ("SBFR", "10.00"),
    ("SBGB", "2.80"),
    ("SBMX", "-16.00"),
    ("SBRB", "7.80"),
    ("SBRI", "-16.10"),
    ("TBRU", "8.30"),
    ("TDIV", "-8.70"),
    ("TIND", "0.00"),
    ("TITR", "-20.90"),
    ("TLCB", "9.10"),
    ("TLCN", "4.70"),
    ("TMON", "9.10"),
    ("TMOS", "-16.10"),
    ("TOFZ", "2.90"),
    ("TPAY", "1.20"),
    ("TRND", "-15.90"),
]

NEW_IN_THIS_MIGRATION = ("AKGD", "SBGD", "TGLD")


def _upsert(bind, ticker: str, value: str) -> None:
    exists = bind.execute(
        sa.text(
            "SELECT 1 FROM invest_fund_returns WHERE ticker = :ticker AND year = :year"
        ),
        {"ticker": ticker, "year": YEAR},
    ).first()
    params = {"ticker": ticker, "year": YEAR, "return_pct": float(value)}
    if exists:
        bind.execute(
            sa.text(
                "UPDATE invest_fund_returns SET return_pct = :return_pct "
                "WHERE ticker = :ticker AND year = :year"
            ),
            params,
        )
    else:
        bind.execute(
            sa.text(
                "INSERT INTO invest_fund_returns (ticker, year, return_pct) "
                "VALUES (:ticker, :year, :return_pct)"
            ),
            params,
        )


def upgrade() -> None:
    bind = op.get_bind()
    for ticker, value in RETURNS_2026:
        _upsert(bind, ticker, value)


def downgrade() -> None:
    bind = op.get_bind()
    for ticker in NEW_IN_THIS_MIGRATION:
        bind.execute(
            sa.text(
                "DELETE FROM invest_fund_returns WHERE ticker = :ticker AND year = :year"
            ),
            {"ticker": ticker, "year": YEAR},
        )
    for ticker, value in PREVIOUS_2026:
        _upsert(bind, ticker, value)
