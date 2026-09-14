"""ДнС 2026-09-11: новости выпуска

Revision ID: c4d5e6f7a8b9
Revises: a0b1c2d3e4f5
Create Date: 2026-09-14 13:30:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "a0b1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 9, 11, 20, 0, 0)
SOURCE = "днс-2026-09-11"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-09-11 ДнС IMOEX",
        "datetime": EPISODE_DT,
        "ticker": "IMOEX",
        "source": SOURCE,
        "summary": "1800 < 2200 > 2500",
        "price": "2281",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС RTS",
        "datetime": EPISODE_DT,
        "ticker": "RTSI",
        "source": SOURCE,
        "summary": "Попытки разворота",
        "price": "852",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "Логичный откат после ЦБ КС",
        "price": "113",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС КС",
        "datetime": EPISODE_DT,
        "ticker": "КС",
        "source": SOURCE,
        "summary": "14%",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "Коррекция продолжается; в сентябре ничего, в октябре возможно ослабление рубля",
        "price": "12.5, 84",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС SBER",
        "datetime": EPISODE_DT,
        "ticker": "SBER",
        "source": SOURCE,
        "summary": "Дивы за 26 год ~16%",
        "price": "283",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС OZON",
        "datetime": EPISODE_DT,
        "ticker": "OZON",
        "source": SOURCE,
        "summary": "Прилетик −5%; на долгосрок (6 мес) неплохо",
        "price": "2543",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС BRENT",
        "datetime": EPISODE_DT,
        "ticker": "BRENT",
        "source": SOURCE,
        "summary": "Отличные отчёты у нефтянки; дивы покруче Сбера; трамповня",
        "price": "105",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС TATNP",
        "datetime": EPISODE_DT,
        "ticker": "TATNP",
        "source": SOURCE,
        "summary": "Топ для лонг-инвеста",
        "price": "593",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС LKOH",
        "datetime": EPISODE_DT,
        "ticker": "LKOH",
        "source": SOURCE,
        "summary": "Топ для лонг-инвеста",
        "price": "5262",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС SIBN",
        "datetime": EPISODE_DT,
        "ticker": "SIBN",
        "source": SOURCE,
        "summary": "Топ для лонг-инвеста",
        "price": "547",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС ROSN",
        "datetime": EPISODE_DT,
        "ticker": "ROSN",
        "source": SOURCE,
        "summary": "Позитив — Восток Ойл; <385 вкусно",
        "price": "352",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС NVTK",
        "datetime": EPISODE_DT,
        "ticker": "NVTK",
        "source": SOURCE,
        "summary": "Экспорт растёт; цена газа для Европы 1500$",
        "price": "1040",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС GAZP",
        "datetime": EPISODE_DT,
        "ticker": "GAZP",
        "source": SOURCE,
        "summary": "Мир-коин — хорошо на новостях",
        "price": "92.7",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС RAGN",
        "datetime": EPISODE_DT,
        "ticker": "RAGN",
        "source": SOURCE,
        "summary": "Мировой дефицит жрачки; но бомбят зерновозы",
        "price": "70",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-11 ДнС BTC",
        "datetime": EPISODE_DT,
        "ticker": "BTC",
        "source": SOURCE,
        "summary": "",
        "price": "70k",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
]

NEW_TICKERS: list[dict[str, object]] = []

NAME_UPDATES: list[tuple[str, str, str]] = []

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
