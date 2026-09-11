"""Поправить сектора и зависимости акций (NLMK, UGLD, …)

Revision ID: d7e8f9a0b1c2
Revises: d6e7f8a9b0c1
Create Date: 2026-09-11 15:00:00.000000
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d7e8f9a0b1c2"
down_revision: Union[str, Sequence[str], None] = "d6e7f8a9b0c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# sector и/или dependencies (dependencies — полный список, не merge)
TICKER_UPDATES: dict[str, dict[str, object]] = {
    "NLMK": {"sector": "Металл"},
    "UGLD": {"sector": "Материалы", "dependencies": ["Золото"]},
    "GAZP": {"sector": "Газ", "dependencies": ["Мир", "Индекс"]},
    "UPRO": {"sector": "Коммуналка", "dependencies": ["Мир"]},
    "LKOH": {"sector": "Нефтянка", "dependencies": ["Индекс"]},
    "MBNK": {"sector": "Фин"},
    "GMKN": {"sector": "Материалы", "dependencies": ["Медь", "Никель"]},
    "SELG": {"sector": "Материалы", "dependencies": ["Золото"]},
}

TICKER_DOWNGRADE: dict[str, dict[str, object]] = {
    "NLMK": {"sector": "Металл, Недвига (стройка), Мир", "dependencies": []},
    "UGLD": {"sector": "Драг (золото)", "dependencies": []},
    "GAZP": {"sector": "Мир, Индекс", "dependencies": []},
    "UPRO": {"sector": "Мир", "dependencies": []},
    "LKOH": {"sector": "Нефтянка, Индекс", "dependencies": []},
    "MBNK": {"sector": "Фин, офз"},
    "GMKN": {"sector": "Драг", "dependencies": []},
    "SELG": {"sector": "Драг", "dependencies": ["Золото"]},
}

SECTOR_RENAME = ("Комм", "Коммуналка")


def _apply_ticker_updates(updates: dict[str, dict[str, object]]) -> None:
    bind = op.get_bind()
    for ticker, fields in updates.items():
        sets: list[str] = []
        params: dict[str, object] = {"ticker": ticker}
        if "sector" in fields:
            sets.append("sector = :sector")
            params["sector"] = fields["sector"]
        if "dependencies" in fields:
            sets.append("dependencies = :deps")
            params["deps"] = json.dumps(fields["dependencies"], ensure_ascii=False)
        if not sets:
            continue
        bind.execute(
            sa.text(f"UPDATE invest_tickers SET {', '.join(sets)} WHERE ticker = :ticker"),
            params,
        )


def upgrade() -> None:
    bind = op.get_bind()
    # Сначала UPRO и остальные тикеры, потом массовый rename Комм → Коммуналка
    # (UPRO уже пишется как Коммуналка).
    _apply_ticker_updates(TICKER_UPDATES)
    old, new = SECTOR_RENAME
    bind.execute(
        sa.text("UPDATE invest_tickers SET sector = :new WHERE sector = :old"),
        {"old": old, "new": new},
    )


def downgrade() -> None:
    bind = op.get_bind()
    old, new = SECTOR_RENAME
    bind.execute(
        sa.text("UPDATE invest_tickers SET sector = :old WHERE sector = :new"),
        {"old": old, "new": new},
    )
    _apply_ticker_updates(TICKER_DOWNGRADE)
