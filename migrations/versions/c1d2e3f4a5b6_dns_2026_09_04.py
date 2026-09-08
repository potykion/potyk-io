"""ДнС 2026-09-04: новости выпуска + name для AFLT, MVID

Revision ID: c1d2e3f4a5b6
Revises: a9b0c1d2e3f4
Create Date: 2026-09-08 15:45:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "a9b0c1d2e3f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 9, 4, 20, 0, 0)
SOURCE = "днс-2026-09-04"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-09-04 ДнС IMOEX",
        "datetime": EPISODE_DT,
        "ticker": "IMOEX",
        "source": SOURCE,
        "summary": "Намеки на разворот, аптренд рано; геополитика (Уиткофф, санкции отложили); сопротивление 2500; 2200–2300 покупать не хочется",
        "price": "2250",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС RTS",
        "datetime": EPISODE_DT,
        "ticker": "RTSI",
        "source": SOURCE,
        "summary": "Хороший уровень для разворота",
        "price": "820",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "Минфин разместил флоатер; рынок долга слабый",
        "price": "113",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС КС",
        "datetime": EPISODE_DT,
        "ticker": "КС",
        "source": SOURCE,
        "summary": "Кажется оставят; фиксы/флоатеры — 16 доха на 2 года топ",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "Откатик, цель до 12.3; уменьшение покупок",
        "price": "12.8, 86",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС MGNT",
        "datetime": EPISODE_DT,
        "ticker": "MGNT",
        "source": SOURCE,
        "summary": "Отчёт −9 млрд убыток, бизнес в плане; капитуляция инвесторов; прокси на снижение КС; +100 через год",
        "price": "1668",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС RTLK",
        "datetime": EPISODE_DT,
        "ticker": "RTLK",
        "source": SOURCE,
        "summary": "Прокси на снижение КС",
        "price": "42.7",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС MVID",
        "datetime": EPISODE_DT,
        "ticker": "MVID",
        "source": SOURCE,
        "summary": "Продавцы с Озона побежали в М.Видео; компания шляпа",
        "price": "46",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС LKOH",
        "datetime": EPISODE_DT,
        "ticker": "LKOH",
        "source": SOURCE,
        "summary": "Отличный отчёт; капекса нет ⇒ роста не будет",
        "price": "5063",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС OZON",
        "datetime": EPISODE_DT,
        "ticker": "OZON",
        "source": SOURCE,
        "summary": "Отыгрыш после распродажи +20%; 2550 пробили и восстановили; Путин про госзакупки через маркетплейсы; хранение в Казахстане; мир-коин",
        "price": "2700",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС AFLT",
        "datetime": EPISODE_DT,
        "ticker": "AFLT",
        "source": SOURCE,
        "summary": "Зеля угрожает, ФНБ купит за 34–35; отчёт спокойный без драйверов; снижение КС ⇒ рост до 50",
        "price": "34",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС PLZL",
        "datetime": EPISODE_DT,
        "ticker": "PLZL",
        "source": SOURCE,
        "summary": "3000 в 2030 — топ идея на 28–29; отчёт полусекретный (добровольный взнос, windfall tax); на полгода неинтересно",
        "price": "980",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС GAZP",
        "datetime": EPISODE_DT,
        "ticker": "GAZP",
        "source": SOURCE,
        "summary": "300 на перемирии; отчёт хороший; цели 110",
        "price": "92",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС SIBN",
        "datetime": EPISODE_DT,
        "ticker": "SIBN",
        "source": SOURCE,
        "summary": "Хор отчёт и дивы",
        "price": "541",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС NVTK",
        "datetime": EPISODE_DT,
        "ticker": "NVTK",
        "source": SOURCE,
        "summary": "Мир-коин; разворотный сигнал; бизнес ок",
        "price": "1025",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС ROSN",
        "datetime": EPISODE_DT,
        "ticker": "ROSN",
        "source": SOURCE,
        "summary": "Уровень 300; мир-коин; Восток Ойл — идея на будущее",
        "price": "320",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-09-04 ДнС HYDR",
        "datetime": EPISODE_DT,
        "ticker": "HYDR",
        "source": SOURCE,
        "summary": "Нет дивов до 2030; хорошая техника",
        "price": "0.36",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
]

NEW_TICKERS: list[dict[str, object]] = []

NAME_UPDATES: list[tuple[str, str, str]] = [
    ("AFLT", "AFLT", "Аэрофлот"),
    ("MVID", "MVID", "М.Видео"),
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
