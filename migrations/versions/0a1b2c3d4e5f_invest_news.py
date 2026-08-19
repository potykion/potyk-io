"""invest news

Заполняем таблицу `invest_news` из vault `templates/potyk-invest/Новости/*.md`.

Frontmatter ключи (как в md):
datetime, ticker, source, summary, price, sentiment

Дополнительно:
action = Покупать / держать / наблюдать / продавать
Если action в md отсутствует — используем "наблюдать".
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
import yaml
from alembic import op

revision: str = "0a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
WIKI_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")

DEFAULT_ACTION = "наблюдать"

INVEST_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-invest"
NEWS_DIR = INVEST_DIR / "Новости"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        return {}, text[match.end() :]
    return meta, text[match.end() :]


def normalize_string(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def wiki_target(raw: object) -> str:
    if raw is None:
        return ""
    s = str(raw).strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()
    match = WIKI_RE.search(s)
    if not match:
        return s
    path, alias = match.group(1).strip(), (match.group(2) or "").strip()
    if alias:
        return alias
    return path.split("/")[-1].strip()


def parse_datetime(raw: object) -> datetime | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, datetime):
        return raw
    s = str(raw).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def load_seed_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if not NEWS_DIR.is_dir():
        return rows

    for path in sorted(NEWS_DIR.glob("*.md")):
        slug = path.stem
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8-sig"))

        dt = parse_datetime(meta.get("datetime"))
        if dt is None:
            continue

        ticker_key = wiki_target(meta.get("ticker"))
        if not ticker_key:
            continue
        # Тикер храним как "символ" из deals: берём первый токен (например, "X5 Ритейл" -> "X5").
        ticker_code = ticker_key.split()[0].strip()
        if not ticker_code:
            continue

        rows.append(
            {
                "slug": slug,
                "datetime": dt,
                "ticker": ticker_code,
                "source": normalize_string(wiki_target(meta.get("source"))),
                "summary": normalize_string(meta.get("summary")),
                "price": normalize_string(meta.get("price")),
                "sentiment": normalize_string(meta.get("sentiment")),
                "action": normalize_string(meta.get("action")) or DEFAULT_ACTION,
                "content": body.strip(),
            }
        )

    return rows


def upgrade() -> None:
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

    bind = op.get_bind()
    insp = sa.inspect(bind)
    table_exists = insp.has_table("invest_news")

    if not table_exists:
        op.create_table(
            "invest_news",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=255), nullable=False),
            sa.Column("datetime", sa.DateTime(), nullable=False),
            sa.Column("ticker", sa.String(length=64), nullable=False),
            sa.Column("source", sa.String(length=255), nullable=False, server_default=""),
            sa.Column("summary", sa.Text(), nullable=False, server_default=""),
            sa.Column("price", sa.String(length=64), nullable=False, server_default=""),
            sa.Column("sentiment", sa.String(length=16), nullable=False, server_default=""),
            sa.Column("action", sa.String(length=32), nullable=False, server_default=DEFAULT_ACTION),
            sa.Column("content", sa.Text(), nullable=False, server_default=""),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_invest_news_slug"),
            "invest_news",
            ["slug"],
            unique=True,
        )
        op.create_index(
            op.f("ix_invest_news_datetime"),
            "invest_news",
            ["datetime"],
            unique=False,
        )
        op.create_index(
            op.f("ix_invest_news_ticker"),
            "invest_news",
            ["ticker"],
            unique=False,
        )

    rows = load_seed_rows()
    if rows:
        # Таблица может уже существовать (например, из-за `db.create_all()` из `main.py`),
        # но быть пустой. Перезаполняем содержимое.
        op.execute(sa.text("DELETE FROM invest_news"))
        op.bulk_insert(news_table, rows)


def downgrade() -> None:
    op.drop_index(op.f("ix_invest_news_ticker"), table_name="invest_news")
    op.drop_index(op.f("ix_invest_news_datetime"), table_name="invest_news")
    op.drop_index(op.f("ix_invest_news_slug"), table_name="invest_news")
    op.drop_table("invest_news")

