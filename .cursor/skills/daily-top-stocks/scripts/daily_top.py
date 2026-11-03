#!/usr/bin/env python3
"""Загрузить дневные доходности TQBR за месяц в SQL (invest_daily_returns)."""
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
    p.add_argument("--month", type=int, required=True, help="Месяц 1–12")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not 1 <= args.month <= 12:
        print("month must be 1..12", file=sys.stderr)
        return 2

    from main import create_app
    from potyk_io_back.invest.daily_top import (
        build_daily_top_view,
        day_label,
        fmt_pct,
        replace_month_returns,
    )

    app = create_app()
    with app.app_context():
        print(f"MOEX → SQL {args.year}-{args.month:02d}…")
        n = replace_month_returns(args.year, args.month, progress=True)
        print(f"Записано строк: {n}")

        view = build_daily_top_view(args.year, args.month)
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

        print(f"Страница: /invest/stocks?ym={args.year:04d}-{args.month:02d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
