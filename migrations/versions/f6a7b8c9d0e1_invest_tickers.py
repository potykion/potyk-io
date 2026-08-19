"""invest tickers

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-19 13:20:00.000000

"""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
import yaml
from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
TICKERS_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-invest" / "Тикеры"
MARKET_TICKERS = {"BRENT", "CNY", "GLD", "IMOEX", "RGBI", "RTSI", "Глобал", "КС"}


def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1)) or {}
    return data if isinstance(data, dict) else {}


def normalize_string(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def normalize_array(value: object) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        items = value
    else:
        items = [value]
    return [str(item).strip() for item in items if str(item).strip()]


def parse_fee(value: object) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


def split_stem(stem: str) -> tuple[str, str]:
    parts = stem.split(maxsplit=1)
    ticker = parts[0].strip()
    name = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ticker
    return ticker, name


def detect_asset_type(path: Path, ticker: str) -> str:
    if "Фонды" in path.parts:
        return "Фонд"
    if ticker in MARKET_TICKERS:
        return "Рынок"
    return "Акция"


def load_seed_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(TICKERS_DIR.rglob("*.md")):
        ticker, name = split_stem(path.stem)
        meta = parse_frontmatter(path.read_text(encoding="utf-8-sig"))
        rows.append(
            {
                "ticker": ticker,
                "name": name or ticker,
                "asset_type": detect_asset_type(path, ticker),
                "sector": normalize_string(meta.get("Сектор")),
                "dependencies": normalize_array(meta.get("Зависимости")),
                "fee": parse_fee(meta.get("Комиссия")),
                "management_company": normalize_string(meta.get("УК")),
            }
        )
    return rows


def upgrade() -> None:
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
    insp = sa.inspect(bind)
    table_exists = insp.has_table("invest_tickers")

    if not table_exists:
        op.create_table(
            "invest_tickers",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ticker", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("asset_type", sa.String(length=16), nullable=False),
            sa.Column(
                "sector",
                sa.String(length=255),
                nullable=False,
                server_default="",
            ),
            sa.Column("dependencies", sa.JSON(), nullable=False, server_default="[]"),
            sa.Column("fee", sa.Numeric(precision=8, scale=4), nullable=True),
            sa.Column(
                "management_company",
                sa.String(length=255),
                nullable=False,
                server_default="",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_invest_tickers_asset_type"),
            "invest_tickers",
            ["asset_type"],
            unique=False,
        )
        op.create_index(
            op.f("ix_invest_tickers_ticker"),
            "invest_tickers",
            ["ticker"],
            unique=True,
        )

    rows = load_seed_rows()
    if rows:
        # Таблица может уже существовать (например, из-за рассинхронизации alembic_version),
        # но быть пустой. Перезаполняем содержимое.
        op.execute(sa.text("DELETE FROM invest_tickers"))
        op.bulk_insert(tickers_table, rows)


def downgrade() -> None:
    op.drop_index(op.f("ix_invest_tickers_ticker"), table_name="invest_tickers")
    op.drop_index(op.f("ix_invest_tickers_asset_type"), table_name="invest_tickers")
    op.drop_table("invest_tickers")
