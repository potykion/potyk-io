"""Сборка дашборда новостей из SQL (invest_news)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from urllib.parse import quote

import markdown
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.invest.entities import InvestFundReturn, InvestNews, InvestTicker
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
    label: str
    sector: str
    deps: str
    fee: str
    returns: dict[int, str]


@dataclass
class FundSectorBlock:
    title: str
    funds: list[FundRow] = field(default_factory=list)


@dataclass
class NewsPage:
    title: str
    datetime_fmt: str
    ticker: str
    source: str
    sentiment: str
    sentiment_tone: str
    price: str
    summary: str
    action: str
    content_html: str


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
        source=row.source or "",
        sentiment=row.sentiment or "",
        sentiment_tone=sentiment_tone(row.sentiment or ""),
        price=row.price or "",
        summary=row.summary or "",
        action=row.action or "",
        content_html=content_html,
    )


def build_dashboard() -> list[SectorBlock]:
    ticker_rows = db.session.scalars(select(InvestTicker)).all()
    ticker_by_code = {t.ticker: t for t in ticker_rows}

    # Сначала новые новости, внутри тикера — тоже по времени.
    news_rows = db.session.scalars(
        select(InvestNews).order_by(InvestNews.datetime.desc(), InvestNews.id.desc())
    ).all()

    by_ticker: dict[str, TickerGroup] = {}

    for n in news_rows:
        t = ticker_by_code.get(n.ticker)
        sector = t.sector if t else ""
        deps = normalize_dependencies(t.dependencies) if t else ""

        group = by_ticker.get(n.ticker)
        if group is None:
            group = TickerGroup(key=n.ticker, sector=sector, deps=deps)
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


def ticker_label(ticker: str, name: str) -> str:
    name = (name or "").strip()
    if not name or name == ticker:
        return ticker
    return f"{ticker} {name}"


def build_funds_dashboard(return_years: list[int] | None = None) -> tuple[list[int], list[FundSectorBlock]]:
    fund_rows = db.session.scalars(
        select(InvestTicker)
        .where(InvestTicker.asset_type == "Фонд")
        .order_by(InvestTicker.sector.asc(), InvestTicker.ticker.asc())
    ).all()

    return_rows = db.session.scalars(select(InvestFundReturn)).all()
    returns_by_ticker: dict[str, dict[int, str]] = {}
    years_set: set[int] = set(return_years or [])
    for row in return_rows:
        years_set.add(row.year)
        returns_by_ticker.setdefault(row.ticker, {})[row.year] = fmt_return_pct(row.return_pct)

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
                label=ticker_label(fund.ticker, fund.name),
                sector=fund.sector or "",
                deps=normalize_dependencies(fund.dependencies),
                fee=fmt_fee(fund.fee),
                returns=returns_by_ticker.get(fund.ticker, {}),
            )
        )

    return years, blocks
