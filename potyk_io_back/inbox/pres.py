from __future__ import annotations

import hmac
import json
import os
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.inbox.entities import Issue
from potyk_io_back.inbox.forms import PullForm, SendForm
from potyk_io_back.inbox.tasks import InboxEntry, load_local_tasks, save_prod_items
from potyk_io_back.potyk_io.menu import MENU_GROUPS

inbox_bp = Blueprint("inbox", __name__, url_prefix="/inbox")

PROD_EXPORT_URL = os.environ.get(
    "POTYK_IO_PROD_URL",
    "https://potyk.io",
).rstrip("/") + "/inbox/export.json"


@inbox_bp.context_processor
def inject_menu():
    return {
        "menu_groups": MENU_GROUPS,
    }


def flash_form_errors(form) -> None:
    for messages in form.errors.values():
        for message in messages:
            flash(message, "error")


def is_local() -> bool:
    if current_app.debug:
        return True
    host = (request.host or "").lower()
    return (
        host.startswith("localhost")
        or host.startswith("127.0.0.1")
        or host.startswith("[::1]")
    )


def check_export_secret(secret: str | None) -> bool:
    expected = os.environ.get("FLASK_SECRET", "")
    if not secret or not expected:
        return False
    if len(secret) != len(expected):
        return False
    return hmac.compare_digest(secret, expected)


def entries_from_db() -> list[InboxEntry]:
    rows = db.session.scalars(
        select(Issue).order_by(Issue.created_at.desc(), Issue.id.desc())
    ).all()
    entries: list[InboxEntry] = []
    for row in rows:
        text = row.text or ""
        title = text.strip().splitlines()[0].lstrip("# ").strip() if text.strip() else f"#{row.id}"
        entries.append(
            InboxEntry(
                project=row.project,
                status=row.status,
                text=text,
                created_at=row.created_at.isoformat(timespec="seconds") if row.created_at else None,
                title=title or f"#{row.id}",
            )
        )
    return entries


@inbox_bp.get("/")
@login_required
def index():
    local = is_local()
    items = load_local_tasks() if local else entries_from_db()
    return render_template(
        "inbox/index.html",
        items=items,
        is_local=local,
        pull_form=PullForm() if local else None,
    )


@inbox_bp.route("/send", methods=["GET", "POST"])
def send():
    form = SendForm()
    if form.validate_on_submit():
        db.session.add(
            Issue(
                project=form.project.data,
                status="new",
                text=form.text.data.strip(),
                created_at=datetime.now(),
            )
        )
        db.session.commit()
        flash("Отправлено", "success")
        return redirect(url_for("inbox.send"))
    if form.is_submitted():
        flash_form_errors(form)
    return render_template("inbox/send.html", form=form)


@inbox_bp.get("/export.json")
def export_json():
    secret = request.headers.get("X-Inbox-Secret") or request.args.get("secret")
    if not check_export_secret(secret):
        abort(401)
    rows = db.session.scalars(
        select(Issue).order_by(Issue.created_at.desc(), Issue.id.desc())
    ).all()
    return jsonify({"items": [row.to_dict() for row in rows]})


@inbox_bp.post("/pull")
@login_required
def pull():
    if not is_local():
        abort(404)

    form = PullForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return redirect(url_for("inbox.index"))

    req = Request(
        PROD_EXPORT_URL,
        headers={
            "X-Inbox-Secret": form.secret.data,
            "Accept": "application/json",
            "User-Agent": "potyk-io-inbox-pull",
        },
    )
    try:
        with urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 401:
            flash("неверный секрет", "error")
        else:
            flash(f"Прод ответил {exc.code}", "error")
        return redirect(url_for("inbox.index"))
    except URLError as exc:
        flash(f"Не достучался до прода: {exc.reason}", "error")
        return redirect(url_for("inbox.index"))
    except json.JSONDecodeError:
        flash("Прод вернул не JSON", "error")
        return redirect(url_for("inbox.index"))

    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        flash("Прод вернул странный ответ", "error")
        return redirect(url_for("inbox.index"))

    saved, skipped = save_prod_items(items)
    if saved == 0 and skipped == 0:
        flash("На проде пусто", "success")
    else:
        flash(f"Выгружено {saved}, пропущено {skipped}", "success")
    return redirect(url_for("inbox.index"))
