"""GCHE → сектор Магаз (+ справочник тикеров)

Revision ID: gche_magaz_56b04a
Revises: invest_dret_95002c
Create Date: 2026-11-03 15:35:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "gche_magaz_56b04a"
down_revision: Union[str, Sequence[str], None] = "invest_dret_95002c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TICKER = "GCHE"
NAME = "Черкизово"
SECTOR = "Магаз"
OLD_SECTOR = "Материалы"


def upgrade() -> None:
    bind = op.get_bind()
    tickers = sa.table(
        "invest_tickers",
        sa.column("ticker", sa.String(length=64)),
        sa.column("name", sa.String(length=255)),
        sa.column("asset_type", sa.String(length=16)),
        sa.column("sector", sa.String(length=255)),
        sa.column("dependencies", sa.JSON()),
        sa.column("fee", sa.Numeric(precision=8, scale=4)),
        sa.column("management_company", sa.String(length=255)),
    )
    exists = bind.execute(
        sa.text("SELECT 1 FROM invest_tickers WHERE ticker = :t"),
        {"t": TICKER},
    ).first()
    if exists:
        bind.execute(
            sa.text("UPDATE invest_tickers SET sector = :sector WHERE ticker = :t"),
            {"sector": SECTOR, "t": TICKER},
        )
    else:
        op.bulk_insert(
            tickers,
            [
                {
                    "ticker": TICKER,
                    "name": NAME,
                    "asset_type": "Акция",
                    "sector": SECTOR,
                    "dependencies": [],
                    "fee": None,
                    "management_company": "",
                }
            ],
        )

    bind.execute(
        sa.text(
            "UPDATE invest_daily_returns SET sector = :sector WHERE ticker = :t"
        ),
        {"sector": SECTOR, "t": TICKER},
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE invest_daily_returns SET sector = :sector WHERE ticker = :t"
        ),
        {"sector": OLD_SECTOR, "t": TICKER},
    )
    bind.execute(
        sa.text("UPDATE invest_tickers SET sector = :sector WHERE ticker = :t"),
        {"sector": OLD_SECTOR, "t": TICKER},
    )
