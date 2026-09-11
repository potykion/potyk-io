"""Названия фондов из T-Invest + TITR сектор Акции

Revision ID: e8f9a0b1c2d3
Revises: d7e8f9a0b1c2
Create Date: 2026-09-11 15:40:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e8f9a0b1c2d3"
down_revision: Union[str, Sequence[str], None] = "d7e8f9a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# name было равно ticker — берём название из T-Invest
FUND_NAMES: dict[str, str] = {
    "AKGD": "Альфа-Капитал Золото",
    "AKMB": "Альфа-Капитал Управляемые облигации",
    "EQMX": "ВИМ – Индекс МосБиржи",
    "GOLD": "ВИМ – Фонд Золото",
    "LQDT": "ВИМ – Ликвидность",
    "OBLG": "ВИМ – Корпоративные облигации",
    "SAFE": "Первая – Фонд Консервативный смарт",
    "SBBY": "Первая – Фонд Инструменты в юанях",
    "SBCB": "Первая – Фонд Валютных Облигаций",
    "SBCN": "Первая – Фонд Сберегательный в юанях",
    "SBFR": "Первая – Фонд Облигации с переменным купоном",
    "SBGB": "Первая – Фонд Государственные облигации",
    "SBGD": "Первая – Фонд Доступное золото",
    "SBMX": "Первая – Фонд Топ Российских акций",
    "SBRB": "Первая – Фонд Корпоративные облигации",
    "SBRI": "Первая – Фонд Ответственные инвестиции",
    "TBRU": "Российские облигации",
    "TGLD": "Золото",
    "TLCB": "Локальные валютные облигации",
    "TMON": "Денежный рынок",
    "TMOS": "Крупнейшие компании РФ",
    "TOFZ": "Т-Капитал ОФЗ",
    "TPAY": "Пассивный доход",
}

FUND_NAMES_DOWN: dict[str, str] = {ticker: ticker for ticker in FUND_NAMES}

TITR_SECTOR_UP = ("TITR", "ИТ", "Акции")
TITR_SECTOR_DOWN = ("TITR", "Акции", "ИТ")


def upgrade() -> None:
    bind = op.get_bind()
    for ticker, name in FUND_NAMES.items():
        bind.execute(
            sa.text("UPDATE invest_tickers SET name = :name WHERE ticker = :ticker"),
            {"ticker": ticker, "name": name},
        )
    ticker, _old, new = TITR_SECTOR_UP
    bind.execute(
        sa.text("UPDATE invest_tickers SET sector = :sector WHERE ticker = :ticker"),
        {"ticker": ticker, "sector": new},
    )


def downgrade() -> None:
    bind = op.get_bind()
    ticker, _old, new = TITR_SECTOR_DOWN
    bind.execute(
        sa.text("UPDATE invest_tickers SET sector = :sector WHERE ticker = :ticker"),
        {"ticker": ticker, "sector": new},
    )
    for ticker, name in FUND_NAMES_DOWN.items():
        bind.execute(
            sa.text("UPDATE invest_tickers SET name = :name WHERE ticker = :ticker"),
            {"ticker": ticker, "name": name},
        )
