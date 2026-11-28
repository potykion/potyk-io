"""Недельные доходности акций → SQL `invest_weekly_returns` + view для /invest/stocks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.invest.daily_top import (
    SECTOR_COLORS,
    compound_pct,
    day_label,
    fmt_pct,
)
from potyk_io_back.invest.entities import InvestWeeklyReturn


@dataclass
class WeeklyReturnCell:
    ticker: str
    pct: float
    pct_label: str
    sector: str
    color: str
    close: float | None


@dataclass
class WeeklyReturnsView:
    weeks: list[tuple[date, str]]  # (week_end, label)
    tickers: list[str]
    rows: list[tuple[str, list[WeeklyReturnCell | None], float, str]]
    # ticker, cells by week, total_pct, total_label
    note: str


def build_weekly_returns_view() -> WeeklyReturnsView | None:
    rows = db.session.scalars(
        select(InvestWeeklyReturn).order_by(
            InvestWeeklyReturn.week_end.asc(),
            InvestWeeklyReturn.ticker.asc(),
        )
    ).all()
    if not rows:
        return None

    weeks = sorted({r.week_end for r in rows})
    week_labels = [(w, day_label(w)) for w in weeks]
    by_ticker: dict[str, dict[date, InvestWeeklyReturn]] = {}
    for r in rows:
        by_ticker.setdefault(r.ticker, {})[r.week_end] = r

    # сортировка тикеров по итоговой дохе за все недели (убыв.)
    scored: list[tuple[float, str]] = []
    for ticker, by_week in by_ticker.items():
        pcts = [float(by_week[w].pct) for w in weeks if w in by_week]
        scored.append((compound_pct(pcts), ticker))
    scored.sort(key=lambda x: (-x[0], x[1]))
    tickers = [t for _, t in scored]

    out_rows: list[tuple[str, list[WeeklyReturnCell | None], float, str]] = []
    for total, ticker in scored:
        by_week = by_ticker[ticker]
        cells: list[WeeklyReturnCell | None] = []
        for w in weeks:
            r = by_week.get(w)
            if not r:
                cells.append(None)
                continue
            sector = (r.sector or "").strip() or "Прочее"
            pct = float(r.pct)
            cells.append(
                WeeklyReturnCell(
                    ticker=ticker,
                    pct=pct,
                    pct_label=fmt_pct(pct),
                    sector=sector,
                    color=SECTOR_COLORS.get(sector, SECTOR_COLORS["Прочее"]),
                    close=float(r.close) if r.close is not None else None,
                )
            )
        out_rows.append((ticker, cells, total, fmt_pct(total)))

    first, last = weeks[0], weeks[-1]
    note = (
        f"Доходность за ISO-неделю (закрытие к закрытию предыдущей недели). "
        f"{len(tickers)} бумаг × {len(weeks)} нед. "
        f"({day_label(first)} — {day_label(last)})."
    )
    return WeeklyReturnsView(
        weeks=week_labels,
        tickers=tickers,
        rows=out_rows,
        note=note,
    )
