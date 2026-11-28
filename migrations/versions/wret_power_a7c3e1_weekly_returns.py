"""Таблица недельных доходностей + сид 13 электроэнергетики × 10 недель

Revision ID: wret_power_a7c3e1
Revises: dns_20261106
Create Date: 2026-11-28 12:40:00.000000

"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "wret_power_a7c3e1"
down_revision: Union[str, Sequence[str], None] = "dns_20261106"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DATA = Path(__file__).resolve().parent / "_data" / "invest_weekly_returns_power_10w.json"
_CHUNK = 200


def _load_rows() -> list[dict]:
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    out: list[dict] = []
    for week_end, ticker, pct, value, volume, close, sector in raw:
        out.append(
            {
                "week_end": date.fromisoformat(week_end),
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
    op.create_table(
        "invest_weekly_returns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("week_end", sa.Date(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("pct", sa.Numeric(10, 4), nullable=False),
        sa.Column("value", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.Column("close", sa.Numeric(18, 6), nullable=True),
        sa.Column("sector", sa.String(length=255), nullable=False, server_default=""),
        sa.UniqueConstraint(
            "week_end",
            "ticker",
            name="uq_invest_weekly_returns_week_ticker",
        ),
    )
    op.create_index(
        "ix_invest_weekly_returns_week_end",
        "invest_weekly_returns",
        ["week_end"],
    )
    op.create_index(
        "ix_invest_weekly_returns_ticker",
        "invest_weekly_returns",
        ["ticker"],
    )
    op.create_index(
        "ix_invest_weekly_returns_sector",
        "invest_weekly_returns",
        ["sector"],
    )
    op.create_index(
        "ix_invest_weekly_returns_pct",
        "invest_weekly_returns",
        ["pct"],
    )

    table = sa.table(
        "invest_weekly_returns",
        sa.column("week_end", sa.Date()),
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
    op.drop_index("ix_invest_weekly_returns_pct", table_name="invest_weekly_returns")
    op.drop_index("ix_invest_weekly_returns_sector", table_name="invest_weekly_returns")
    op.drop_index("ix_invest_weekly_returns_ticker", table_name="invest_weekly_returns")
    op.drop_index("ix_invest_weekly_returns_week_end", table_name="invest_weekly_returns")
    op.drop_table("invest_weekly_returns")
