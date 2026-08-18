from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.invest.dashboard import build_dashboard, load_news_page
from potyk_io_back.invest.entities import InvestDeal, InvestDepositChange, current_deposit
from potyk_io_back.invest.forms import MAX_VOLUME_PCT, DealForm, DepositForm
from potyk_io_back.invest.menu import INVEST_MENU_ITEMS, is_invest_link_active

invest_bp = Blueprint("invest", __name__, url_prefix="/invest")


def flash_form_errors(form) -> None:
    for messages in form.errors.values():
        for message in messages:
            flash(message, "error")


def money(value) -> str:
    if value is None:
        return "—"
    quantized = Decimal(value).quantize(Decimal("0.01"))
    formatted = f"{quantized:,.2f}".replace(",", " ")
    if formatted.endswith(" 00"):
        return formatted[:-3]
    if formatted.endswith("0") and "." in formatted.replace(" ", ""):
        return formatted.rstrip("0").rstrip(".")
    return formatted


def price(value) -> str:
    if value is None:
        return "—"
    quantized = Decimal(value).normalize()
    text = format(quantized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


@invest_bp.app_template_filter("invest_money")
def invest_money_filter(value) -> str:
    return money(value)


@invest_bp.app_template_filter("invest_price")
def invest_price_filter(value) -> str:
    return price(value)


@invest_bp.context_processor
def inject_invest_menu():
    items = [
        {
            "icon": item["icon"],
            "title": item["title"],
            "url": item["url"],
            "active": is_invest_link_active(item["url"], request.path),
        }
        for item in INVEST_MENU_ITEMS
    ]
    return {"invest_menu_items": items}


@invest_bp.route("/")
def index():
    return render_template("potyk-invest/index.html", sectors=build_dashboard())


@invest_bp.route("/Новости/<path:slug>")
def news(slug: str):
    page = load_news_page(slug)
    if page is None:
        abort(404)
    return render_template("potyk-invest/news.html", page=page)


def deals_context(
    *,
    deposit_form: DepositForm | None = None,
    deal_form: DealForm | None = None,
    open_panel: str | None = None,
) -> dict:
    deposit = current_deposit()
    changes = db.session.scalars(
        select(InvestDepositChange).order_by(
            InvestDepositChange.date.desc(),
            InvestDepositChange.id.desc(),
        )
    ).all()
    deals = db.session.scalars(
        select(InvestDeal).order_by(InvestDeal.opened_at.desc(), InvestDeal.id.desc())
    ).all()
    if deposit_form is None:
        deposit_form = DepositForm(data={"amount": deposit})
    return {
        "deposit": deposit,
        "deposit_changes": changes,
        "deals": deals,
        "deposit_form": deposit_form,
        "deal_form": deal_form or DealForm(deposit=deposit),
        "open_panel": open_panel,
        "max_volume": (deposit * MAX_VOLUME_PCT / Decimal("100")),
    }


def render_deals(**kwargs):
    return render_template("potyk-invest/deals.html", **deals_context(**kwargs))


@invest_bp.route("/deals")
@login_required
def deals():
    return render_deals()


@invest_bp.post("/deals/deposit")
@login_required
def update_deposit():
    form = DepositForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_deals(deposit_form=form, open_panel="deposit"), 400

    db.session.add(
        InvestDepositChange(
            date=form.date.data,
            amount=form.amount.data,
        )
    )
    db.session.commit()
    flash("Депозит обновлён", "success")
    return redirect(url_for("invest.deals"))


@invest_bp.post("/deals")
@login_required
def add_deal():
    deposit = current_deposit()
    form = DealForm(deposit=deposit)
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_deals(deal_form=form, open_panel="deal"), 400

    db.session.add(
        InvestDeal(
            ticker=form.ticker.data.strip().upper(),
            opened_at=form.opened_at.data,
            volume=form.volume.data,
            buy_price=form.buy_price.data,
            qty=form.qty,
            entry_level=form.entry_level.data,
            exit_level=form.exit_level.data,
            take_profit_raw=(form.take_profit.data or "").strip(),
            take_profit_price=form.take_profit_price,
            stop_loss_raw=(form.stop_loss.data or "").strip(),
            stop_loss_price=form.stop_loss_price,
            thoughts=(form.thoughts.data or "").strip(),
        )
    )
    db.session.commit()
    flash("Сделка добавлена", "success")
    return redirect(url_for("invest.deals"))
