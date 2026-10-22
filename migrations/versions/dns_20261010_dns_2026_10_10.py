"""ДнС 2026-10-10: новости выпуска

Revision ID: dns_20261010
Revises: dns_20261002
Create Date: 2026-10-22 16:35:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dns_20261010"
down_revision: Union[str, Sequence[str], None] = "dns_20261002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 10, 10, 20, 0, 0)
SOURCE = "днс-2026-10-10"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-10-10 ДнС Тезисы",
        "datetime": EPISODE_DT,
        "ticker": "Глобал",
        "source": SOURCE,
        "summary": "Трамп; погоду делает ЦБ; дефолты растут",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС КС",
        "datetime": EPISODE_DT,
        "ticker": "КС",
        "source": SOURCE,
        "summary": "Вряд ли поднимут, но и не опустят",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "Индексация тарифов ЖКХ ⇒ взлёт инфляции ⇒ RGBI падает; ОФЗ 17% доха — неплохо",
        "price": "110",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС IMOEX",
        "datetime": EPISODE_DT,
        "ticker": "IMOEX",
        "source": SOURCE,
        "summary": "Расти только на геополитике, а так апатия",
        "price": "2300",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "Приличные объёмы покупки валюты ~12 млрд/день; серьёзной девальвации не будет; ренж 12–13 / 80–87; лучше фиксы/флоатеры, чем валютки",
        "price": "12.5, 83.5",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС PLZL",
        "datetime": EPISODE_DT,
        "ticker": "PLZL",
        "source": SOURCE,
        "summary": "Ожил; 900–1000 — хороший уровень входа, держать до 2030",
        "price": "950",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС T",
        "datetime": EPISODE_DT,
        "ticker": "T",
        "source": SOURCE,
        "summary": "Чуть отрос",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС X5",
        "datetime": EPISODE_DT,
        "ticker": "X5",
        "source": SOURCE,
        "summary": "Рост под дивы, держать и после; стабильный понятный бизнес",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС POSI",
        "datetime": EPISODE_DT,
        "ticker": "POSI",
        "source": SOURCE,
        "summary": "+5%; 1300–1400 продавать, хочется добрать у ~1000",
        "price": "1350",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС LKOH",
        "datetime": EPISODE_DT,
        "ticker": "LKOH",
        "source": SOURCE,
        "summary": "Хорошие дивы",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС SBER",
        "datetime": EPISODE_DT,
        "ticker": "SBER",
        "source": SOURCE,
        "summary": "Хорошие дивы",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС GAZP",
        "datetime": EPISODE_DT,
        "ticker": "GAZP",
        "source": SOURCE,
        "summary": "Около 100, надо 110",
        "price": "100",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС SIBN",
        "datetime": EPISODE_DT,
        "ticker": "SIBN",
        "source": SOURCE,
        "summary": "Хорошо; дивы как в Сбере ~15%",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС SPBE",
        "datetime": EPISODE_DT,
        "ticker": "SPBE",
        "source": SOURCE,
        "summary": "+15%, непонятно почему рост",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС GLRX",
        "datetime": EPISODE_DT,
        "ticker": "GLRX",
        "source": SOURCE,
        "summary": "Рост, непонятно почему",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС SELG",
        "datetime": EPISODE_DT,
        "ticker": "SELG",
        "source": SOURCE,
        "summary": "Хороший момент для входа был",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС GMKN",
        "datetime": EPISODE_DT,
        "ticker": "GMKN",
        "source": SOURCE,
        "summary": "Windfall tax",
        "price": "",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС YDEX",
        "datetime": EPISODE_DT,
        "ticker": "YDEX",
        "source": SOURCE,
        "summary": "Прилёты по дата-центрам; −7% за пару дней; дорого, по 3000 норм; непонятно на чём расти",
        "price": "3400",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС SMLT",
        "datetime": EPISODE_DT,
        "ticker": "SMLT",
        "source": SOURCE,
        "summary": "Сбер в помощь, банкротить не хотят",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-10 ДнС MDMG",
        "datetime": EPISODE_DT,
        "ticker": "MDMG",
        "source": SOURCE,
        "summary": "Капекс нелогичный, мб порежут дивы",
        "price": "",
        "sentiment": "🔴",
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
