from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from potyk_io_back.core.db import db

MSK = ZoneInfo("Europe/Moscow")


class HealthMeditation(db.Model):
    """Одна запись = одна медитация."""

    __tablename__ = "health_meditations"

    id = db.Column(db.Integer, primary_key=True)
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


def _count_since(start: datetime) -> int:
    return (
        db.session.scalar(
            select(func.count())
            .select_from(HealthMeditation)
            .where(HealthMeditation.done_at >= start)
        )
        or 0
    )


def meditation_stats(now: datetime | None = None) -> dict[str, int]:
    """Счётчики: день / неделя / месяц / год / всего."""
    msk = _now_msk(now)
    today = msk.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    total = db.session.scalar(select(func.count()).select_from(HealthMeditation)) or 0
    return {
        "day": _count_since(datetime.combine(today, time.min)),
        "week": _count_since(datetime.combine(week_start, time.min)),
        "month": _count_since(datetime.combine(month_start, time.min)),
        "year": _count_since(datetime.combine(year_start, time.min)),
        "total": int(total),
    }


def add_meditation(now: datetime | None = None) -> dict[str, int]:
    db.session.add(HealthMeditation(done_at=wall_now(now)))
    db.session.commit()
    return meditation_stats(now)
