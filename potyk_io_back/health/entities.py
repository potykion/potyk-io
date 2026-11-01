from __future__ import annotations

from datetime import datetime, time, timedelta
from math import ceil
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from potyk_io_back.core.db import db

MSK = ZoneInfo("Europe/Moscow")

STAT_KEYS = ("day", "week", "month", "year", "total")
KIND_DEED = "deed"
KIND_ACHIEVEMENT = "achievement"
MEDITATION_NAME = "Медитация"
DEFAULT_LOG_PER_PAGE = 20


class HealthStataItem(db.Model):
    """Справочник дел / достижений для статы."""

    __tablename__ = "health_stata_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    kind = db.Column(db.String(32), nullable=False, default=KIND_DEED, index=True)


class HealthStataEntry(db.Model):
    """Одна галочка по одному делу / достижению."""

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


def list_stata_items(kind: str = KIND_DEED) -> list[HealthStataItem]:
    return list(
        db.session.scalars(
            select(HealthStataItem)
            .where(HealthStataItem.kind == kind)
            .order_by(HealthStataItem.name)
        )
    )


def get_or_create_stata_items(
    names: list[str],
    *,
    kind: str = KIND_DEED,
) -> list[HealthStataItem]:
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
            item = HealthStataItem(name=name, kind=kind)
            db.session.add(item)
            db.session.flush()
        elif item.kind != kind:
            # Не смешиваем дело и достижение с одним именем.
            continue
        items.append(item)
    return items


def ensure_meditation_item() -> HealthStataItem:
    item = db.session.scalar(
        select(HealthStataItem).where(HealthStataItem.name == MEDITATION_NAME)
    )
    if item is None:
        item = HealthStataItem(name=MEDITATION_NAME, kind=KIND_DEED)
        db.session.add(item)
        db.session.commit()
    return item


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


def _stats_for_item(item: HealthStataItem, now: datetime | None = None) -> dict:
    starts = _period_starts(now)
    row: dict = {"id": item.id, "name": item.name}
    for key in STAT_KEYS:
        row[key] = _count_entries(item.id, starts[key])
    return row


def stata_stats(now: datetime | None = None, *, kind: str = KIND_DEED) -> list[dict]:
    """Счётчики по каждому делу/достижению: день / неделя / месяц / год / всего."""
    return [_stats_for_item(item, now) for item in list_stata_items(kind)]


def meditation_stats(now: datetime | None = None) -> dict[str, int]:
    item = ensure_meditation_item()
    row = _stats_for_item(item, now)
    return {key: int(row[key]) for key in STAT_KEYS}


def add_meditation(now: datetime | None = None) -> dict[str, int]:
    item = ensure_meditation_item()
    db.session.add(HealthStataEntry(item_id=item.id, done_at=wall_now(now)))
    db.session.commit()
    return meditation_stats(now)


def add_stata_entries(
    names: list[str],
    now: datetime | None = None,
    *,
    kind: str = KIND_DEED,
) -> list[dict]:
    items = get_or_create_stata_items(names, kind=kind)
    if not items:
        return stata_stats(now, kind=kind)
    stamp = wall_now(now)
    for item in items:
        db.session.add(HealthStataEntry(item_id=item.id, done_at=stamp))
    db.session.commit()
    return stata_stats(now, kind=kind)


def delete_stata_entry(entry_id: int, *, kind: str = KIND_DEED) -> bool:
    entry = db.session.get(HealthStataEntry, entry_id)
    if entry is None:
        return False
    item = db.session.get(HealthStataItem, entry.item_id)
    if item is None or item.kind != kind:
        return False
    db.session.delete(entry)
    db.session.commit()
    return True


def list_stata_log(
    *,
    kind: str = KIND_DEED,
    page: int = 1,
    per_page: int = DEFAULT_LOG_PER_PAGE,
) -> dict:
    """Журнал отметок: дело + когда, с пагинацией (новые сверху)."""
    page = max(1, int(page or 1))
    per_page = max(1, min(100, int(per_page or DEFAULT_LOG_PER_PAGE)))

    base = (
        select(HealthStataEntry, HealthStataItem.name)
        .join(HealthStataItem, HealthStataItem.id == HealthStataEntry.item_id)
        .where(HealthStataItem.kind == kind)
    )
    total = db.session.scalar(
        select(func.count())
        .select_from(HealthStataEntry)
        .join(HealthStataItem, HealthStataItem.id == HealthStataEntry.item_id)
        .where(HealthStataItem.kind == kind)
    ) or 0
    pages = max(1, ceil(total / per_page)) if total else 1
    if page > pages:
        page = pages

    rows = db.session.execute(
        base.order_by(HealthStataEntry.done_at.desc(), HealthStataEntry.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()

    entries = [
        {
            "id": entry.id,
            "name": name,
            "done_at": entry.done_at,
            "done_at_label": entry.done_at.strftime("%d.%m.%Y %H:%M") if entry.done_at else "",
        }
        for entry, name in rows
    ]
    return {
        "entries": entries,
        "page": page,
        "pages": pages,
        "total": int(total),
        "per_page": per_page,
        "has_prev": page > 1,
        "has_next": page < pages,
    }
