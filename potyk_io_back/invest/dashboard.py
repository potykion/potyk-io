"""Сборка дашборда новостей из vault potyk-invest."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import markdown
import yaml

from potyk_io_back.potyk_io.md_rendering.render import MD_EXTENSIONS

INVEST_DIR = Path(__file__).resolve().parents[2] / "templates" / "potyk-invest"
TICKERS_DIR = INVEST_DIR / "Тикеры"
NEWS_DIR = INVEST_DIR / "Новости"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
WIKI_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")

EMPTY_SECTOR = "Без сектора"


@dataclass
class Ticker:
    name: str
    sector: str = ""
    deps: str = ""


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
    ticker_key: str


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


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        return {}, text[match.end() :]
    return meta, text[match.end() :]


def prop_label(raw) -> str:
    if raw is None or raw == "":
        return ""
    items = raw if isinstance(raw, list) else [raw]
    return ", ".join(str(x).strip() for x in items if str(x).strip())


def wiki_target(raw) -> str:
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


def fmt_val(v) -> str:
    if v is None:
        return ""
    return str(v).strip()


def sentiment_tone(sentiment: str) -> str:
    if "🟢" in sentiment:
        return "pos"
    if "🟡" in sentiment:
        return "neu"
    if "🔴" in sentiment:
        return "neg"
    return "none"


def parse_datetime(raw) -> datetime | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, datetime):
        return raw
    s = str(raw).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def fmt_datetime(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%d.%m.%Y %H:%M")


def load_tickers() -> list[Ticker]:
    tickers: list[Ticker] = []
    if not TICKERS_DIR.is_dir():
        return tickers
    for path in sorted(TICKERS_DIR.glob("*.md")):
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8-sig"))
        tickers.append(
            Ticker(
                name=path.stem,
                sector=prop_label(meta.get("Сектор")),
                deps=prop_label(meta.get("Зависимости")),
            )
        )
    return tickers


def resolve_ticker(tickers: list[Ticker], key: str) -> Ticker | None:
    stem = key.split("/")[-1].split("|")[0].strip()
    if not stem:
        return None
    code = stem.split()[0]
    for t in tickers:
        name = t.name
        if name == stem or name == code or name.startswith(code + " "):
            return t
        parts = name.split()
        if code in parts:
            return t
    return None


def news_url(stem: str) -> str:
    return "/invest/Новости/" + quote(stem, safe="")


def resolve_news(slug: str) -> Path | None:
    """Безопасно резолвит md-файл новости по slug из URL."""
    name = Path(slug.strip()).name
    if name.lower().endswith(".md"):
        name = name[:-3]
    if not name or name in {".", ".."}:
        return None
    root = NEWS_DIR.resolve()
    path = (NEWS_DIR / f"{name}.md").resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path if path.is_file() else None


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
    content_html: str


def load_news_page(slug: str) -> NewsPage | None:
    path = resolve_news(slug)
    if path is None:
        return None

    meta, body = parse_frontmatter(path.read_text(encoding="utf-8-sig"))
    sentiment = fmt_val(meta.get("sentiment"))
    body = body.strip()
    content_html = (
        markdown.markdown(body, extensions=MD_EXTENSIONS, output_format="html")
        if body
        else ""
    )
    return NewsPage(
        title=path.stem,
        datetime_fmt=fmt_datetime(parse_datetime(meta.get("datetime"))),
        ticker=wiki_target(meta.get("ticker")),
        source=wiki_target(meta.get("source")),
        sentiment=sentiment,
        sentiment_tone=sentiment_tone(sentiment),
        price=fmt_val(meta.get("price")),
        summary=fmt_val(meta.get("summary")),
        content_html=content_html,
    )


def load_news() -> list[NewsItem]:
    items: list[NewsItem] = []
    if not NEWS_DIR.is_dir():
        return items
    for path in NEWS_DIR.glob("*.md"):
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8-sig"))
        ticker_key = wiki_target(meta.get("ticker"))
        if not ticker_key:
            continue
        dt = parse_datetime(meta.get("datetime"))
        sentiment = fmt_val(meta.get("sentiment"))
        items.append(
            NewsItem(
                title=path.stem,
                url=news_url(path.stem),
                datetime=dt,
                datetime_fmt=fmt_datetime(dt),
                sentiment=sentiment,
                sentiment_tone=sentiment_tone(sentiment),
                price=fmt_val(meta.get("price")),
                summary=fmt_val(meta.get("summary")) or "—",
                ticker_key=ticker_key,
            )
        )
    items.sort(key=lambda n: n.datetime or datetime.min, reverse=True)
    return items


def build_dashboard() -> list[SectorBlock]:
    tickers = load_tickers()
    news = load_news()

    by_key: dict[str, TickerGroup] = {}
    for item in news:
        page = resolve_ticker(tickers, item.ticker_key)
        key = page.name if page else item.ticker_key
        group = by_key.get(key)
        if group is None:
            group = TickerGroup(
                key=key,
                sector=page.sector if page else "",
                deps=page.deps if page else "",
            )
            by_key[key] = group
        group.news.append(item)

    groups = list(by_key.values())
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
