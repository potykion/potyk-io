#!/usr/bin/env python3
"""Загрузить дневные доходности TQBR в SQL (invest_daily_returns)."""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MOEX → invest_daily_returns")
    p.add_argument("--year", type=int, default=date.today().year)
    p.add_argument("--month", type=int, help="Месяц 1–12 (весь месяц)")
    p.add_argument("--from", dest="date_from", help="Начало YYYY-MM-DD")
    p.add_argument("--to", dest="date_to", help="Конец YYYY-MM-DD")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    from main import create_app
    from potyk_io_back.invest.daily_top import (
        build_daily_top_view,
        day_label,
        fmt_pct,
        replace_month_returns,
        replace_returns_range,
    )

    app = create_app()
    with app.app_context():
        if args.date_from or args.date_to:
            if not (args.date_from and args.date_to):
                print("нужны оба --from и --to", file=sys.stderr)
                return 2
            start = date.fromisoformat(args.date_from)
            end = date.fromisoformat(args.date_to)
            print(f"MOEX → SQL {start.isoformat()}…{end.isoformat()}…")
            n = replace_returns_range(start, end, progress=True)
            year, month = end.year, end.month
        else:
            if not args.month or not 1 <= args.month <= 12:
                print("нужен --month 1..12 или --from/--to", file=sys.stderr)
                return 2
            year, month = args.year, args.month
            print(f"MOEX → SQL {year}-{month:02d}…")
            n = replace_month_returns(year, month, progress=True)

        print(f"Записано строк: {n}")
        view = build_daily_top_view(year, month)

        if not view or not view.days:
            print("Нет данных для топа (проверь порог оборота)", file=sys.stderr)
            return 1

        chunk = 5
        for i in range(0, len(view.days), chunk):
            days = view.days[i : i + chunk]
            header = " | ".join(f"{day_label(d.day):^14}" for d in days)
            print(header)
            print("-" * len(header))
            for rank in range(view.top_n):
                cells = []
                for d in days:
                    top = d.entries[: view.top_n]
                    if rank >= len(top):
                        cells.append(f"{'':14}")
                    else:
                        e = top[rank]
                        cells.append(
                            f"{e.ticker} {fmt_pct(e.pct):>7}"[:14].ljust(14)
                        )
                print(" | ".join(cells))
            print()

        print(f"Страница: /invest/stocks?ym={year:04d}-{month:02d}")
        print("Для прода: data-миграция с дампом invest_daily_returns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
