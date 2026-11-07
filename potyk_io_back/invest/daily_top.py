"""Дневные доходности акций TQBR (MOEX ISS) → SQL `invest_daily_returns`."""
from __future__ import annotations

import calendar
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import delete, func, select

from potyk_io_back.core.db import db
from potyk_io_back.invest.entities import InvestDailyReturn, InvestTicker

MOEX_HISTORY = (
    "https://iss.moex.com/iss/history/engines/stock/markets/shares/"
    "boards/TQBR/securities.json"
)
MOEX_SECURITIES = (
    "https://iss.moex.com/iss/engines/stock/markets/shares/"
    "boards/TQBR/securities.json"
)

DEFAULT_TOP = 10
DEFAULT_MIN_VALUE = 100_000_000.0

SECTOR_FALLBACK: dict[str, str] = {
    "SBER": "Фин",
    "SBERP": "Фин",
    "T": "Фин",
    "VTBR": "Фин",
    "VTBRP": "Фин",
    "MOEX": "Фин",
    "CBOM": "Фин",
    "BSPB": "Фин",
    "BSPBP": "Фин",
    "SVCB": "Фин",
    "MBNK": "Фин",
    "RENI": "Фин",
    "AFKS": "Фин",
    "DOMRF": "Фин",
    "SFIN": "Фин",
    "LKOH": "Нефтянка",
    "ROSN": "Нефтянка",
    "SIBN": "Нефтянка",
    "SNGS": "Нефтянка",
    "SNGSP": "Нефтянка",
    "TATN": "Нефтянка",
    "TATNP": "Нефтянка",
    "BANE": "Нефтянка",
    "BANEP": "Нефтянка",
    "TRNFP": "Нефтянка",
    "RNFT": "Нефтянка",
    "POGR": "Нефтянка",
    "GAZP": "Газ",
    "NVTK": "Газ",
    "YDEX": "ИТ",
    "YNDX": "ИТ",
    "VKCO": "ИТ",
    "POSI": "ИТ",
    "ASTR": "ИТ",
    "HHRU": "ИТ",
    "HEAD": "ИТ",
    "CIAN": "ИТ",
    "CNRU": "ИТ",
    "DATA": "ИТ",
    "DIAS": "ИТ",
    "IVAT": "ИТ",
    "SOFL": "ИТ",
    "BAZA": "ИТ",
    "OZON": "Ритейл",
    "MGNT": "Ритейл",
    "X5": "Ритейл",
    "LENT": "Ритейл",
    "MVID": "Ритейл",
    "BELU": "Ритейл",
    "FIXP": "Ритейл",
    "GMKN": "Материалы",
    "NLMK": "Металл",
    "CHMF": "Металл",
    "MAGN": "Металл",
    "TRMK": "Металл",
    "MTLR": "Металл",
    "MTLRP": "Металл",
    "ALRS": "Материалы",
    "PLZL": "Материалы",
    "SELG": "Материалы",
    "UGLD": "Материалы",
    "PHOR": "Материалы",
    "SGZH": "Материалы",
    "POLY": "Материалы",
    "GCHE": "Ритейл",
    "RUAL": "Алюм",
    "ENPG": "Алюм",
    "ENGP": "Алюм",
    "MTSS": "Телеком",
    "RTKM": "Телеком",
    "RTKMP": "Телеком",
    "RTLK": "Телеком",
    "RTLKP": "Телеком",
    "AFLT": "Транспорт",
    "FLOT": "Транспорт",
    "NMTP": "Транспорт",
    "FESH": "Транспорт",
    "GLTR": "Транспорт",
    "WUSH": "Транспорт",
    "NKHP": "Транспорт",
    "SVAV": "Транспорт",
    "PIKK": "Недвига",
    "SMLT": "Недвига",
    "LSRG": "Недвига",
    "ETLN": "Недвига",
    "SFTL": "Недвига",
    "GLRX": "Недвига",
    "FEES": "Коммуналка",
    "HYDR": "Коммуналка",
    "IRAO": "Коммуналка",
    "UPRO": "Коммуналка",
    "MSNG": "Коммуналка",
    "OGKB": "Коммуналка",
    "TGKA": "Коммуналка",
    "MDMG": "Хп",
    "GEMC": "Хп",
    "SPBE": "Мир",
    "AKRN": "Удобрения",
    "KAZT": "Удобрения",
    "KAZTP": "Удобрения",
    "RAGR": "Ритейл",
    "RAGN": "Ритейл",
    "AQUA": "Ритейл",
    "ABRD": "Ритейл",
}

SECTOR_COLORS: dict[str, str] = {
    "Фин": "#dbeafe",
    "Нефтянка": "#ffedd5",
    "Газ": "#ccfbf1",
    "ИТ": "#ede9fe",
    "Металл": "#e5e7eb",
    "Материалы": "#dcfce7",
    "Ритейл": "#fce7f3",
    "Телеком": "#cffafe",
    "Транспорт": "#e0e7ff",
    "Недвига": "#fef3c7",
    "Коммуналка": "#ecfccb",
    "Хп": "#fae8ff",
    "Алюм": "#f3f4f6",
    "Удобрения": "#d1fae5",
    "Мир": "#e0f2fe",
    "Прочее": "#f5f3ee",
}

MONTH_RU_SHORT = {
    1: "янв",
    2: "фев",
    3: "мар",
    4: "апр",
    5: "май",
    6: "июн",
    7: "июл",
    8: "авг",
    9: "сен",
    10: "окт",
    11: "ноя",
    12: "дек",
}

MONTH_RU_FULL = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь",
}


def day_label(d: date) -> str:
    return f"{d.day} {MONTH_RU_SHORT[d.month]}"


def fmt_pct(x: float) -> str:
    sign = "+" if x > 0 else ""
    return f"{sign}{x:.2f}%"


def compound_pct(daily_pcts: list[float]) -> float:
    """Итоговая доходность: произведение (1 + r_i) − 1, в процентах."""
    if not daily_pcts:
        return 0.0
    factor = 1.0
    for p in daily_pcts:
        factor *= 1.0 + float(p) / 100.0
    return (factor - 1.0) * 100.0


def load_sectors_map() -> dict[str, str]:
    sectors = dict(SECTOR_FALLBACK)
    rows = db.session.execute(
        select(InvestTicker.ticker, InvestTicker.sector).where(InvestTicker.sector != "")
    ).all()
    for ticker, sector in rows:
        if ticker and sector:
            sectors[str(ticker).upper()] = str(sector)
    return sectors


def _http_json(url: str, retries: int = 5) -> dict:
    import json

    last: Exception | None = None
    for i in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "potyk-io-daily-top/1.0"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            last = e
            time.sleep(0.8 * (i + 1))
    raise RuntimeError(f"MOEX request failed: {url}\n{last}")


def _history_page(day: date, start: int) -> tuple[list[str], list[list]]:
    params = {
        "date": day.isoformat(),
        "start": start,
        "iss.meta": "off",
        "iss.only": "history",
        "history.columns": "SECID,CLOSE,VALUE,VOLUME,NUMTRADES,TRENDCLSPR,LEGALCLOSEPRICE",
    }
    url = MOEX_HISTORY + "?" + urllib.parse.urlencode(params)
    data = _http_json(url)
    block = data["history"]
    return block["columns"], block["data"]


def fetch_day_rows(day: date) -> list[dict]:
    cols, rows = _history_page(day, 0)
    all_rows = list(rows)
    start = len(rows)
    while rows:
        cols, rows = _history_page(day, start)
        if not rows:
            break
        all_rows.extend(rows)
        start += len(rows)
        if len(rows) < 100:
            break
    idx = {c: i for i, c in enumerate(cols)}
    out = []
    for r in all_rows:
        out.append(
            {
                "ticker": r[idx["SECID"]],
                "close": r[idx["CLOSE"]],
                "value": r[idx["VALUE"]] or 0,
                "volume": r[idx["VOLUME"]] or 0,
                "trend": r[idx["TRENDCLSPR"]],
            }
        )
    return out


def fetch_share_tickers() -> set[str]:
    params = {"iss.meta": "off", "iss.only": "securities"}
    url = MOEX_SECURITIES + "?" + urllib.parse.urlencode(params)
    data = _http_json(url)
    cols = data["securities"]["columns"]
    rows = data["securities"]["data"]
    idx = {c: i for i, c in enumerate(cols)}
    return {r[idx["SECID"]] for r in rows if r[idx["SECTYPE"]] in ("1", "2")}


def _days_inclusive(start: date, end: date) -> list[date]:
    if end < start:
        return []
    out: list[date] = []
    cur = start
    step = timedelta(days=1)
    while cur <= end:
        out.append(cur)
        cur = cur + step
    return out


def replace_returns_range(
    start: date,
    end: date,
    *,
    sectors: dict[str, str] | None = None,
    progress: bool = False,
) -> int:
    """Скачать диапазон дат с MOEX и перезаписать строки в SQL. Возвращает число строк."""
    sectors = sectors or load_sectors_map()
    shares = fetch_share_tickers()

    db.session.execute(
        delete(InvestDailyReturn).where(
            InvestDailyReturn.trade_date >= start,
            InvestDailyReturn.trade_date <= end,
        )
    )

    inserted = 0
    for day in _days_inclusive(start, end):
        rows = fetch_day_rows(day)
        if not rows:
            if progress:
                print(f"  {day.isoformat()}: нет торгов", flush=True)
            continue
        day_n = 0
        for r in rows:
            if r["ticker"] not in shares:
                continue
            if r["trend"] is None:
                continue
            sector = sectors.get(r["ticker"], "Прочее")
            db.session.add(
                InvestDailyReturn(
                    trade_date=day,
                    ticker=r["ticker"],
                    pct=Decimal(str(r["trend"])),
                    value=Decimal(str(r["value"] or 0)),
                    volume=int(r["volume"] or 0) or None,
                    close=(
                        Decimal(str(r["close"]))
                        if r["close"] is not None
                        else None
                    ),
                    sector=sector,
                )
            )
            inserted += 1
            day_n += 1
        if progress:
            print(f"  {day.isoformat()}: {day_n} акций", flush=True)
        time.sleep(0.15)

    db.session.commit()
    return inserted


def replace_month_returns(
    year: int,
    month: int,
    *,
    sectors: dict[str, str] | None = None,
    progress: bool = False,
) -> int:
    """Скачать месяц с MOEX и перезаписать строки в SQL. Возвращает число строк."""
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    return replace_returns_range(
        first, last, sectors=sectors, progress=progress
    )


def list_available_months() -> list[tuple[int, int]]:
    rows = db.session.execute(
        select(
            func.strftime("%Y", InvestDailyReturn.trade_date),
            func.strftime("%m", InvestDailyReturn.trade_date),
        ).distinct()
    ).all()
    out: list[tuple[int, int]] = []
    for y_s, m_s in rows:
        if y_s and m_s:
            out.append((int(y_s), int(m_s)))
    return sorted(out, reverse=True)


def default_year_month(today: date | None = None) -> tuple[int, int]:
    available = list_available_months()
    if available:
        return available[0]
    today = today or date.today()
    if today.day <= 3 and today.month > 1:
        return today.year, today.month - 1
    if today.day <= 3 and today.month == 1:
        return today.year - 1, 12
    return today.year, today.month


@dataclass
class DailyTopEntry:
    ticker: str
    pct: float
    value: float
    sector: str
    pct_label: str
    color: str


@dataclass
class DailyTopDay:
    day: date
    label: str
    entries: list[DailyTopEntry]


@dataclass
class DailyTopView:
    year: int
    month: int
    month_title: str
    min_value: float
    top_n: int
    days: list[DailyTopDay]
    ranks: list[list[DailyTopEntry | None]]
    legend: list[tuple[str, str]]
    available_months: list[tuple[int, int, str]]

    def client_payload(self) -> dict:
        """JSON: все строки месяца из SQL (для фильтра по сектору без дыр)."""
        return {
            "top_n": self.top_n,
            "min_value": self.min_value,
            "days": [
                {
                    "label": day.label,
                    "entries": [
                        {
                            "ticker": e.ticker,
                            "pct": e.pct,
                            "pct_label": e.pct_label,
                            "value": e.value,
                            "sector": e.sector,
                            "color": e.color,
                        }
                        for e in day.entries
                    ],
                }
                for day in self.days
            ],
        }


def build_daily_top_view(
    year: int,
    month: int,
    *,
    top_n: int = DEFAULT_TOP,
    min_value: float = DEFAULT_MIN_VALUE,
) -> DailyTopView | None:
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    rows = db.session.scalars(
        select(InvestDailyReturn)
        .where(
            InvestDailyReturn.trade_date >= first,
            InvestDailyReturn.trade_date <= last,
        )
        .order_by(
            InvestDailyReturn.trade_date.asc(),
            InvestDailyReturn.pct.desc(),
        )
    ).all()
    if not rows:
        return None

    by_day: dict[date, list[DailyTopEntry]] = {}
    for row in rows:
        sector = (row.sector or "").strip() or "Прочее"
        pct = float(row.pct)
        entry = DailyTopEntry(
            ticker=row.ticker,
            pct=pct,
            value=float(row.value or 0),
            sector=sector,
            pct_label=fmt_pct(pct),
            color=SECTOR_COLORS.get(sector, SECTOR_COLORS["Прочее"]),
        )
        by_day.setdefault(row.trade_date, []).append(entry)

    days = [
        DailyTopDay(day=d, label=day_label(d), entries=by_day[d])
        for d in sorted(by_day.keys())
    ]

    # Топ-N только среди ликвидных (оборот ≥ min_value)
    ranks: list[list[DailyTopEntry | None]] = []
    liquid_by_day = [
        [e for e in day.entries if e.value >= min_value] for day in days
    ]
    for rank in range(top_n):
        row_cells: list[DailyTopEntry | None] = []
        for liquid in liquid_by_day:
            row_cells.append(liquid[rank] if rank < len(liquid) else None)
        ranks.append(row_cells)

    legend_sectors = sorted(
        {e.sector for day in days for e in day.entries},
        key=lambda s: s.casefold(),
    )
    legend = [(s, SECTOR_COLORS.get(s, SECTOR_COLORS["Прочее"])) for s in legend_sectors]
    available = [
        (y, m, f"{MONTH_RU_FULL[m]} {y}") for y, m in list_available_months()
    ]

    return DailyTopView(
        year=year,
        month=month,
        month_title=f"{MONTH_RU_FULL[month]} {year}",
        min_value=min_value,
        top_n=top_n,
        days=days,
        ranks=ranks,
        legend=legend,
        available_months=available,
    )
