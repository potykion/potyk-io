from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from potyk_io_back.core.db import db

MSK = ZoneInfo("Europe/Moscow")

STAT_KEYS = ("day", "week", "month", "year", "total")


class HealthStataItem(db.Model):
    """Справочник дел для статы (медитация, спорт и т.п.)."""

    __tablename__ = "health_stata_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)


class HealthStataEntry(db.Model):
    """Одна галочка по одному делу."""

    __tablename__ = "health_stata_entries"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(
        db.Integer,
        db.ForeignKey("health_stata_items.id"),
        nullable=False,
        index=True,
    )
    done_at = db.Column(db.DateTime, nullable=False, index=True)


def _now_msk(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now(tz=MSK)
    if now.tzinfo is None:
        return now.replace(tzinfo=MSK)
    return now.astimezone(MSK)


def wall_now(now: datetime | None = None) -> datetime:
    """Наивное локальное время (МСК) для записи в БД."""
    return _now_msk(now).replace(tzinfo=None)


def list_stata_items() -> list[HealthStataItem]:
    return list(db.session.scalars(select(HealthStataItem).order_by(HealthStataItem.name)))


def get_or_create_stata_items(names: list[str]) -> list[HealthStataItem]:
    items: list[HealthStataItem] = []
    seen: set[str] = set()
    for raw in names:
        name = (raw or "").strip()
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        item = db.session.scalar(select(HealthStataItem).where(HealthStataItem.name == name))
        if item is None:
            item = HealthStataItem(name=name)
            db.session.add(item)
            db.session.flush()
        items.append(item)
    return items


def _period_starts(now: datetime | None = None) -> dict[str, datetime | None]:
    msk = _now_msk(now)
    today = msk.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    return {
        "day": datetime.combine(today, time.min),
        "week": datetime.combine(week_start, time.min),
        "month": datetime.combine(month_start, time.min),
        "year": datetime.combine(year_start, time.min),
        "total": None,
    }


def _count_entries(item_id: int, since: datetime | None) -> int:
    q = (
        select(func.count())
        .select_from(HealthStataEntry)
        .where(HealthStataEntry.item_id == item_id)
    )
    if since is not None:
        q = q.where(HealthStataEntry.done_at >= since)
    return db.session.scalar(q) or 0


def stata_stats(now: datetime | None = None) -> list[dict]:
    """Счётчики по каждому делу: день / неделя / месяц / год / всего."""
    starts = _period_starts(now)
    result: list[dict] = []
    for item in list_stata_items():
        row: dict = {"id": item.id, "name": item.name}
        for key in STAT_KEYS:
            row[key] = _count_entries(item.id, starts[key])
        result.append(row)
    return result


def add_stata_entries(names: list[str], now: datetime | None = None) -> list[dict]:
    items = get_or_create_stata_items(names)
    if not items:
        return stata_stats(now)
    stamp = wall_now(now)
    for item in items:
        db.session.add(HealthStataEntry(item_id=item.id, done_at=stamp))
    db.session.commit()
    return stata_stats(now)
