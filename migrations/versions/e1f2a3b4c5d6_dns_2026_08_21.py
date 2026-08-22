"""ДнС 2026-08-21: новости выпуска + тикеры BTC, имя ENGP

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-08-22 14:00:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 8, 21, 20, 0, 0)
SOURCE = "днс-2026-08-21"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-08-21 ДнС Тезисы",
        "datetime": EPISODE_DT,
        "ticker": "Глобал",
        "source": SOURCE,
        "summary": "Новостей нема, неизвестность; хомяки; осенью будет весело",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС IMOEX",
        "datetime": EPISODE_DT,
        "ticker": "IMOEX",
        "source": SOURCE,
        "summary": "ничего интересного",
        "price": "2131",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС RTS",
        "datetime": EPISODE_DT,
        "ticker": "RTSI",
        "source": SOURCE,
        "summary": "ничего интересного",
        "price": "800",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "фиксация, коррекция",
        "price": "113",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "перегрев был => откат; цели 90 к концу года",
        "price": "12.3, 83",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС CIAN",
        "datetime": EPISODE_DT,
        "ticker": "CNRU",
        "source": SOURCE,
        "summary": "хорошо в долгосрок, дивчики",
        "price": "647",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС HEAD",
        "datetime": EPISODE_DT,
        "ticker": "HEAD",
        "source": SOURCE,
        "summary": "отчет нейтрал",
        "price": "2732",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС DOMRF",
        "datetime": EPISODE_DT,
        "ticker": "DOMRF",
        "source": SOURCE,
        "summary": "налог на банки?",
        "price": "2100",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС SBER",
        "datetime": EPISODE_DT,
        "ticker": "SBER",
        "source": SOURCE,
        "summary": "налог на банки?",
        "price": "273",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС GMKN",
        "datetime": EPISODE_DT,
        "ticker": "GMKN",
        "source": SOURCE,
        "summary": "анонс дивов?; ралли в металлах",
        "price": "121",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС RUAL",
        "datetime": EPISODE_DT,
        "ticker": "RUAL",
        "source": SOURCE,
        "summary": "отчет хор; но нет дивов",
        "price": "26",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС ENGP",
        "datetime": EPISODE_DT,
        "ticker": "ENGP",
        "source": SOURCE,
        "summary": "отчет хор, лучше русала; но аккуратно",
        "price": "300",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС BRENT",
        "datetime": EPISODE_DT,
        "ticker": "BRENT",
        "source": SOURCE,
        "summary": "в ожидании адских санкций",
        "price": "92",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС GLD",
        "datetime": EPISODE_DT,
        "ticker": "GLD",
        "source": SOURCE,
        "summary": "дорога на 5000",
        "price": "4482",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-08-21 ДнС BTC",
        "datetime": EPISODE_DT,
        "ticker": "BTC",
        "source": SOURCE,
        "summary": "красавец; фиксировать на 120; техника 60>80>120; коррекция −50% норма; растёт на избегании печатного станка",
        "price": "77к",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
]

NEW_TICKERS: list[dict[str, object]] = [
    {
        "ticker": "BTC",
        "name": "Биткоин",
        "asset_type": "Рынок",
        "sector": "",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
]

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

    op.execute(
        sa.text("UPDATE invest_tickers SET name = 'Эн+' WHERE ticker = 'ENGP' AND name = 'ENGP'"),
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
    for slug in NEWS_SLUGS:
        op.execute(
            sa.text("DELETE FROM invest_news WHERE slug = :slug"),
            {"slug": slug},
        )

    op.execute(sa.text("DELETE FROM invest_tickers WHERE ticker = 'BTC'"))

    op.execute(
        sa.text("UPDATE invest_tickers SET name = 'ENGP' WHERE ticker = 'ENGP' AND name = 'Эн+'"),
    )
