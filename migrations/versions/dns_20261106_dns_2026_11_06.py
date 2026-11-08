"""ДнС 2026-11-06: новости выпуска + тикеры FIXR/ETLN/облиг

Revision ID: dns_20261106
Revises: dret_seed_nov6_c4e8
Create Date: 2026-11-08 16:30:00.000000
"""

from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "dns_20261106"
down_revision: Union[str, Sequence[str], None] = "dret_seed_nov6_c4e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EPISODE_DT = datetime(2026, 11, 6, 20, 0, 0)
SOURCE = "днс-2026-11-06"
DEFAULT_ACTION = "наблюдать"

NEWS_ROWS: list[dict[str, object]] = [
    {
        "slug": "2026-11-06 ДнС Тезисы",
        "datetime": EPISODE_DT,
        "ticker": "Глобал",
        "source": SOURCE,
        "summary": "18–19.11 возможен позитив",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС IMOEX",
        "datetime": EPISODE_DT,
        "ticker": "IMOEX",
        "source": SOURCE,
        "summary": "Негативная неделя; 2500 взяли, но откат; 2500 очень сложно без драйверов роста и геопозитива",
        "price": "",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС RTS",
        "datetime": EPISODE_DT,
        "ticker": "RTSI",
        "source": SOURCE,
        "summary": "~1000 — работать от уровней; 800 круто",
        "price": "1000",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС RGBI ОФЗ",
        "datetime": EPISODE_DT,
        "ticker": "RGBI",
        "source": SOURCE,
        "summary": "Ничего нового; флоатеры ОФЗ 29008/29009 обгонят денежный рынок на горизонте года",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС CNY",
        "datetime": EPISODE_DT,
        "ticker": "CNY",
        "source": SOURCE,
        "summary": "CNY/USD 12→13, 85–87 — технический отскок будет; девала не особо хочется",
        "price": "12-13, 85-87",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС SIBN",
        "datetime": EPISODE_DT,
        "ticker": "SIBN",
        "source": SOURCE,
        "summary": "Продано",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС HYDR",
        "datetime": EPISODE_DT,
        "ticker": "HYDR",
        "source": SOURCE,
        "summary": "Шикарный отчёт; облиги ключ+2",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС BLNG",
        "datetime": EPISODE_DT,
        "ticker": "BLNG",
        "source": SOURCE,
        "summary": "Трешачок, но сидим",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС PLST",
        "datetime": EPISODE_DT,
        "ticker": "PLST",
        "source": SOURCE,
        "summary": "Свет в конце туннеля появился",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС ETLN",
        "datetime": EPISODE_DT,
        "ticker": "ETLN",
        "source": SOURCE,
        "summary": "Облиги: купоны пока платятся",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС MGKL",
        "datetime": EPISODE_DT,
        "ticker": "MGKL",
        "source": SOURCE,
        "summary": "Горемыка: дефолты, очень рисково — не надо",
        "price": "",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС SBER",
        "datetime": EPISODE_DT,
        "ticker": "SBER",
        "source": SOURCE,
        "summary": "Банки (Сбер/Т/ДомРФ) что-то не растут",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС T",
        "datetime": EPISODE_DT,
        "ticker": "T",
        "source": SOURCE,
        "summary": "Банки не растут; упала на сделке про Циан",
        "price": "",
        "sentiment": "🔴",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС DOMRF",
        "datetime": EPISODE_DT,
        "ticker": "DOMRF",
        "source": SOURCE,
        "summary": "Банки (Сбер/Т/ДомРФ) что-то не растут",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС OZON",
        "datetime": EPISODE_DT,
        "ticker": "OZON",
        "source": SOURCE,
        "summary": "Продано; хороший отчёт",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС POSI",
        "datetime": EPISODE_DT,
        "ticker": "POSI",
        "source": SOURCE,
        "summary": "Красавчик; 1500–1600 продать; добирать на откатиках",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС BAZA",
        "datetime": EPISODE_DT,
        "ticker": "BAZA",
        "source": SOURCE,
        "summary": "Нет долга — кайф",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС HEAD",
        "datetime": EPISODE_DT,
        "ticker": "HEAD",
        "source": SOURCE,
        "summary": "Аутсайдер месяца, но хорошая; дивы есть",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС CIAN",
        "datetime": EPISODE_DT,
        "ticker": "CNRU",
        "source": SOURCE,
        "summary": "Т хочет купить; продавать не надо — байбек и дивы; но что ловить, если цена покупки будет <1000?",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС IRAO",
        "datetime": EPISODE_DT,
        "ticker": "IRAO",
        "source": SOURCE,
        "summary": "Тоже молодцы",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС ALRS",
        "datetime": EPISODE_DT,
        "ticker": "ALRS",
        "source": SOURCE,
        "summary": "Хз почему рост; отчёт не оч",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС GAZP",
        "datetime": EPISODE_DT,
        "ticker": "GAZP",
        "source": SOURCE,
        "summary": "+40 за последнее время — кайф мир-коин; из убытка в прошлом году до прибыли в текущем",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС NVTK",
        "datetime": EPISODE_DT,
        "ticker": "NVTK",
        "source": SOURCE,
        "summary": "Экспорт СПГ рекордный",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС SGZH",
        "datetime": EPISODE_DT,
        "ticker": "SGZH",
        "source": SOURCE,
        "summary": "Мир-коин",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС SNGSP",
        "datetime": EPISODE_DT,
        "ticker": "SNGSP",
        "source": SOURCE,
        "summary": "Узенькая консолидация красивая; дивы жирные от девала",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС VKCO",
        "datetime": EPISODE_DT,
        "ticker": "VKCO",
        "source": SOURCE,
        "summary": "Почва для техотскока; долгосрочно не оч — не раскрывает заработки; долги сокращает; после пампа не идти",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС SMLT",
        "datetime": EPISODE_DT,
        "ticker": "SMLT",
        "source": SOURCE,
        "summary": "Дефолта не будет из‑за реструктуризации; отличный рост на новостях; спекульнуть (бонды→акции)?; мир-коин покруче газика",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС X5",
        "datetime": EPISODE_DT,
        "ticker": "X5",
        "source": SOURCE,
        "summary": "Хороший отчёт; дивы будут, но чуть меньше",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС MGNT",
        "datetime": EPISODE_DT,
        "ticker": "MGNT",
        "source": SOURCE,
        "summary": "Прокси на снижение КС; рост не оч",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС RTLK",
        "datetime": EPISODE_DT,
        "ticker": "RTLK",
        "source": SOURCE,
        "summary": "Прокси на снижение КС",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС FIXR",
        "datetime": EPISODE_DT,
        "ticker": "FIXR",
        "source": SOURCE,
        "summary": "Ликвидность маленькая; поднабрать на коррекции под дивы — нет долгов, есть прибыль; но падает",
        "price": "",
        "sentiment": "🟡",
        "action": DEFAULT_ACTION,
        "content": "",
    },
    {
        "slug": "2026-11-06 ДнС SELG",
        "datetime": EPISODE_DT,
        "ticker": "SELG",
        "source": SOURCE,
        "summary": "Новость-заказуха подбила акции; можно взять на откате",
        "price": "",
        "sentiment": "🟢",
        "action": DEFAULT_ACTION,
        "content": "",
    },
]

NEW_TICKERS: list[dict[str, object]] = [
    {
        "ticker": "FIXR",
        "name": "Фикс Прайс",
        "asset_type": "Акция",
        "sector": "Ритейл",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "ETLN",
        "name": "Эталон",
        "asset_type": "Акция",
        "sector": "Недвига",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "BLNG",
        "name": "Балт лизинг",
        "asset_type": "Рынок",
        "sector": "Облигации",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "PLST",
        "name": "Полипласт",
        "asset_type": "Рынок",
        "sector": "Облигации",
        "dependencies": [],
        "fee": None,
        "management_company": "",
    },
    {
        "ticker": "MGKL",
        "name": "МГКЛ",
        "asset_type": "Рынок",
        "sector": "Облигации",
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
