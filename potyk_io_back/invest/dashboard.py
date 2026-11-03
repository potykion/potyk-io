"""Сборка дашборда новостей из SQL (invest_news)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from urllib.parse import quote

import markdown
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.invest.daily_top import MONTH_RU_FULL, compound_pct, fmt_pct
from potyk_io_back.invest.entities import (
    NEWS_FEED_ASSET_TYPES,
    InvestDailyReturn,
    InvestDeal,
    InvestFundReturn,
    InvestNews,
    InvestTicker,
    InvestTickerLevel,
)
from potyk_io_back.potyk_io.md_rendering.render import MD_EXTENSIONS, MD_EXTENSION_CONFIGS

EMPTY_SECTOR = "Без сектора"


def sentiment_tone(sentiment: str) -> str:
    if "🟢" in sentiment:
        return "pos"
    if "🟡" in sentiment:
        return "neu"
    if "🔴" in sentiment:
        return "neg"
    return "none"


def fmt_datetime(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%d.%m.%Y %H:%M")


def normalize_dependencies(raw) -> str:
    if not raw:
        return ""
    if isinstance(raw, list):
        items = [str(x).strip() for x in raw if str(x).strip()]
        return ", ".join(items)
    return str(raw).strip()


def news_url(slug: str) -> str:
    return "/invest/Новости/" + quote(slug, safe="")


def ticker_url(ticker: str) -> str:
    return "/invest/tickers/" + quote(ticker, safe="")


@dataclass
class NewsFilters:
    date_from: date | None = None
    date_to: date | None = None
    sentiment: str = ""
    ticker: str = ""
    sector: str = ""

    @property
    def active(self) -> bool:
        return bool(
            self.date_from
            or self.date_to
            or self.sentiment
            or self.ticker
            or self.sector
        )


@dataclass
class NewsItem:
    title: str
    url: str
    datetime: datetime | None
    datetime_fmt: str
    sentiment: str
    sentiment_tone: str
    price: str
    summary: str
    action: str


@dataclass
class TickerGroup:
    key: str
    url: str
    sector: str
    deps: str
    news: list[NewsItem] = field(default_factory=list)


@dataclass
class SectorBlock:
    title: str
    tickers: list[TickerGroup] = field(default_factory=list)


@dataclass
class FundRow:
    ticker: str
    name: str
    deps: str
    fee: str
    returns: dict[int, str]
    return_values: dict[int, Decimal | None]


@dataclass
class FundSectorBlock:
    title: str
    funds: list[FundRow] = field(default_factory=list)


@dataclass
class NewsPage:
    title: str
    datetime_fmt: str
    ticker: str
    ticker_url: str
    source: str
    sentiment: str
    sentiment_tone: str
    price: str
    summary: str
    action: str
    content_html: str


@dataclass
class TickerDailyReturn:
    trade_date: date
    date_fmt: str
    pct: float
    pct_label: str
    value: float
    value_mln: str
    close: float | None
    close_fmt: str


@dataclass
class TickerMonthReturn:
    year: int
    month: int
    title: str
    pct: float
    pct_label: str
    days: int


@dataclass
class TickerPage:
    ticker: str
    name: str
    asset_type: str
    sector: str
    deps: str
    entry_level: Decimal | None
    exit_level: Decimal | None
    deals: list[InvestDeal]
    news: list[NewsItem]
    daily_returns: list[TickerDailyReturn] = field(default_factory=list)
    month_returns: list[TickerMonthReturn] = field(default_factory=list)


def load_news_page(slug: str) -> NewsPage | None:
    row = db.session.scalars(select(InvestNews).where(InvestNews.slug == slug)).first()
    if row is None:
        return None

    body = (row.content or "").strip()
    content_html = (
        markdown.markdown(
            body,
            extensions=MD_EXTENSIONS,
            extension_configs=MD_EXTENSION_CONFIGS,
            output_format="html",
        )
        if body
        else ""
    )

    return NewsPage(
        title=row.slug,
        datetime_fmt=fmt_datetime(row.datetime),
        ticker=row.ticker,
        ticker_url=ticker_url(row.ticker),
        source=row.source or "",
        sentiment=row.sentiment or "",
        sentiment_tone=sentiment_tone(row.sentiment or ""),
        price=row.price or "",
        summary=row.summary or "",
        action=row.action or "",
        content_html=content_html,
    )


def _fmt_close(value) -> str:
    if value is None:
        return "—"
    text = f"{Decimal(value):.6f}".rstrip("0").rstrip(".")
    return text or "0"


def load_ticker_page(ticker: str) -> TickerPage:
    code = (ticker or "").strip()
    row = db.session.scalars(
        select(InvestTicker).where(InvestTicker.ticker == code)
    ).first()
    levels = db.session.scalars(
        select(InvestTickerLevel).where(InvestTickerLevel.ticker == code)
    ).first()
    deals = db.session.scalars(
        select(InvestDeal)
        .where(InvestDeal.ticker == code)
        .order_by(InvestDeal.opened_at.desc(), InvestDeal.id.desc())
    ).all()
    news_rows = db.session.scalars(
        select(InvestNews)
        .where(InvestNews.ticker == code)
        .order_by(InvestNews.datetime.desc(), InvestNews.id.desc())
    ).all()
    daily_rows = db.session.scalars(
        select(InvestDailyReturn)
        .where(InvestDailyReturn.ticker == code)
        .order_by(InvestDailyReturn.trade_date.desc(), InvestDailyReturn.id.desc())
    ).all()

    news: list[NewsItem] = []
    for n in news_rows:
        sentiment = n.sentiment or ""
        news.append(
            NewsItem(
                title=n.slug,
                url=news_url(n.slug),
                datetime=n.datetime,
                datetime_fmt=fmt_datetime(n.datetime),
                sentiment=sentiment,
                sentiment_tone=sentiment_tone(sentiment),
                price=n.price or "",
                summary=n.summary or "—",
                action=n.action or "",
            )
        )

    daily_returns: list[TickerDailyReturn] = []
    by_month: dict[tuple[int, int], list[float]] = {}
    for r in daily_rows:
        pct = float(r.pct)
        value = float(r.value or 0)
        daily_returns.append(
            TickerDailyReturn(
                trade_date=r.trade_date,
                date_fmt=r.trade_date.strftime("%d.%m.%Y"),
                pct=pct,
                pct_label=fmt_pct(pct),
                value=value,
                value_mln=f"{value / 1e6:.1f}",
                close=float(r.close) if r.close is not None else None,
                close_fmt=_fmt_close(r.close),
            )
        )
        key = (r.trade_date.year, r.trade_date.month)
        by_month.setdefault(key, []).append(pct)

    month_returns: list[TickerMonthReturn] = []
    for (year, month), pcts in sorted(by_month.items(), reverse=True):
        # daily_rows приходят desc — для компаундинга нужен хронологический порядок
        chron = list(reversed(pcts))
        total = compound_pct(chron)
        month_returns.append(
            TickerMonthReturn(
                year=year,
                month=month,
                title=f"{MONTH_RU_FULL[month]} {year}",
                pct=total,
                pct_label=fmt_pct(total),
                days=len(chron),
            )
        )

    return TickerPage(
        ticker=code,
        name=(row.name if row else "") or "",
        asset_type=(row.asset_type if row else "") or "",
        sector=(row.sector if row else "") or "",
        deps=normalize_dependencies(row.dependencies) if row else "",
        entry_level=levels.entry_level if levels else None,
        exit_level=levels.exit_level if levels else None,
        deals=deals,
        news=news,
        daily_returns=daily_returns,
        month_returns=month_returns,
    )


def _news_in_feed(ticker_row: InvestTicker | None) -> bool:
    """Акции и рынок/глобал — да; фонды — нет; неизвестный тикер — да."""
    if ticker_row is None:
        return True
    return ticker_row.asset_type in NEWS_FEED_ASSET_TYPES


def _matches_filters(
    news: InvestNews,
    ticker_row: InvestTicker | None,
    filters: NewsFilters,
) -> bool:
    if filters.date_from is not None:
        if news.datetime is None or news.datetime.date() < filters.date_from:
            return False
    if filters.date_to is not None:
        if news.datetime is None or news.datetime.date() > filters.date_to:
            return False
    if filters.sentiment and filters.sentiment not in (news.sentiment or ""):
        return False
    if filters.ticker and news.ticker != filters.ticker:
        return False
    if filters.sector:
        sector = (ticker_row.sector if ticker_row else "") or ""
        if sector != filters.sector:
            return False
    return True


def build_dashboard(filters: NewsFilters | None = None) -> list[SectorBlock]:
    filters = filters or NewsFilters()
    ticker_rows = db.session.scalars(select(InvestTicker)).all()
    ticker_by_code = {t.ticker: t for t in ticker_rows}

    news_rows = db.session.scalars(
        select(InvestNews).order_by(InvestNews.datetime.desc(), InvestNews.id.desc())
    ).all()

    by_ticker: dict[str, TickerGroup] = {}

    for n in news_rows:
        t = ticker_by_code.get(n.ticker)
        if not _news_in_feed(t):
            continue
        if not _matches_filters(n, t, filters):
            continue

        sector = t.sector if t else ""
        deps = normalize_dependencies(t.dependencies) if t else ""

        group = by_ticker.get(n.ticker)
        if group is None:
            group = TickerGroup(
                key=n.ticker,
                url=ticker_url(n.ticker),
                sector=sector,
                deps=deps,
            )
            by_ticker[n.ticker] = group

        sentiment = n.sentiment or ""
        group.news.append(
            NewsItem(
                title=n.slug,
                url=news_url(n.slug),
                datetime=n.datetime,
                datetime_fmt=fmt_datetime(n.datetime),
                sentiment=sentiment,
                sentiment_tone=sentiment_tone(sentiment),
                price=n.price or "",
                summary=n.summary or "—",
                action=n.action or "",
            )
        )

    groups = list(by_ticker.values())
    groups.sort(
        key=lambda g: (
            0 if not g.sector else 1,
            g.sector,
            g.key,
        )
    )

    blocks: list[SectorBlock] = []
    current: SectorBlock | None = None
    for group in groups:
        title = group.sector or EMPTY_SECTOR
        if current is None or current.title != title:
            current = SectorBlock(title=title)
            blocks.append(current)
        current.tickers.append(group)

    return blocks


def fmt_fee(value) -> str:
    if value is None:
        return "—"
    text = format(Decimal(value).normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return f"{text}%"


def fmt_return_pct(value) -> str:
    quantized = Decimal(value).quantize(Decimal("0.01"))
    text = format(quantized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    signed = f"+{text}" if quantized > 0 else text
    return f"{signed}%"


@dataclass
class DepTickerRow:
    ticker: str
    name: str
    sector: str
    flags: dict[str, bool]


def dependency_labels(raw) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    text = str(raw).strip()
    return [text] if text else []


def build_dependencies_matrix() -> tuple[list[str], list[DepTickerRow]]:
    """Матрица всех акций: строки — тикеры, столбцы — факторы."""
    stock_rows = db.session.scalars(
        select(InvestTicker)
        .where(InvestTicker.asset_type == "Акция")
        .order_by(InvestTicker.ticker.asc())
    ).all()

    columns: list[str] = sorted(
        {label for t in stock_rows for label in dependency_labels(t.dependencies)},
        key=lambda s: s.casefold(),
    )

    rows: list[DepTickerRow] = []
    for ticker in stock_rows:
        labels = set(dependency_labels(ticker.dependencies))
        rows.append(
            DepTickerRow(
                ticker=ticker.ticker,
                name=(ticker.name or "").strip(),
                sector=(ticker.sector or "").strip(),
                flags={col: col in labels for col in columns},
            )
        )

    return columns, rows


def build_funds_dashboard(return_years: list[int] | None = None) -> tuple[list[int], list[FundSectorBlock]]:
    fund_rows = db.session.scalars(
        select(InvestTicker)
        .where(InvestTicker.asset_type == "Фонд")
        .order_by(InvestTicker.sector.asc(), InvestTicker.ticker.asc())
    ).all()

    return_rows = db.session.scalars(select(InvestFundReturn)).all()
    returns_by_ticker: dict[str, dict[int, str]] = {}
    return_values_by_ticker: dict[str, dict[int, Decimal | None]] = {}
    years_set: set[int] = set(return_years or [])
    for row in return_rows:
        years_set.add(row.year)
        returns_by_ticker.setdefault(row.ticker, {})[row.year] = fmt_return_pct(row.return_pct)
        return_values_by_ticker.setdefault(row.ticker, {})[row.year] = Decimal(row.return_pct)

    years = sorted(years_set)
    if not years:
        years = list(return_years or [])

    blocks: list[FundSectorBlock] = []
    current: FundSectorBlock | None = None
    for fund in fund_rows:
        title = fund.sector or EMPTY_SECTOR
        if current is None or current.title != title:
            current = FundSectorBlock(title=title)
            blocks.append(current)
        current.funds.append(
            FundRow(
                ticker=fund.ticker,
                name=(fund.name or "").strip(),
                deps=normalize_dependencies(fund.dependencies),
                fee=fmt_fee(fund.fee),
                returns=returns_by_ticker.get(fund.ticker, {}),
                return_values=return_values_by_ticker.get(fund.ticker, {}),
            )
        )

    return years, blocks
