from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import func, select

from potyk_io_back.core.db import db
from potyk_io_back.fin.budget import compute_days
from potyk_io_back.fin.entities import (
    ClosedDay,
    Expense,
    Saving,
    get_settings,
    normalize_expense_category,
)
from potyk_io_back.fin.forms import BudgetForm, CloseDayForm, DeleteForm, ExpenseForm, SavingForm

fin_bp = Blueprint("fin", __name__, url_prefix="/fin")


def flash_form_errors(form) -> None:
    for messages in form.errors.values():
        for message in messages:
            flash(message, "error")


def is_htmx() -> bool:
    return request.headers.get("HX-Request") == "true"


def category_stats_for_period(
    expenses: list[Expense],
    date_from: date,
    date_to: date,
) -> tuple[list[dict], int]:
    totals: dict[str, int] = {}
    display: dict[str, str] = {}
    ops: dict[str, list[Expense]] = {}
    for expense in expenses:
        if expense.date < date_from or expense.date > date_to:
            continue
        key = expense.category.casefold()
        totals[key] = totals.get(key, 0) + expense.amount
        if key not in display:
            display[key] = normalize_expense_category(expense.category)
        ops.setdefault(key, []).append(expense)

    max_total = max(totals.values(), default=0)
    rows = []
    for key, total in totals.items():
        items = sorted(ops[key], key=lambda e: (e.date, e.id), reverse=True)
        rows.append(
            {
                "category": display[key],
                "total": total,
                "share": (total / max_total) if max_total else 0,
                "expenses": items,
            }
        )
    rows.sort(key=lambda r: (-r["total"], r["category"].casefold()))
    return rows, sum(r["total"] for r in rows)


def index_context(
    *,
    open_panel: str | None = None,
    expense_form: ExpenseForm | None = None,
    saving_form: SavingForm | None = None,
    budget_form: BudgetForm | None = None,
) -> dict:
    settings = get_settings()
    expenses = db.session.scalars(
        select(Expense).order_by(Expense.date, Expense.id)
    ).all()
    savings = db.session.scalars(
        select(Saving).order_by(Saving.date.desc(), Saving.id.desc())
    ).all()
    raw_categories = db.session.scalars(select(Expense.category).distinct()).all()
    categories_by_key = {
        normalize_expense_category(c).casefold(): normalize_expense_category(c)
        for c in raw_categories
        if c
    }
    categories = sorted(categories_by_key.values(), key=str.casefold)
    closed_dates = set(
        db.session.scalars(select(ClosedDay.date).order_by(ClosedDay.date)).all()
    )

    days = compute_days(
        expenses,
        settings.daily_budget,
        extra_dates=[s.date for s in savings],
    )
    saved_by_date: dict[date, int] = {}
    for s in savings:
        saved_by_date[s.date] = saved_by_date.get(s.date, 0) + s.amount
    for d in days:
        d.saved = saved_by_date.get(d.date, 0)

    days_desc = list(reversed(days))
    today = date.today()
    stats_to = today
    stats_from = today.replace(day=1)

    stats_from_raw = request.args.get("stats_from")
    stats_to_raw = request.args.get("stats_to")
    if stats_from_raw and stats_to_raw:
        try:
            stats_from = date.fromisoformat(stats_from_raw)
            stats_to = date.fromisoformat(stats_to_raw)
            if stats_from > stats_to:
                stats_from, stats_to = stats_to, stats_from
        except ValueError:
            pass

    category_stats, stats_total = category_stats_for_period(
        expenses, stats_from, stats_to
    )
    today_state = next((d for d in days if d.date == today), None)
    total_saved = db.session.scalar(select(func.coalesce(func.sum(Saving.amount), 0))) or 0
    auto_remainder_total = sum(d.eod_remainder for d in days if d.date < today)

    if budget_form is None:
        budget_form = BudgetForm(data={"daily_budget": settings.daily_budget})

    return {
        "settings": settings,
        "days": days_desc,
        "today": today,
        "today_state": today_state,
        "savings": savings,
        "total_saved": total_saved,
        "auto_remainder_total": auto_remainder_total,
        "stats_from": stats_from,
        "stats_to": stats_to,
        "category_stats": category_stats,
        "stats_total": stats_total,
        "closed_dates": closed_dates,
        "categories": categories,
        "expense_form": expense_form or ExpenseForm(),
        "saving_form": saving_form or SavingForm(),
        "budget_form": budget_form,
        "delete_form": DeleteForm(),
        "close_day_form": CloseDayForm(),
        "open_panel": open_panel,
    }


def render_index(**kwargs):
    return render_template("potyk-fin/index.html", **index_context(**kwargs))


@fin_bp.route("/")
@login_required
def index():
    return render_index()


@fin_bp.post("/days/<date_str>/close")
@login_required
def toggle_day_close(date_str: str):
    form = CloseDayForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return redirect(request.referrer or url_for("fin.index"))

    try:
        day = date.fromisoformat(date_str)
    except ValueError:
        flash("Некорректная дата", "error")
        return redirect(request.referrer or url_for("fin.index"))

    closed = request.form.get("closed") == "on"
    row = db.session.get(ClosedDay, day)
    if closed and row is None:
        db.session.add(ClosedDay(date=day))
    elif not closed and row is not None:
        db.session.delete(row)
    db.session.commit()
    return redirect(request.referrer or url_for("fin.index"))


@fin_bp.post("/expenses")
@login_required
def add_expense():
    form = ExpenseForm()
    if not form.validate_on_submit():
        if is_htmx():
            ctx = index_context(open_panel="expense", expense_form=form)
            return render_template("potyk-fin/partials/_expense_form.html", **ctx)
        flash_form_errors(form)
        return render_index(open_panel="expense", expense_form=form), 400

    expense = Expense(
        date=form.date.data,
        amount=form.amount.data,
        category=normalize_expense_category(form.category.data),
        description=(form.description.data or "").strip(),
        optional=form.optional.data,
    )
    db.session.add(expense)
    db.session.commit()

    if is_htmx():
        fresh = ExpenseForm(
            formdata=None,
            date=expense.date,
        )
        ctx = index_context(expense_form=fresh)
        return render_template("potyk-fin/partials/_expense_added.html", **ctx)

    flash("Трата добавлена", "success")
    return redirect(url_for("fin.index"))


@fin_bp.post("/expenses/<int:expense_id>/delete")
@login_required
def delete_expense(expense_id: int):
    form = DeleteForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return redirect(url_for("fin.index"))

    expense = db.session.get(Expense, expense_id)
    if expense is None:
        flash("Трата не найдена", "error")
        return redirect(url_for("fin.index"))
    db.session.delete(expense)
    db.session.commit()
    flash("Трата удалена", "success")
    return redirect(url_for("fin.index"))


@fin_bp.post("/savings")
@login_required
def add_saving():
    form = SavingForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_index(open_panel="saving", saving_form=form), 400

    db.session.add(
        Saving(
            date=form.date.data,
            amount=form.amount.data,
            note=(form.note.data or "").strip(),
        )
    )
    db.session.commit()
    flash("Сейв зафиксирован", "success")
    return redirect(url_for("fin.index"))


@fin_bp.post("/savings/<int:saving_id>/delete")
@login_required
def delete_saving(saving_id: int):
    form = DeleteForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return redirect(url_for("fin.index"))

    saving = db.session.get(Saving, saving_id)
    if saving is None:
        flash("Сейв не найден", "error")
        return redirect(url_for("fin.index"))
    db.session.delete(saving)
    db.session.commit()
    flash("Сейв удалён", "success")
    return redirect(url_for("fin.index"))


@fin_bp.post("/settings/budget")
@login_required
def update_budget():
    form = BudgetForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_index(open_panel="budget", budget_form=form), 400

    settings = get_settings()
    settings.daily_budget = form.daily_budget.data
    db.session.commit()
    flash("Бюджет на день обновлён", "success")
    return redirect(url_for("fin.index"))
