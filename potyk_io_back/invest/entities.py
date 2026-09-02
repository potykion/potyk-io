from decimal import Decimal

from sqlalchemy import select

from potyk_io_back.core.db import db


class InvestDepositChange(db.Model):
    __tablename__ = "invest_deposit_changes"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    amount = db.Column(db.Numeric(18, 2), nullable=False)


class InvestDeal(db.Model):
    __tablename__ = "invest_deals"

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(32), nullable=False, index=True)
    opened_at = db.Column(db.DateTime, nullable=False, index=True)
    volume = db.Column(db.Numeric(18, 2), nullable=False)
    buy_price = db.Column(db.Numeric(18, 6), nullable=False)
    qty = db.Column(db.Numeric(18, 6), nullable=False)
    entry_level = db.Column(db.Numeric(18, 6), nullable=True)
    exit_level = db.Column(db.Numeric(18, 6), nullable=True)
    take_profit_raw = db.Column(db.String(32), nullable=False, default="")
    take_profit_price = db.Column(db.Numeric(18, 6), nullable=True)
    stop_loss_raw = db.Column(db.String(32), nullable=False, default="")
    stop_loss_price = db.Column(db.Numeric(18, 6), nullable=True)
    thoughts = db.Column(db.Text, nullable=False, default="")
    closed_at = db.Column(db.DateTime, nullable=True, index=True)
    sell_price = db.Column(db.Numeric(18, 6), nullable=True)
    pnl = db.Column(db.Numeric(18, 2), nullable=True)
    close_thoughts = db.Column(db.Text, nullable=False, default="")
    close_errors = db.Column(db.Text, nullable=False, default="")

    @property
    def is_closed(self) -> bool:
        return self.closed_at is not None

    @property
    def pnl_pct(self) -> Decimal | None:
        if self.sell_price is None or not self.buy_price:
            return None
        buy = Decimal(self.buy_price)
        sell = Decimal(self.sell_price)
        return ((sell - buy) / buy * Decimal(100)).quantize(Decimal("0.01"))


class InvestTickerLevel(db.Model):
    __tablename__ = "invest_ticker_levels"

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(32), nullable=False, unique=True, index=True)
    entry_level = db.Column(db.Numeric(18, 6), nullable=True)
    exit_level = db.Column(db.Numeric(18, 6), nullable=True)


class InvestTicker(db.Model):
    __tablename__ = "invest_tickers"

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(64), nullable=False, unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    asset_type = db.Column(db.String(16), nullable=False, index=True)
    sector = db.Column(db.String(255), nullable=False, default="")
    dependencies = db.Column(db.JSON, nullable=False, default=list)
    fee = db.Column(db.Numeric(8, 4), nullable=True)
    management_company = db.Column(db.String(255), nullable=False, default="")


class InvestNews(db.Model):
    __tablename__ = "invest_news"

    id = db.Column(db.Integer, primary_key=True)

    # slug нужен для URL `/invest/Новости/<slug>` и как отображаемое название на карточках.
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)

    datetime = db.Column(db.DateTime, nullable=False, index=True)
    ticker = db.Column(db.String(64), nullable=False, index=True)

    source = db.Column(db.String(255), nullable=False, default="")
    summary = db.Column(db.Text, nullable=False, default="")
    price = db.Column(db.String(64), nullable=False, default="")

    # В старом vault это было emoji из frontmatter (🟢/🟡/🔴).
    sentiment = db.Column(db.String(16), nullable=False, default="")

    # Покупать / держать / наблюдать / продавать
    action = db.Column(db.String(32), nullable=False, default="наблюдать")

    # Markdown body (часть файла после frontmatter), рендерится в HTML на странице новости.
    content = db.Column(db.Text, nullable=False, default="")


def load_source_choices_from_db() -> list[tuple[str, str]]:
    """Уникальные непустые источники из invest_news, отсортированные по убыванию даты."""
    rows = db.session.execute(
        select(InvestNews.source)
        .where(InvestNews.source != "")
        .group_by(InvestNews.source)
        .order_by(InvestNews.source.desc())
    ).scalars().all()
    return [(s, s) for s in rows if s]


def load_ticker_choices_from_db() -> list[tuple[str, str]]:
    """
    (value, label) для Tom Select: value = тикер, label = "TICKER Имя".
    """
    rows = db.session.scalars(select(InvestTicker).order_by(InvestTicker.ticker.asc()))
    choices: list[tuple[str, str]] = []
    for r in rows:
        ticker = (r.ticker or "").strip()
        name = (r.name or "").strip()
        if not ticker:
            continue
        label = ticker if (not name or name == ticker) else f"{ticker} {name}"
        choices.append((ticker, label))
    return choices


def current_deposit() -> Decimal:
    row = db.session.scalars(
        select(InvestDepositChange).order_by(
            InvestDepositChange.date.desc(),
            InvestDepositChange.id.desc(),
        )
    ).first()
    if row is None:
        return Decimal("0")
    return Decimal(row.amount)
