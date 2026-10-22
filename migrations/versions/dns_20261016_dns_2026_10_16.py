"""ДнС 2026-10-16: новости выпуска + тикер DATA

Revision ID: dns_20261016
Revises: dns_20261010
Create Date: 2026-10-22 16:40:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dns_20261016"
down_revision: Union[str, Sequence[str], None] = "dns_20261010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 10, 16, 20, 0, 0)
SOURCE = "днс-2026-10-16"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-10-16 ДнС IMOEX",
        "datetime": EPISODE_DT,
        "ticker": "IMOEX",
        "source": SOURCE,
        "summary": "В зелёной зоне; дорога на 2500 — серьёзное сопротивление",
        "price": "2423",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС RTS",
        "datetime": EPISODE_DT,
        "ticker": "RTSI",
        "source": SOURCE,
        "summary": "800 — мощнейший разворотный уровень; цель к 1000",
        "price": "900",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "Рубль укрепляется: покупки валюты минфина меньше продаж экспортёров",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "Чуть ожил; 110 — хороший уровень входа; удивительно на фоне ускоряющейся инфляции; позитив для акций",
        "price": "111.67",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС Тезисы",
        "datetime": EPISODE_DT,
        "ticker": "Глобал",
        "source": SOURCE,
        "summary": "Дизельная сделка: частичное снятие санкций; атаки на дата-центры — несмотря на негатив, всё спокойно",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС ROSN",
        "datetime": EPISODE_DT,
        "ticker": "ROSN",
        "source": SOURCE,
        "summary": "385 — сопротивление; бенефициар дизеля; рост: Восток Ойл",
        "price": "365",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС LKOH",
        "datetime": EPISODE_DT,
        "ticker": "LKOH",
        "source": SOURCE,
        "summary": "Весь позитив отыграл, в т.ч. зарубежные активы; второй по дизелю",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС SIBN",
        "datetime": EPISODE_DT,
        "ticker": "SIBN",
        "source": SOURCE,
        "summary": "3-е место по дизелю",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС SNGSP",
        "datetime": EPISODE_DT,
        "ticker": "SNGSP",
        "source": SOURCE,
        "summary": "Совсем убитый, апсайд есть",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС TATNP",
        "datetime": EPISODE_DT,
        "ticker": "TATNP",
        "source": SOURCE,
        "summary": "Всё отыграно",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС FLOT",
        "datetime": EPISODE_DT,
        "ticker": "FLOT",
        "source": SOURCE,
        "summary": "Сильно погоду не делает",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС YDEX",
        "datetime": EPISODE_DT,
        "ticker": "YDEX",
        "source": SOURCE,
        "summary": "Облако не сильно в доле выручки; несмотря на атаки ЦОД — спокойно",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС SBER",
        "datetime": EPISODE_DT,
        "ticker": "SBER",
        "source": SOURCE,
        "summary": "Недостроенный ЦОД; атаки — спокойно",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС VKCO",
        "datetime": EPISODE_DT,
        "ticker": "VKCO",
        "source": SOURCE,
        "summary": "Хочется; кто-то ушёл с Яндекса к ним",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС DATA",
        "datetime": EPISODE_DT,
        "ticker": "DATA",
        "source": SOURCE,
        "summary": "Логики нет",
        "price": "",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС BAZA",
        "datetime": EPISODE_DT,
        "ticker": "BAZA",
        "source": SOURCE,
        "summary": "Софт для серверов ⇒ закономерный рост после Яндекса",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС RTLK",
        "datetime": EPISODE_DT,
        "ticker": "RTLK",
        "source": SOURCE,
        "summary": "РТК ЦОД — драйвер роста; гос. игрок; на дне; долг большой ⇒ ставка на снижение КС",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС TRNFP",
        "datetime": EPISODE_DT,
        "ticker": "TRNFP",
        "source": SOURCE,
        "summary": "Неприятная новость по тарифам; хорошие дивы, но низкая индексация — роста не предвидится",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС GAZP",
        "datetime": EPISODE_DT,
        "ticker": "GAZP",
        "source": SOURCE,
        "summary": "Восстанавливается и растёт; сопротивление 112; мир-коин",
        "price": "112",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС OZON",
        "datetime": EPISODE_DT,
        "ticker": "OZON",
        "source": SOURCE,
        "summary": "Цель 3700",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС AFKS",
        "datetime": EPISODE_DT,
        "ticker": "AFKS",
        "source": SOURCE,
        "summary": "Продажа Медси Альфе",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС PLZL",
        "datetime": EPISODE_DT,
        "ticker": "PLZL",
        "source": SOURCE,
        "summary": "Хорошая цена без дивов",
        "price": "1400",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС X5",
        "datetime": EPISODE_DT,
        "ticker": "X5",
        "source": SOURCE,
        "summary": "Хороший отчёт ⇒ Магнит тоже рад",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС MGNT",
        "datetime": EPISODE_DT,
        "ticker": "MGNT",
        "source": SOURCE,
        "summary": "Рад хорошему отчёту X5; прокси на снижение КС",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-10-16 ДнС POSI",
        "datetime": EPISODE_DT,
        "ticker": "POSI",
        "source": SOURCE,
        "summary": "Пошли в сегмент B2C — позитив; таргет 1400–1500",
        "price": "1450",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
]

NEW_TICKERS: list[dict[str, object]] = [
    {
        "ticker": "DATA",
        "name": "Аренадата",
        "asset_type": "Акция",
        "sector": "ИТ",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
]

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
