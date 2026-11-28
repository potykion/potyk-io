from datetime import date, timedelta

from sqlalchemy import func, select

from potyk_io_back.core.db import db


def normalize_expense_category(category: str) -> str:
    text = (category or "").strip()
    if not text:
        return text
    return text[0].upper() + text[1:].casefold()


def next_unfilled_expense_date(
    *,
    today: date | None = None,
    last_operation_date: date | None = None,
) -> date:
    """Дата последней операции (трата/сейв) + 1 день; не позже сегодня. Без операций — вчера."""
    today = today or date.today()
    if last_operation_date is None:
        last_expense = db.session.scalar(select(func.max(Expense.date)))
        last_saving = db.session.scalar(select(func.max(Saving.date)))
        candidates = [d for d in (last_expense, last_saving) if d is not None]
        last_operation_date = max(candidates) if candidates else None
    if last_operation_date is None:
        return today - timedelta(days=1)
    nxt = last_operation_date + timedelta(days=1)
    return nxt if nxt <= today else today


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    optional = db.Column(db.Boolean, nullable=False, default=False)


class Saving(db.Model):
    __tablename__ = "savings"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(255), nullable=False, default="")


class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    daily_budget = db.Column(db.Integer, nullable=False, default=10_000)


class ClosedDay(db.Model):
    __tablename__ = "closed_days"

    date = db.Column(db.Date, primary_key=True)


def get_settings() -> Settings:
    settings = db.session.get(Settings, 1)
    if settings is None:
        settings = Settings(id=1, daily_budget=10_000)
        db.session.add(settings)
        db.session.commit()
    return settings
