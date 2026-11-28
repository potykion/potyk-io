from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select

from potyk_io_back.core.db import db
from potyk_io_back.fin.budget import compute_days
from potyk_io_back.fin.entities import (
    ClosedDay,
    Expense,
    Saving,
    get_settings,
    next_unfilled_expense_date,
)
from potyk_io_back.fin.pres import (
    category_stats_for_period,
    categories_by_frequency,
    month_label_ru,
    next_calendar_month,
    prev_calendar_month,
)


def _expense_dict(expense) -> dict:
    return {
        "id": expense.id,
        "date": expense.date.isoformat(),
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description or "",
        "optional": bool(getattr(expense, "optional", False)),
        "running_balance": getattr(expense, "running_balance", None),
    }


def _saving_dict(saving: Saving) -> dict:
    return {
        "id": saving.id,
        "date": saving.date.isoformat(),
        "amount": saving.amount,
        "note": saving.note or "",
    }


def build_fin_state(
    *,
    stats_from: date | None = None,
    stats_to: date | None = None,
) -> dict:
    settings = get_settings()
    expenses = db.session.scalars(
        select(Expense).order_by(Expense.date, Expense.id)
    ).all()
    savings = db.session.scalars(
        select(Saving).order_by(Saving.date.desc(), Saving.id.desc())
    ).all()
    categories = categories_by_frequency(expenses)
    closed_dates = set(
        db.session.scalars(select(ClosedDay.date).order_by(ClosedDay.date)).all()
    )

    days = compute_days(
        expenses,
        settings.daily_budget,
        extra_dates=[s.date for s in savings],
    )
    saved_by_date: dict[date, int] = {}
    savings_by_date: dict[date, list[Saving]] = {}
    for s in savings:
        saved_by_date[s.date] = saved_by_date.get(s.date, 0) + s.amount
        savings_by_date.setdefault(s.date, []).append(s)
    for d in days:
        d.saved = saved_by_date.get(d.date, 0)
        d.savings = sorted(
            savings_by_date.get(d.date, []),
            key=lambda s: s.id,
            reverse=True,
        )

    today = date.today()
    if stats_from is None or stats_to is None:
        stats_to = today
        stats_from = today.replace(day=1)
    if stats_from > stats_to:
        stats_from, stats_to = stats_to, stats_from

    category_stats, stats_total = category_stats_for_period(
        expenses, stats_from, stats_to
    )
    stats_saved_total = sum(
        s.amount for s in savings if stats_from <= s.date <= stats_to
    )
    stats_expenses_plus_saves = stats_total + stats_saved_total
    prev_stats_from, prev_stats_to = prev_calendar_month(stats_from)
    next_month = next_calendar_month(stats_from, today)
    if next_month is None:
        next_stats_from = next_stats_to = None
        next_month_label = None
    else:
        next_stats_from, next_stats_to = next_month
        next_month_label = month_label_ru(next_stats_from)

    total_saved = db.session.scalar(select(func.coalesce(func.sum(Saving.amount), 0))) or 0
    auto_remainder_total = sum(d.eod_remainder for d in days if d.date < today)

    days_payload = []
    for d in reversed(days):
        days_payload.append(
            {
                "date": d.date.isoformat(),
                "budget": d.budget,
                "carry_in": d.carry_in,
                "start_available": d.start_available,
                "spent": d.spent,
                "end_balance": d.end_balance,
                "eod_remainder": d.eod_remainder,
                "carry_out": d.carry_out,
                "saved": d.saved,
                "closed": d.date in closed_dates,
                "expenses": [_expense_dict(e) for e in d.expenses],
                "savings": [_saving_dict(s) for s in d.savings],
            }
        )

    stats_rows = []
    for row in category_stats:
        stats_rows.append(
            {
                "category": row["category"],
                "total": row["total"],
                "count": row["count"],
                "avg": row["avg"],
                "share": row["share"],
                "expenses": [_expense_dict(e) for e in row["expenses"]],
            }
        )

    return {
        "today": today.isoformat(),
        "settings": {"daily_budget": settings.daily_budget},
        "categories": categories,
        "defaults": {
            "expense_date": next_unfilled_expense_date(
                today=today,
                last_operation_date=(
                    max([e.date for e in expenses] + [s.date for s in savings])
                    if (expenses or savings)
                    else None
                ),
            ).isoformat(),
            "saving_date": (today - timedelta(days=1)).isoformat(),
        },
        "today_closed": today in closed_dates,
        "total_saved": int(total_saved),
        "auto_remainder_total": int(auto_remainder_total),
        "stats": {
            "from": stats_from.isoformat(),
            "to": stats_to.isoformat(),
            "total": stats_total,
            "saved_total": stats_saved_total,
            "expenses_plus_saves": stats_expenses_plus_saves,
            "prev_from": prev_stats_from.isoformat(),
            "prev_to": prev_stats_to.isoformat(),
            "prev_month_label": month_label_ru(prev_stats_from),
            "next_from": next_stats_from.isoformat() if next_stats_from else None,
            "next_to": next_stats_to.isoformat() if next_stats_to else None,
            "next_month_label": next_month_label,
            "categories": stats_rows,
        },
        "days": days_payload,
    }
