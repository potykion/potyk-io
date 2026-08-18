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
