"""ДнС 2026-08-28: новости выпуска + тикеры SIBN, TRMK, NMTP, ASTR, FEES

Revision ID: f7a8b9c0d1e2
Revises: b6c7d8e9f0a1
Create Date: 2026-08-29 14:00:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "b6c7d8e9f0a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 8, 28, 20, 0, 0)
SOURCE = "днс-2026-08-28"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-08-28 ДнС Тезисы",
        "datetime": EPISODE_DT,
        "ticker": "Глобал",
        "source": SOURCE,
        "summary": "Осенью: выборы, прилеты, санкции, инфляция",
        "price": "",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС IMOEX",
        "datetime": EPISODE_DT,
        "ticker": "IMOEX",
        "source": SOURCE,
        "summary": "Символический плюс за нефтянку; закрытие сент 2250 — возможный слом; 6 мес падения; крупняка нет; в облигах ~20% — нет риск-премии",
        "price": "2111",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС RTS",
        "datetime": EPISODE_DT,
        "ticker": "RTSI",
        "source": SOURCE,
        "summary": "Негативная картина",
        "price": "778",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "Давление; минфин обещает вернуться; лучше корпораты — фиксы и флоатеры",
        "price": "113",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "Для валюток поздно; цели до 14/90",
        "price": "12.9, 87",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС LKOH",
        "datetime": EPISODE_DT,
        "ticker": "LKOH",
        "source": SOURCE,
        "summary": "Хороший отчёт; 5000 — сильное сопротивление",
        "price": "4569",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС SIBN",
        "datetime": EPISODE_DT,
        "ticker": "SIBN",
        "source": SOURCE,
        "summary": "Хороший отчёт, див-база; почти идеальный разворот",
        "price": "500",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС TATNP",
        "datetime": EPISODE_DT,
        "ticker": "TATNP",
        "source": SOURCE,
        "summary": "Хороший отчёт, див-база",
        "price": "531",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС OZON",
        "datetime": EPISODE_DT,
        "ticker": "OZON",
        "source": SOURCE,
        "summary": "Первый прилет −30% дискретный аук; была лучшая идея; докупить ниже 2000",
        "price": "2193",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС MGNT",
        "datetime": EPISODE_DT,
        "ticker": "MGNT",
        "source": SOURCE,
        "summary": "Слабая картина",
        "price": "1500",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС X5",
        "datetime": EPISODE_DT,
        "ticker": "X5",
        "source": SOURCE,
        "summary": "Держать под дивы; паника от озона",
        "price": "1739",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС AFKS",
        "datetime": EPISODE_DT,
        "ticker": "AFKS",
        "source": SOURCE,
        "summary": "Мать озона => падение; акции слабые, допка",
        "price": "7.4",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС VTBR",
        "datetime": EPISODE_DT,
        "ticker": "VTBR",
        "source": SOURCE,
        "summary": "Исторические лои; слабый отчёт",
        "price": "50",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС ALRS",
        "datetime": EPISODE_DT,
        "ticker": "ALRS",
        "source": SOURCE,
        "summary": "Долги",
        "price": "18.5",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС TRMK",
        "datetime": EPISODE_DT,
        "ticker": "TRMK",
        "source": SOURCE,
        "summary": "Убытки растут",
        "price": "57",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС UPRO",
        "datetime": EPISODE_DT,
        "ticker": "UPRO",
        "source": SOURCE,
        "summary": "Казино; нераспределённые дивы",
        "price": "1",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС FLOT",
        "datetime": EPISODE_DT,
        "ticker": "FLOT",
        "source": SOURCE,
        "summary": "Норм отчёт; но в зоне риска",
        "price": "75",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС HYDR",
        "datetime": EPISODE_DT,
        "ticker": "HYDR",
        "source": SOURCE,
        "summary": "Норм отчёт; но дивов нет",
        "price": "0.33",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС NMTP",
        "datetime": EPISODE_DT,
        "ticker": "NMTP",
        "source": SOURCE,
        "summary": "Растущая история, без долгов, есть кэш, дивы хорошие; но в зоне риска",
        "price": "6.8",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС TRNFP",
        "datetime": EPISODE_DT,
        "ticker": "TRNFP",
        "source": SOURCE,
        "summary": "Всё стабильно, но неинтересно",
        "price": "1019",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС GMKN",
        "datetime": EPISODE_DT,
        "ticker": "GMKN",
        "source": SOURCE,
        "summary": "Дивы 1.5%, годовой мб 8–9%; позитив",
        "price": "119",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС MOEX",
        "datetime": EPISODE_DT,
        "ticker": "MOEX",
        "source": SOURCE,
        "summary": "Всё неплохо, но отток бабла",
        "price": "150",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС POSI",
        "datetime": EPISODE_DT,
        "ticker": "POSI",
        "source": SOURCE,
        "summary": "Айтишка начала показывать хороший результат",
        "price": "937",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС ASTR",
        "datetime": EPISODE_DT,
        "ticker": "ASTR",
        "source": SOURCE,
        "summary": "Айтишка начала показывать хороший результат",
        "price": "211",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС DIAS",
        "datetime": EPISODE_DT,
        "ticker": "DIAS",
        "source": SOURCE,
        "summary": "Айтишка начала показывать хороший результат",
        "price": "1121",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС GEMC",
        "datetime": EPISODE_DT,
        "ticker": "GEMC",
        "source": SOURCE,
        "summary": "До конца года не интересно",
        "price": "592",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС GAZP",
        "datetime": EPISODE_DT,
        "ticker": "GAZP",
        "source": SOURCE,
        "summary": "Миркоин, не интересно",
        "price": "85",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС SELG",
        "datetime": EPISODE_DT,
        "ticker": "SELG",
        "source": SOURCE,
        "summary": "Главное удержать 35",
        "price": "36.8",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС PLZL",
        "datetime": EPISODE_DT,
        "ticker": "PLZL",
        "source": SOURCE,
        "summary": "По 1000 хорошо",
        "price": "1050",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС RAGN",
        "datetime": EPISODE_DT,
        "ticker": "RAGN",
        "source": SOURCE,
        "summary": "Слабый отчёт; сливают после гэпа",
        "price": "72",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС FEES",
        "datetime": EPISODE_DT,
        "ticker": "FEES",
        "source": SOURCE,
        "summary": "Отчёт хор; но риски",
        "price": "0.04",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-28 ДнС CIAN",
        "datetime": EPISODE_DT,
        "ticker": "CNRU",
        "source": SOURCE,
        "summary": "В плюсе за полгода — один из немногих",
        "price": "632",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
]

NEW_TICKERS: list[dict[str, object]] = [
    {
        "ticker": "SIBN",
        "name": "Газпром нефть",
        "asset_type": "Акция",
        "sector": "Нефтянка",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "TRMK",
        "name": "ТМК",
        "asset_type": "Акция",
        "sector": "Металл",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "NMTP",
        "name": "НМТП",
        "asset_type": "Акция",
        "sector": "Транспорт",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "ASTR",
        "name": "Астра",
        "asset_type": "Акция",
        "sector": "ИТ",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "FEES",
        "name": "Россети",
        "asset_type": "Акция",
        "sector": "Комм",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
]

NAME_UPDATES: list[tuple[str, str, str]] = [
    ("AFKS", "AFKS", "АФК Система"),
    ("FLOT", "FLOT", "Совкомфлот"),
    ("GAZP", "GAZP", "Газпром"),
    ("GEMC", "GEMC", "ЮМГ"),
    ("UPRO", "UPRO", "Юнипро"),
]

NEW_TICKER_CODES = [row["ticker"] for row in NEW_TICKERS]
NEWS_SLUGS = [row["slug"] for row in NEWS_ROWS]


def upgrade() -> None:
    bind = op.get_bind()

    tickers_table = sa.table(
        "invest_tickers",
        sa.column("ticker", sa.String(length=64)),
        sa.column("name", sa.String(length=255)),
        sa.column("asset_type", sa.String(length=16)),
        sa.column("sector", sa.String(length=255)),
        sa.column("dependencies", sa.JSON()),
        sa.column("fee", sa.Numeric(precision=8, scale=4)),
        sa.column("management_company", sa.String(length=255)),
    )
    for row in NEW_TICKERS:
        exists = bind.execute(
            sa.text("SELECT 1 FROM invest_tickers WHERE ticker = :ticker"),
            {"ticker": row["ticker"]},
        ).first()
        if not exists:
            op.bulk_insert(tickers_table, [row])

    for ticker, old_name, new_name in NAME_UPDATES:
        bind.execute(
            sa.text(
                "UPDATE invest_tickers SET name = :new_name "
                "WHERE ticker = :ticker AND name = :old_name",
            ),
            {"ticker": ticker, "old_name": old_name, "new_name": new_name},
        )

    news_table = sa.table(
        "invest_news",
        sa.column("slug", sa.String(length=255)),
        sa.column("datetime", sa.DateTime()),
        sa.column("ticker", sa.String(length=64)),
        sa.column("source", sa.String(length=255)),
        sa.column("summary", sa.Text()),
        sa.column("price", sa.String(length=64)),
        sa.column("sentiment", sa.String(length=16)),
        sa.column("action", sa.String(length=32)),
        sa.column("content", sa.Text()),
    )
    op.bulk_insert(news_table, NEWS_ROWS)


def downgrade() -> None:
    bind = op.get_bind()

    for slug in NEWS_SLUGS:
        bind.execute(
            sa.text("DELETE FROM invest_news WHERE slug = :slug"),
            {"slug": slug},
        )

    for ticker in NEW_TICKER_CODES:
        bind.execute(
            sa.text("DELETE FROM invest_tickers WHERE ticker = :ticker"),
            {"ticker": ticker},
        )

    for ticker, old_name, new_name in NAME_UPDATES:
        bind.execute(
            sa.text(
                "UPDATE invest_tickers SET name = :old_name "
                "WHERE ticker = :ticker AND name = :new_name",
            ),
            {"ticker": ticker, "old_name": old_name, "new_name": new_name},
        )
