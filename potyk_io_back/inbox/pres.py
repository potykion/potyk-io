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

PROD_BASE_URL = os.environ.get(
    "POTYK_IO_PROD_URL",
    "https://potyk.io",
).rstrip("/")
PROD_EXPORT_URL = PROD_BASE_URL + "/inbox/export.json"
PROD_ACK_URL = PROD_BASE_URL + "/inbox/ack.json"


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


@inbox_bp.post("/ack.json")
def ack_json():
    secret = request.headers.get("X-Inbox-Secret") or request.args.get("secret")
    if not check_export_secret(secret):
        abort(401)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        abort(400)
    raw_ids = payload.get("ids")
    if not isinstance(raw_ids, list):
        abort(400)

    ids: list[int] = []
    for value in raw_ids:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            ids.append(value)
        elif isinstance(value, str) and value.isdigit():
            ids.append(int(value))
    ids = list(dict.fromkeys(ids))
    if not ids:
        return jsonify({"deleted": 0})

    rows = db.session.scalars(select(Issue).where(Issue.id.in_(ids))).all()
    for row in rows:
        db.session.delete(row)
    db.session.commit()
    return jsonify({"deleted": len(rows)})


def _prod_headers(secret: str) -> dict[str, str]:
    return {
        "X-Inbox-Secret": secret,
        "Accept": "application/json",
        "User-Agent": "potyk-io-inbox-pull",
    }


def ack_prod_items(secret: str, ids: list[int]) -> int:
    body = json.dumps({"ids": ids}).encode("utf-8")
    req = Request(
        PROD_ACK_URL,
        data=body,
        headers={
            **_prod_headers(secret),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    deleted = payload.get("deleted") if isinstance(payload, dict) else None
    if not isinstance(deleted, int):
        raise ValueError("ack вернул странный ответ")
    return deleted


@inbox_bp.post("/pull")
@login_required
def pull():
    if not is_local():
        abort(404)

    form = PullForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return redirect(url_for("inbox.index"))

    secret = form.secret.data
    req = Request(
        PROD_EXPORT_URL,
        headers=_prod_headers(secret),
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

    saved, skipped, synced_ids = save_prod_items(items)
    if saved == 0 and skipped == 0:
        flash("На проде пусто", "success")
        return redirect(url_for("inbox.index"))

    deleted: int | None = None
    if synced_ids:
        try:
            deleted = ack_prod_items(secret, synced_ids)
        except HTTPError as exc:
            if exc.code == 401:
                flash(
                    f"Выгружено {saved}, пропущено {skipped}; "
                    "на проде не удалил — неверный секрет",
                    "error",
                )
            else:
                flash(
                    f"Выгружено {saved}, пропущено {skipped}; "
                    f"на проде не удалил — ответ {exc.code}",
                    "error",
                )
            return redirect(url_for("inbox.index"))
        except URLError as exc:
            flash(
                f"Выгружено {saved}, пропущено {skipped}; "
                f"на проде не удалил: {exc.reason}",
                "error",
            )
            return redirect(url_for("inbox.index"))
        except (json.JSONDecodeError, ValueError, TypeError):
            flash(
                f"Выгружено {saved}, пропущено {skipped}; "
                "на проде не удалил — странный ответ ack",
                "error",
            )
            return redirect(url_for("inbox.index"))

    flash(f"Выгружено {saved}, пропущено {skipped}, удалено на проде {deleted or 0}", "success")
    return redirect(url_for("inbox.index"))
