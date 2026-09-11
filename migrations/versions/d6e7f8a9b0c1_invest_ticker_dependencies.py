"""Проставить зависимости тикеров (КС, Мир) из новостей

Revision ID: d6e7f8a9b0c1
Revises: d5e6f7a8b9c0
Create Date: 2026-09-11 14:00:00.000000
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d6e7f8a9b0c1"
down_revision: Union[str, Sequence[str], None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Добавляем к существующим, не затираем.
DEPS_TO_ADD: dict[str, list[str]] = {
    # Прокси на снижение КС (рост при снижении, падение при повышении/паузе)
    "MGNT": ["КС"],
    "SMLT": ["КС"],
    "SVAV": ["КС"],
    "RTLK": ["КС"],
    "AFLT": ["КС"],
    "SVCB": ["КС"],
    # мир-коин
    "OZON": ["Мир"],
    "NVTK": ["Мир"],
    "ROSN": ["Мир"],
}


def _load_deps(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [text] if text else []
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
        return []
    return []


def _merge(existing: list[str], additions: list[str]) -> list[str]:
    result = list(existing)
    for item in additions:
        if item not in result:
            result.append(item)
    return result


def upgrade() -> None:
    bind = op.get_bind()
    for ticker, additions in DEPS_TO_ADD.items():
        row = bind.execute(
            sa.text("SELECT dependencies FROM invest_tickers WHERE ticker = :ticker"),
            {"ticker": ticker},
        ).first()
        if row is None:
            continue
        merged = _merge(_load_deps(row[0]), additions)
        bind.execute(
            sa.text(
                "UPDATE invest_tickers SET dependencies = :deps WHERE ticker = :ticker"
            ),
            {"ticker": ticker, "deps": json.dumps(merged, ensure_ascii=False)},
        )


def downgrade() -> None:
    bind = op.get_bind()
    for ticker, additions in DEPS_TO_ADD.items():
        row = bind.execute(
            sa.text("SELECT dependencies FROM invest_tickers WHERE ticker = :ticker"),
            {"ticker": ticker},
        ).first()
        if row is None:
            continue
        remaining = [d for d in _load_deps(row[0]) if d not in additions]
        bind.execute(
            sa.text(
                "UPDATE invest_tickers SET dependencies = :deps WHERE ticker = :ticker"
            ),
            {"ticker": ticker, "deps": json.dumps(remaining, ensure_ascii=False)},
        )
