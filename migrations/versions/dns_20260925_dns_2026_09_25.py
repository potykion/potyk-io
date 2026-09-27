"""ДнС 2026-09-25: новости выпуска

Revision ID: dns_20260925
Revises: dns_20260918
Create Date: 2026-09-27 15:15:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dns_20260925"
down_revision: Union[str, Sequence[str], None] = "dns_20260918"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 9, 25, 20, 0, 0)
SOURCE = "днс-2026-09-25"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-09-25 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "ОФЗ в говне; КС скорее всего оставят",
        "price": "112",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС КС",
        "datetime": EPISODE_DT,
        "ticker": "КС",
        "source": SOURCE,
        "summary": "Скорее всего оставят",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "В следующем году не очень будет",
        "price": "12.5, 84",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС PHOR",
        "datetime": EPISODE_DT,
        "ticker": "PHOR",
        "source": SOURCE,
        "summary": "Windfall tax — посыпались",
        "price": "5054",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС ENGP",
        "datetime": EPISODE_DT,
        "ticker": "ENGP",
        "source": SOURCE,
        "summary": "Windfall tax — посыпались",
        "price": "291.55",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС GMKN",
        "datetime": EPISODE_DT,
        "ticker": "GMKN",
        "source": SOURCE,
        "summary": "Windfall tax — посыпались",
        "price": "118.32",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС PLZL",
        "datetime": EPISODE_DT,
        "ticker": "PLZL",
        "source": SOURCE,
        "summary": "Отыграли налог до этого",
        "price": "1005",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС SBER",
        "datetime": EPISODE_DT,
        "ticker": "SBER",
        "source": SOURCE,
        "summary": "Ничего не происходит",
        "price": "276",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС T",
        "datetime": EPISODE_DT,
        "ticker": "T",
        "source": SOURCE,
        "summary": "Отчёты/фундаментал супер, но падение 7 мес",
        "price": "251",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС CIAN",
        "datetime": EPISODE_DT,
        "ticker": "CNRU",
        "source": SOURCE,
        "summary": "Нормик: айтишка + недвижка + байбек",
        "price": "644",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС HEAD",
        "datetime": EPISODE_DT,
        "ticker": "HEAD",
        "source": SOURCE,
        "summary": "Байбек, нет долга, дивы",
        "price": "2904",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС BAZA",
        "datetime": EPISODE_DT,
        "ticker": "BAZA",
        "source": SOURCE,
        "summary": "Нет долга, айтишка, дивы",
        "price": "105",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС SIBN",
        "datetime": EPISODE_DT,
        "ticker": "SIBN",
        "source": SOURCE,
        "summary": "Прилёты, но аптренд по теханализу",
        "price": "551",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС ROSN",
        "datetime": EPISODE_DT,
        "ticker": "ROSN",
        "source": SOURCE,
        "summary": "Тоже норм",
        "price": "360",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС NVTK",
        "datetime": EPISODE_DT,
        "ticker": "NVTK",
        "source": SOURCE,
        "summary": "Хорошо; дорога на 1300",
        "price": "1052",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС GAZP",
        "datetime": EPISODE_DT,
        "ticker": "GAZP",
        "source": SOURCE,
        "summary": "Надо 110–112, 100 ни о чём; P/E=1; миркоин",
        "price": "98.8",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС LKOH",
        "datetime": EPISODE_DT,
        "ticker": "LKOH",
        "source": SOURCE,
        "summary": "Интрига продажи зарубежных активов; путь на 6200",
        "price": "5374",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-25 ДнС OZON",
        "datetime": EPISODE_DT,
        "ticker": "OZON",
        "source": SOURCE,
        "summary": "Плюсует; хочется 4000",
        "price": "2925",
        "sentiment": "🟢",
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
