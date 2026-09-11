"""Объединить сектора офз/Флоатеры/РЕПО → Облигации (+ deps)

Revision ID: e9f0a1b2c3d4
Revises: e8f9a0b1c2d3
Create Date: 2026-09-11 15:50:00.000000
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e9f0a1b2c3d4"
down_revision: Union[str, Sequence[str], None] = "e8f9a0b1c2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# sector → Облигации, в dependencies — бывший подтип
TICKER_UPDATES: dict[str, dict[str, object]] = {
    "SBGB": {"sector": "Облигации", "dependencies": ["ОФЗ"]},
    "TOFZ": {"sector": "Облигации", "dependencies": ["ОФЗ"]},
    "SBFR": {"sector": "Облигации", "dependencies": ["Флоатеры"]},
    "TPAY": {"sector": "Облигации", "dependencies": ["Флоатеры"]},
    "LQDT": {"sector": "Облигации", "dependencies": ["РЕПО"]},
    "TMON": {"sector": "Облигации", "dependencies": ["РЕПО"]},
}

TICKER_DOWNGRADE: dict[str, dict[str, object]] = {
    "SBGB": {"sector": "офз", "dependencies": []},
    "TOFZ": {"sector": "офз", "dependencies": []},
    "SBFR": {"sector": "Флоатеры", "dependencies": []},
    "TPAY": {"sector": "Флоатеры", "dependencies": []},
    "LQDT": {"sector": "РЕПО", "dependencies": []},
    "TMON": {"sector": "РЕПО", "dependencies": []},
}


def _apply(updates: dict[str, dict[str, object]]) -> None:
    bind = op.get_bind()
    for ticker, fields in updates.items():
        bind.execute(
            sa.text(
                "UPDATE invest_tickers SET sector = :sector, dependencies = :deps "
                "WHERE ticker = :ticker"
            ),
            {
                "ticker": ticker,
                "sector": fields["sector"],
                "deps": json.dumps(fields["dependencies"], ensure_ascii=False),
            },
        )


def upgrade() -> None:
    _apply(TICKER_UPDATES)


def downgrade() -> None:
    _apply(TICKER_DOWNGRADE)
