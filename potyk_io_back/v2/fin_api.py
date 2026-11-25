from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from flask_login import login_required

from potyk_io_back.core.db import db
from potyk_io_back.fin.entities import (
    ClosedDay,
    Expense,
    Saving,
    get_settings,
    normalize_expense_category,
)
from potyk_io_back.v2.fin_state import build_fin_state


def _parse_date(value: str | None, field: str) -> date:
    if not value:
        raise ValueError(f"Укажи {field}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Некорректная дата ({field})") from exc


def _parse_positive_int(value, field: str) -> int:
    try:
        amount = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Укажи {field}") from exc
    if amount < 1:
        raise ValueError(f"Укажи положительную {field}")
    return amount


def _stats_args() -> tuple[date | None, date | None]:
    raw_from = request.args.get("stats_from")
    raw_to = request.args.get("stats_to")
    if not raw_from or not raw_to:
        return None, None
    try:
        return date.fromisoformat(raw_from), date.fromisoformat(raw_to)
    except ValueError:
        return None, None


def _state_response():
    stats_from, stats_to = _stats_args()
    body = request.get_json(silent=True) or {}
    if stats_from is None and body.get("stats_from") and body.get("stats_to"):
        try:
            stats_from = date.fromisoformat(body["stats_from"])
            stats_to = date.fromisoformat(body["stats_to"])
        except ValueError:
            stats_from = stats_to = None
    return jsonify(build_fin_state(stats_from=stats_from, stats_to=stats_to))


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def register_fin_api(bp: Blueprint) -> None:
    @bp.get("/api/fin")
    @login_required
    def api_fin_state():
        return _state_response()

    @bp.post("/api/fin/expenses")
    @login_required
    def api_add_expense():
        data = request.get_json(silent=True) or {}
        try:
            expense = Expense(
                date=_parse_date(data.get("date"), "дату"),
                amount=_parse_positive_int(data.get("amount"), "сумму"),
                category=normalize_expense_category(str(data.get("category") or "")),
                description=str(data.get("description") or "").strip()[:255],
                optional=bool(data.get("optional")),
            )
            if not expense.category:
                raise ValueError("Укажи категорию")
            if len(expense.category) > 64:
                raise ValueError("Категория слишком длинная")
        except ValueError as exc:
            return _error(str(exc))
        db.session.add(expense)
        db.session.commit()
        return _state_response()

    @bp.post("/api/fin/expenses/bulk")
    @login_required
    def api_add_expenses_bulk():
        data = request.get_json(silent=True) or {}
        rows = data.get("expenses") or []
        if not isinstance(rows, list) or not rows:
            return _error("Добавь хотя бы одну трату")
        try:
            for row in rows:
                category = normalize_expense_category(str(row.get("category") or ""))
                if not category:
                    raise ValueError("Укажи категорию")
                if len(category) > 64:
                    raise ValueError("Категория слишком длинная")
                db.session.add(
                    Expense(
                        date=_parse_date(row.get("date"), "дату"),
                        amount=_parse_positive_int(row.get("amount"), "сумму"),
                        category=category,
                        description=str(row.get("description") or "").strip()[:255],
                        optional=bool(row.get("optional")),
                    )
                )
        except ValueError as exc:
            db.session.rollback()
            return _error(str(exc))
        db.session.commit()
        return _state_response()

    @bp.put("/api/fin/expenses/<int:expense_id>")
    @login_required
    def api_edit_expense(expense_id: int):
        expense = db.session.get(Expense, expense_id)
        if expense is None:
            return _error("Трата не найдена", 404)
        data = request.get_json(silent=True) or {}
        try:
            category = normalize_expense_category(str(data.get("category") or ""))
            if not category:
                raise ValueError("Укажи категорию")
            expense.date = _parse_date(data.get("date"), "дату")
            expense.amount = _parse_positive_int(data.get("amount"), "сумму")
            expense.category = category
            expense.description = str(data.get("description") or "").strip()[:255]
            expense.optional = bool(data.get("optional"))
        except ValueError as exc:
            return _error(str(exc))
        db.session.commit()
        return _state_response()

    @bp.delete("/api/fin/expenses/<int:expense_id>")
    @login_required
    def api_delete_expense(expense_id: int):
        expense = db.session.get(Expense, expense_id)
        if expense is None:
            return _error("Трата не найдена", 404)
        db.session.delete(expense)
        db.session.commit()
        return _state_response()

    @bp.post("/api/fin/savings")
    @login_required
    def api_add_saving():
        data = request.get_json(silent=True) or {}
        try:
            saving = Saving(
                date=_parse_date(data.get("date"), "дату"),
                amount=_parse_positive_int(data.get("amount"), "сумму"),
                note=str(data.get("note") or "").strip()[:255],
            )
        except ValueError as exc:
            return _error(str(exc))
        db.session.add(saving)
        db.session.commit()
        return _state_response()

    @bp.put("/api/fin/savings/<int:saving_id>")
    @login_required
    def api_edit_saving(saving_id: int):
        saving = db.session.get(Saving, saving_id)
        if saving is None:
            return _error("Сейв не найден", 404)
        data = request.get_json(silent=True) or {}
        try:
            saving.date = _parse_date(data.get("date"), "дату")
            saving.amount = _parse_positive_int(data.get("amount"), "сумму")
            saving.note = str(data.get("note") or "").strip()[:255]
        except ValueError as exc:
            return _error(str(exc))
        db.session.commit()
        return _state_response()

    @bp.delete("/api/fin/savings/<int:saving_id>")
    @login_required
    def api_delete_saving(saving_id: int):
        saving = db.session.get(Saving, saving_id)
        if saving is None:
            return _error("Сейв не найден", 404)
        db.session.delete(saving)
        db.session.commit()
        return _state_response()

    @bp.put("/api/fin/settings/budget")
    @login_required
    def api_update_budget():
        data = request.get_json(silent=True) or {}
        try:
            daily_budget = _parse_positive_int(data.get("daily_budget"), "бюджет")
        except ValueError as exc:
            return _error(str(exc))
        settings = get_settings()
        settings.daily_budget = daily_budget
        db.session.commit()
        return _state_response()

    @bp.put("/api/fin/days/<date_str>/close")
    @login_required
    def api_toggle_day_close(date_str: str):
        try:
            day = date.fromisoformat(date_str)
        except ValueError:
            return _error("Некорректная дата")
        data = request.get_json(silent=True) or {}
        closed = bool(data.get("closed"))
        row = db.session.get(ClosedDay, day)
        if closed and row is None:
            db.session.add(ClosedDay(date=day))
        elif not closed and row is not None:
            db.session.delete(row)
        db.session.commit()
        return _state_response()
