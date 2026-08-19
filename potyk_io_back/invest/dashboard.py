"""Сборка дашборда новостей из SQL (invest_news)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import quote

import markdown
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.invest.entities import InvestNews, InvestTicker
from potyk_io_back.potyk_io.md_rendering.render import MD_EXTENSIONS

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
    content_html = markdown.markdown(body, extensions=MD_EXTENSIONS, output_format="html") if body else ""

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
