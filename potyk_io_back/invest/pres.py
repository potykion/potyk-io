from decimal import Decimal

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import select

from potyk_io_back.core.db import db
from potyk_io_back.invest.dashboard import build_dashboard, load_news_page
from potyk_io_back.invest.entities import (
    InvestDeal,
    InvestDepositChange,
    InvestNews,
    InvestTickerLevel,
    current_deposit,
    load_source_choices_from_db,
    load_ticker_choices_from_db,
)
from potyk_io_back.invest.forms import (
    MAX_VOLUME_PCT,
    CloseDealForm,
    DealDeleteForm,
    DealForm,
    DepositForm,
    EditDealForm,
    NewsForm,
    TickerLevelForm,
    compute_pnl,
)
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
    ticker_choices = load_ticker_choices_from_db()
    source_choices = load_source_choices_from_db()
    news_form = NewsForm(ticker_choices=ticker_choices, source_choices=source_choices)
    return render_template(
        "potyk-invest/index.html",
        sectors=build_dashboard(),
        news_form=news_form,
        open_panel=None,
    )


@invest_bp.post("/")
@login_required
def add_news():
    ticker_choices = load_ticker_choices_from_db()
    source_choices = load_source_choices_from_db()
    form = NewsForm(ticker_choices=ticker_choices, source_choices=source_choices)
    if not form.validate_on_submit():
        flash_form_errors(form)
        return (
            render_template(
                "potyk-invest/index.html",
                sectors=build_dashboard(),
                news_form=form,
                open_panel="news",
            ),
            400,
        )

    dt = form.datetime.data
    ticker = form.ticker.data.strip().upper()

    slug_base = f"{dt:%Y-%m-%d} {dt:%H-%M} {ticker} {form.action.data}"
    slug_base = slug_base[:240]
    slug = slug_base
    i = 1
    while db.session.scalars(select(InvestNews.id).where(InvestNews.slug == slug)).first() is not None:
        i += 1
        slug = f"{slug_base} ({i})"
        slug = slug[:255]

    db.session.add(
        InvestNews(
            slug=slug,
            datetime=dt,
            ticker=ticker,
            source=(form.source.data or "").strip(),
            summary=(form.summary.data or "").strip(),
            price=(form.price.data or "").strip(),
            sentiment=(form.sentiment.data or "").strip(),
            action=form.action.data,
            content=(form.body.data or "").strip(),
        )
    )
    db.session.commit()

    flash("Новость добавлена", "success")
    return redirect(url_for("invest.index"))


@invest_bp.route("/Новости/<path:slug>")
def news(slug: str):
    page = load_news_page(slug)
    if page is None:
        abort(404)
    return render_template("potyk-invest/news.html", page=page)


def ticker_levels_map() -> dict[str, dict[str, str | None]]:
    rows = db.session.scalars(
        select(InvestTickerLevel).order_by(InvestTickerLevel.ticker.asc())
    ).all()
    result: dict[str, dict[str, str | None]] = {}
    for row in rows:
        result[row.ticker] = {
            "entry": price(row.entry_level) if row.entry_level is not None else None,
            "exit": price(row.exit_level) if row.exit_level is not None else None,
        }
    return result


def deals_context(
    *,
    deposit_form: DepositForm | None = None,
    deal_form: DealForm | None = None,
    edit_form: EditDealForm | None = None,
    edit_deal: InvestDeal | None = None,
    level_form: TickerLevelForm | None = None,
    close_form: CloseDealForm | None = None,
    close_deal: InvestDeal | None = None,
    delete_form: DealDeleteForm | None = None,
    open_panel: str | None = None,
) -> dict:
    deposit = current_deposit()
    ticker_choices = load_ticker_choices_from_db()
    changes = db.session.scalars(
        select(InvestDepositChange).order_by(
            InvestDepositChange.date.desc(),
            InvestDepositChange.id.desc(),
        )
    ).all()
    deals = db.session.scalars(
        select(InvestDeal).order_by(InvestDeal.opened_at.desc(), InvestDeal.id.desc())
    ).all()
    ticker_levels = db.session.scalars(
        select(InvestTickerLevel).order_by(InvestTickerLevel.ticker.asc())
    ).all()
    if deposit_form is None:
        deposit_form = DepositForm(data={"amount": deposit})
    return {
        "deposit": deposit,
        "deposit_changes": changes,
        "deals": deals,
        "ticker_levels": ticker_levels,
        "ticker_levels_json": ticker_levels_map(),
        "deposit_form": deposit_form,
        "deal_form": deal_form or DealForm(deposit=deposit, ticker_choices=ticker_choices),
        "edit_form": edit_form,
        "edit_deal": edit_deal,
        "level_form": level_form or TickerLevelForm(ticker_choices=ticker_choices),
        "close_form": close_form or CloseDealForm(),
        "close_deal": close_deal,
        "delete_form": delete_form or DealDeleteForm(),
        "open_panel": open_panel,
        "max_volume_pct": MAX_VOLUME_PCT,
        "deal_stats": deal_stats(deals),
    }


def deal_stats(deals: list[InvestDeal]) -> dict:
    closed = [deal for deal in deals if deal.is_closed]
    wins = sum(1 for deal in closed if deal.pnl is not None and deal.pnl > 0)
    losses = sum(1 for deal in closed if deal.pnl is not None and deal.pnl < 0)
    decided = wins + losses
    winrate = (wins / decided * 100) if decided else None
    return {
        "total": len(deals),
        "wins": wins,
        "losses": losses,
        "winrate": winrate,
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
    form = DealForm(deposit=deposit, ticker_choices=load_ticker_choices_from_db())
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_deals(deal_form=form, open_panel="deal"), 400

    db.session.add(
        InvestDeal(
            ticker=form.ticker.data.strip().upper(),
            opened_at=form.opened_at.data,
            volume=form.volume.data,
            buy_price=form.buy_price.data,
            qty=form.qty.data,
            entry_level=form.entry_level.data,
            exit_level=form.exit_level.data,
            take_profit_raw=form.take_profit_raw,
            take_profit_price=form.take_profit_price,
            stop_loss_raw=form.stop_loss_raw,
            stop_loss_price=form.stop_loss_price,
            thoughts=(form.thoughts.data or "").strip(),
        )
    )
    db.session.commit()
    flash("Сделка добавлена", "success")
    return redirect(url_for("invest.deals"))


@invest_bp.post("/deals/ticker-levels")
@login_required
def save_ticker_levels():
    ticker_choices = load_ticker_choices_from_db()
    form = TickerLevelForm(ticker_choices=ticker_choices)
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_deals(level_form=form, open_panel="levels"), 400

    ticker = form.ticker.data.strip().upper()
    row = db.session.scalars(
        select(InvestTickerLevel).where(InvestTickerLevel.ticker == ticker)
    ).first()
    if row is None:
        row = InvestTickerLevel(ticker=ticker)
        db.session.add(row)
    row.entry_level = form.entry_level.data
    row.exit_level = form.exit_level.data
    db.session.commit()
    flash("Уровни сохранены", "success")
    return redirect(url_for("invest.deals"))


@invest_bp.post("/deals/<int:deal_id>/close")
@login_required
def close_deal(deal_id: int):
    deal = db.session.get(InvestDeal, deal_id)
    if deal is None:
        flash("Сделка не найдена", "error")
        return redirect(url_for("invest.deals"))
    if deal.is_closed:
        flash("Сделка уже закрыта", "error")
        return redirect(url_for("invest.deals"))

    form = CloseDealForm()
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_deals(close_form=form, close_deal=deal, open_panel="close"), 400

    sell_price = form.sell_price.data
    deal.closed_at = form.closed_at.data
    deal.sell_price = sell_price
    deal.pnl = compute_pnl(Decimal(deal.qty), Decimal(deal.buy_price), Decimal(sell_price))
    deal.close_thoughts = (form.thoughts.data or "").strip()
    deal.close_errors = (form.mistakes.data or "").strip() if deal.pnl < 0 else ""
    db.session.commit()
    flash("Сделка закрыта", "success")
    return redirect(url_for("invest.deals"))


@invest_bp.route("/deals/<int:deal_id>/edit")
@login_required
def edit_deal_form(deal_id: int):
    deal = db.session.get(InvestDeal, deal_id)
    if deal is None:
        flash("Сделка не найдена", "error")
        return redirect(url_for("invest.deals"))

    deposit = current_deposit()
    form = EditDealForm(deposit=deposit, ticker_choices=load_ticker_choices_from_db())
    form.populate_from_deal(deal)
    return render_deals(edit_form=form, edit_deal=deal, open_panel="edit")


@invest_bp.post("/deals/<int:deal_id>/edit")
@login_required
def edit_deal(deal_id: int):
    deal = db.session.get(InvestDeal, deal_id)
    if deal is None:
        flash("Сделка не найдена", "error")
        return redirect(url_for("invest.deals"))

    deposit = current_deposit()
    form = EditDealForm(deposit=deposit, ticker_choices=load_ticker_choices_from_db())
    if not form.validate_on_submit():
        flash_form_errors(form)
        return render_deals(edit_form=form, edit_deal=deal, open_panel="edit"), 400

    deal.ticker = form.ticker.data.strip().upper()
    deal.opened_at = form.opened_at.data
    deal.volume = form.volume.data
    deal.buy_price = form.buy_price.data
    deal.qty = form.qty.data
    deal.entry_level = form.entry_level.data
    deal.exit_level = form.exit_level.data
    deal.take_profit_raw = form.take_profit_raw
    deal.take_profit_price = form.take_profit_price
    deal.stop_loss_raw = form.stop_loss_raw
    deal.stop_loss_price = form.stop_loss_price
    deal.thoughts = (form.thoughts.data or "").strip()

    if deal.is_closed and deal.sell_price is not None:
        deal.pnl = compute_pnl(
            Decimal(deal.qty),
            Decimal(deal.buy_price),
            Decimal(deal.sell_price),
        )
        if deal.pnl >= 0:
            deal.close_errors = ""

    db.session.commit()
    flash("Сделка обновлена", "success")
    return redirect(url_for("invest.deals"))


@invest_bp.post("/deals/<int:deal_id>/delete")
@login_required
def delete_deal(deal_id: int):
    form = DealDeleteForm()
    if not form.validate_on_submit():
        flash("Не удалось удалить сделку", "error")
        return redirect(url_for("invest.deals"))

    deal = db.session.get(InvestDeal, deal_id)
    if deal is None:
        flash("Сделка не найдена", "error")
        return redirect(url_for("invest.deals"))

    db.session.delete(deal)
    db.session.commit()
    flash("Сделка удалена", "success")
    return redirect(url_for("invest.deals"))
