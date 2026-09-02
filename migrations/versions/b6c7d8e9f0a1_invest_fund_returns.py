"""invest fund returns + seed from favorite-funds CSV

Revision ID: b6c7d8e9f0a1
Revises: a5b6c7d8e9f0
Create Date: 2026-09-02 15:00:00.000000

"""
from __future__ import annotations

from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b6c7d8e9f0a1"
down_revision: Union[str, Sequence[str], None] = "a5b6c7d8e9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_TICKERS: list[dict[str, object]] = [
    {
        "ticker": "RU000A109KH9",
        "name": "Т-Капитал Баланс",
        "asset_type": "Фонд",
        "sector": "Смешанные",
        "dependencies": [],
        "fee": None,
        "management_company": "Т-Капитал",
    },
    {
        "ticker": "RU000A109KS6",
        "name": "Т-Капитал Компании второго эшелона",
        "asset_type": "Фонд",
        "sector": "Акции",
        "dependencies": [],
        "fee": None,
        "management_company": "Т-Капитал",
    },
    {
        "ticker": "RU000A104172",
        "name": "ПАРУС-СБЛ",
        "asset_type": "Фонд",
        "sector": "Недвига",
        "dependencies": [],
        "fee": None,
        "management_company": "Парус",
    },
    {
        "ticker": "TLCN",
        "name": "Лужники Коллекшн Москва",
        "asset_type": "Фонд",
        "sector": "Недвига",
        "dependencies": [],
        "fee": None,
        "management_company": "Т-Капитал",
    },
    {
        "ticker": "AKME",
        "name": "Альфа-Капитал Управляемые Российские Акции",
        "asset_type": "Фонд",
        "sector": "Акции",
        "dependencies": [],
        "fee": None,
        "management_company": "Альфа-Капитал",
    },
    {
        "ticker": "TDIV",
        "name": "Т-Капитал Дивидендные акции",
        "asset_type": "Фонд",
        "sector": "Акции",
        "dependencies": ["Индекс"],
        "fee": None,
        "management_company": "Т-Капитал",
    },
    {
        "ticker": "TRND",
        "name": "Т-Капитал Трендовые акции",
        "asset_type": "Фонд",
        "sector": "Акции",
        "dependencies": [],
        "fee": None,
        "management_company": "Т-Капитал",
    },
    {
        "ticker": "TIND",
        "name": "Т-Капитал Индустриальная недвижимость",
        "asset_type": "Фонд",
        "sector": "Недвига",
        "dependencies": [],
        "fee": None,
        "management_company": "Т-Капитал",
    },
    {
        "ticker": "AKQU",
        "name": "Альфа-Капитал Квант",
        "asset_type": "Фонд",
        "sector": "Акции",
        "dependencies": [],
        "fee": None,
        "management_company": "Альфа-Капитал",
    },
    {
        "ticker": "TITR",
        "name": "Т-Капитал Российские технологии",
        "asset_type": "Фонд",
        "sector": "ИТ",
        "dependencies": [],
        "fee": None,
        "management_company": "Т-Капитал",
    },
]

NEW_TICKER_CODES = [row["ticker"] for row in NEW_TICKERS]

# ticker, year, return_pct — только годы с данными в CSV
RETURN_ROWS: list[tuple[str, int, str]] = [
    ("RU000A109KH9", 2022, "-38.50"),
    ("RU000A109KH9", 2023, "40.50"),
    ("RU000A109KH9", 2024, "4.60"),
    ("RU000A109KH9", 2025, "37.00"),
    ("RU000A109KH9", 2026, "-0.10"),
    ("AKMB", 2022, "7.80"),
    ("AKMB", 2023, "10.50"),
    ("AKMB", 2024, "3.10"),
    ("AKMB", 2025, "31.30"),
    ("AKMB", 2026, "6.30"),
    ("TBRU", 2022, "6.20"),
    ("TBRU", 2023, "7.40"),
    ("TBRU", 2024, "5.10"),
    ("TBRU", 2025, "30.00"),
    ("TBRU", 2026, "8.30"),
    ("OBLG", 2022, "8.80"),
    ("OBLG", 2023, "3.40"),
    ("OBLG", 2024, "6.80"),
    ("OBLG", 2025, "27.70"),
    ("OBLG", 2026, "8.80"),
    ("SBRB", 2022, "9.70"),
    ("SBRB", 2023, "2.60"),
    ("SBRB", 2024, "7.00"),
    ("SBRB", 2025, "26.20"),
    ("SBRB", 2026, "7.80"),
    ("RU000A109KS6", 2024, "-1.40"),
    ("RU000A109KS6", 2025, "25.50"),
    ("RU000A109KS6", 2026, "-4.50"),
    ("GOLD", 2022, "-6.20"),
    ("GOLD", 2023, "44.40"),
    ("GOLD", 2024, "40.80"),
    ("GOLD", 2025, "24.20"),
    ("GOLD", 2026, "8.40"),
    ("TOFZ", 2024, "8.50"),
    ("TOFZ", 2025, "24.10"),
    ("TOFZ", 2026, "2.90"),
    ("SBFR", 2024, "14.00"),
    ("SBFR", 2025, "21.70"),
    ("SBFR", 2026, "10.00"),
    ("SBGB", 2022, "2.70"),
    ("SBGB", 2023, "-0.60"),
    ("SBGB", 2024, "-0.10"),
    ("SBGB", 2025, "21.60"),
    ("SBGB", 2026, "2.80"),
    ("TLCN", 2023, "14.10"),
    ("TLCN", 2024, "25.80"),
    ("TLCN", 2025, "21.30"),
    ("TLCN", 2026, "4.70"),
    ("LQDT", 2022, "9.60"),
    ("LQDT", 2023, "9.70"),
    ("LQDT", 2024, "18.30"),
    ("LQDT", 2025, "20.50"),
    ("LQDT", 2026, "9.80"),
    ("SAFE", 2022, "9.70"),
    ("SAFE", 2023, "4.90"),
    ("SAFE", 2024, "15.90"),
    ("SAFE", 2025, "20.10"),
    ("SAFE", 2026, "9.50"),
    ("TMON", 2023, "5.90"),
    ("TMON", 2024, "18.20"),
    ("TMON", 2025, "19.20"),
    ("TMON", 2026, "9.10"),
    ("AKME", 2022, "-33.70"),
    ("AKME", 2023, "76.20"),
    ("AKME", 2024, "11.70"),
    ("AKME", 2025, "10.80"),
    ("AKME", 2026, "-17.30"),
    ("TMOS", 2022, "-39.20"),
    ("TMOS", 2023, "49.00"),
    ("TMOS", 2024, "-0.90"),
    ("TMOS", 2025, "6.40"),
    ("TMOS", 2026, "-16.10"),
    ("TDIV", 2023, "-0.20"),
    ("TDIV", 2024, "-2.20"),
    ("TDIV", 2025, "4.80"),
    ("TDIV", 2026, "-8.70"),
    ("EQMX", 2022, "-41.10"),
    ("EQMX", 2023, "50.50"),
    ("EQMX", 2024, "-0.70"),
    ("EQMX", 2025, "4.60"),
    ("EQMX", 2026, "-16.00"),
    ("SBMX", 2022, "-40.60"),
    ("SBMX", 2023, "50.40"),
    ("SBMX", 2024, "0.00"),
    ("SBMX", 2025, "4.20"),
    ("SBMX", 2026, "-16.00"),
    ("TPAY", 2024, "-4.70"),
    ("TPAY", 2025, "4.00"),
    ("TPAY", 2026, "1.20"),
    ("RU000A104172", 2022, "14.10"),
    ("RU000A104172", 2023, "1.50"),
    ("RU000A104172", 2024, "48.30"),
    ("RU000A104172", 2025, "4.00"),
    ("RU000A104172", 2026, "-7.00"),
    ("TRND", 2025, "1.10"),
    ("TRND", 2026, "-15.90"),
    ("TIND", 2026, "0.00"),
    ("SBRI", 2022, "-29.90"),
    ("SBRI", 2023, "33.40"),
    ("SBRI", 2024, "-7.10"),
    ("SBRI", 2025, "-1.40"),
    ("SBRI", 2026, "-16.10"),
    ("AKQU", 2022, "8.10"),
    ("AKQU", 2023, "2.50"),
    ("AKQU", 2024, "12.10"),
    ("AKQU", 2025, "-1.60"),
    ("AKQU", 2026, "-16.20"),
    ("TLCB", 2023, "5.10"),
    ("TLCB", 2024, "3.40"),
    ("TLCB", 2025, "-9.80"),
    ("TLCB", 2026, "9.10"),
    ("SBBY", 2023, "-0.60"),
    ("SBBY", 2024, "16.30"),
    ("SBBY", 2025, "-10.20"),
    ("SBBY", 2026, "12.70"),
    ("SBCB", 2022, "-17.20"),
    ("SBCB", 2023, "-0.30"),
    ("SBCB", 2024, "17.90"),
    ("SBCB", 2025, "-17.70"),
    ("SBCB", 2026, "5.80"),
    ("SBCN", 2023, "26.20"),
    ("SBCN", 2024, "15.50"),
    ("SBCN", 2025, "-19.30"),
    ("SBCN", 2026, "14.00"),
    ("TITR", 2024, "-29.20"),
    ("TITR", 2025, "-22.10"),
    ("TITR", 2026, "-20.90"),
]


def upgrade() -> None:
    op.create_table(
        "invest_fund_returns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=64), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("return_pct", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker", "year", name="uq_invest_fund_returns_ticker_year"),
    )
    op.create_index(
        op.f("ix_invest_fund_returns_ticker"),
        "invest_fund_returns",
        ["ticker"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invest_fund_returns_year"),
        "invest_fund_returns",
        ["year"],
        unique=False,
    )

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
    bind = op.get_bind()
    for row in NEW_TICKERS:
        exists = bind.execute(
            sa.text("SELECT 1 FROM invest_tickers WHERE ticker = :ticker"),
            {"ticker": row["ticker"]},
        ).first()
        if not exists:
            op.bulk_insert(tickers_table, [row])

    returns_table = sa.table(
        "invest_fund_returns",
        sa.column("ticker", sa.String(length=64)),
        sa.column("year", sa.Integer()),
        sa.column("return_pct", sa.Numeric(precision=8, scale=2)),
    )
    op.bulk_insert(
        returns_table,
        [
            {
                "ticker": ticker,
                "year": year,
                "return_pct": Decimal(value),
            }
            for ticker, year, value in RETURN_ROWS
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_invest_fund_returns_year"), table_name="invest_fund_returns")
    op.drop_index(op.f("ix_invest_fund_returns_ticker"), table_name="invest_fund_returns")
    op.drop_table("invest_fund_returns")

    placeholders = ", ".join(f"'{ticker}'" for ticker in NEW_TICKER_CODES)
    op.execute(sa.text(f"DELETE FROM invest_tickers WHERE ticker IN ({placeholders})"))
