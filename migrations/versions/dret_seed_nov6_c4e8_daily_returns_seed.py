"""Сид дневных доходностей TQBR (окт 2026 + 1–6 ноя 2026)

Revision ID: dret_seed_nov6_c4e8
Revises: retail_sec_7c3a91
Create Date: 2026-11-07 12:20:00.000000

"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dret_seed_nov6_c4e8"
down_revision: Union[str, Sequence[str], None] = "retail_sec_7c3a91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DATA = Path(__file__).resolve().parent / "_data" / "invest_daily_returns_oct_nov6_2026.json"
_DATE_MIN = "2026-10-01"
_DATE_MAX = "2026-11-06"
_CHUNK = 500


def _load_rows() -> list[dict]:
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    out: list[dict] = []
    for trade_date, ticker, pct, value, volume, close, sector in raw:
        out.append(
            {
                "trade_date": date.fromisoformat(trade_date),
                "ticker": ticker,
                "pct": pct,
                "value": value,
                "volume": volume,
                "close": close,
                "sector": sector or "",
            }
        )
    return out


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "DELETE FROM invest_daily_returns "
            "WHERE trade_date >= :a AND trade_date <= :b"
        ),
        {"a": _DATE_MIN, "b": _DATE_MAX},
    )
    table = sa.table(
        "invest_daily_returns",
        sa.column("trade_date", sa.Date()),
        sa.column("ticker", sa.String(length=32)),
        sa.column("pct", sa.Numeric(10, 4)),
        sa.column("value", sa.Numeric(18, 2)),
        sa.column("volume", sa.BigInteger()),
        sa.column("close", sa.Numeric(18, 6)),
        sa.column("sector", sa.String(length=255)),
    )
    rows = _load_rows()
    for i in range(0, len(rows), _CHUNK):
        op.bulk_insert(table, rows[i : i + _CHUNK])


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "DELETE FROM invest_daily_returns "
            "WHERE trade_date >= :a AND trade_date <= :b"
        ),
        {"a": _DATE_MIN, "b": _DATE_MAX},
    )
