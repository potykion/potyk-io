from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from flask_wtf import FlaskForm
from wtforms import DateField, DateTimeField, DecimalField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional, ValidationError

MAX_VOLUME_PCT = Decimal("5")
QTY_QUANT = Decimal("0.000001")
MONEY_QUANT = Decimal("0.01")
PRICE_QUANT = Decimal("0.000001")

_PCT_RE = re.compile(r"^([+-]?\d+(?:\.\d+)?)\s*%$")
_OFFSET_RE = re.compile(r"^([+-]\d+(?:\.\d+)?)$")
_ABS_RE = re.compile(r"^(\d+(?:\.\d+)?)$")


def _normalize_number(raw: str) -> str:
    return raw.strip().replace(" ", "").replace(",", ".")


class CommaDecimalField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist = [_normalize_number(valuelist[0])]
        super().process_formdata(valuelist)


def parse_level(raw: str | None, buy_price: Decimal) -> Decimal | None:
    text = _normalize_number(raw or "")
    if not text:
        return None

    try:
        if match := _PCT_RE.match(text):
            pct = Decimal(match.group(1))
            price = buy_price * (Decimal(100) + pct) / Decimal(100)
        elif match := _OFFSET_RE.match(text):
            price = buy_price + Decimal(match.group(1))
        elif match := _ABS_RE.match(text):
            price = Decimal(match.group(1))
        else:
            raise ValueError
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(
            "Непонятный формат. Примеры: +10, -10, 10% или 150"
        ) from exc

    if price <= 0:
        raise ValueError("Цена должна быть больше нуля")
    return price.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)


def volume_money(deposit: Decimal, volume_pct: Decimal) -> Decimal:
    return (deposit * volume_pct / Decimal(100)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def compute_qty(deposit: Decimal, volume_pct: Decimal, buy_price: Decimal) -> Decimal:
    return (volume_money(deposit, volume_pct) / buy_price).quantize(
        QTY_QUANT, rounding=ROUND_HALF_UP
    )


def volume_pct_from_qty(deposit: Decimal, qty: Decimal, buy_price: Decimal) -> Decimal:
    money = (qty * buy_price).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    return (money / deposit * Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class DepositForm(FlaskForm):
    date = DateField("Дата", validators=[DataRequired()], default=date.today)
    amount = CommaDecimalField(
        "Сумма",
        places=2,
        rounding=ROUND_HALF_UP,
        validators=[InputRequired(), NumberRange(min=0, message="Укажи неотрицательную сумму")],
    )
    submit = SubmitField("Сохранить депозит")


class DealForm(FlaskForm):
    ticker = StringField(
        "Тикер",
        validators=[DataRequired(message="Укажи тикер"), Length(max=32)],
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
    )
    opened_at = DateTimeField(
        "Дата и время",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,
        validators=[DataRequired()],
        render_kw={"type": "datetime-local"},
    )
    volume = CommaDecimalField(
        "Объём, %",
        places=2,
        rounding=ROUND_HALF_UP,
        validators=[
            Optional(),
            NumberRange(min=0.01, max=5, message="Объём от 0.01% до 5% депозита"),
        ],
    )
    buy_price = CommaDecimalField(
        "Цена покупки",
        places=6,
        rounding=ROUND_HALF_UP,
        validators=[InputRequired(), NumberRange(min=0.000001, message="Укажи цену покупки")],
    )
    qty = CommaDecimalField(
        "Кол-во позиций",
        places=6,
        rounding=ROUND_HALF_UP,
        validators=[Optional(), NumberRange(min=0.000001, message="Укажи количество")],
    )
    entry_level = CommaDecimalField(
        "Уровень входа",
        places=6,
        rounding=ROUND_HALF_UP,
        validators=[Optional(), NumberRange(min=0)],
    )
    exit_level = CommaDecimalField(
        "Уровень выхода",
        places=6,
        rounding=ROUND_HALF_UP,
        validators=[Optional(), NumberRange(min=0)],
    )
    take_profit = StringField(
        "Тейк-профит",
        validators=[Optional(), Length(max=32)],
        description="+10, 10% или цена",
    )
    stop_loss = StringField(
        "Стоп-лосс",
        validators=[Optional(), Length(max=32)],
        description="-10, -5% или цена",
    )
    thoughts = TextAreaField("Причина входа", validators=[Optional()], default="")
    submit = SubmitField("Добавить сделку")

    def __init__(self, deposit: Decimal | None = None, **kwargs):
        super().__init__(**kwargs)
        self.deposit = deposit if deposit is not None else Decimal("0")
        self.take_profit_price: Decimal | None = None
        self.stop_loss_price: Decimal | None = None
        self.volume_amount: Decimal | None = None

    def validate_volume(self, field: CommaDecimalField) -> None:
        if field.data is None:
            return
        if self.deposit <= 0:
            raise ValidationError("Сначала укажи депозит")
        if field.data > MAX_VOLUME_PCT:
            raise ValidationError(f"Объём не больше {MAX_VOLUME_PCT}% депозита")

    def validate(self, extra_validators=None) -> bool:
        if not super().validate(extra_validators):
            return False

        if self.deposit <= 0:
            self.volume.errors.append("Сначала укажи депозит")
            return False

        if self.volume.data is None and self.qty.data is None:
            message = "Укажи объём или количество позиций"
            self.volume.errors.append(message)
            self.qty.errors.append(message)
            return False

        buy_price = Decimal(self.buy_price.data)
        if self.volume.data is None:
            pct = volume_pct_from_qty(self.deposit, Decimal(self.qty.data), buy_price)
            if pct > MAX_VOLUME_PCT:
                self.qty.errors.append(
                    f"Это больше {MAX_VOLUME_PCT}% депозита ({pct}%)"
                )
                return False
            self.volume.data = pct
        elif self.qty.data is None:
            self.qty.data = compute_qty(self.deposit, Decimal(self.volume.data), buy_price)

        volume_pct = Decimal(self.volume.data)
        self.volume_amount = volume_money(self.deposit, volume_pct)

        try:
            self.take_profit_price = parse_level(self.take_profit.data, buy_price)
        except ValueError as exc:
            self.take_profit.errors.append(str(exc))
            return False

        try:
            self.stop_loss_price = parse_level(self.stop_loss.data, buy_price)
        except ValueError as exc:
            self.stop_loss.errors.append(str(exc))
            return False

        return True


def compute_pnl(qty: Decimal, buy_price: Decimal, sell_price: Decimal) -> Decimal:
    return ((sell_price - buy_price) * qty).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


class CloseDealForm(FlaskForm):
    closed_at = DateTimeField(
        "Дата и время",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,
        validators=[DataRequired()],
        render_kw={"type": "datetime-local"},
    )
    sell_price = CommaDecimalField(
        "Цена продажи",
        places=6,
        rounding=ROUND_HALF_UP,
        validators=[InputRequired(), NumberRange(min=0.000001, message="Укажи цену продажи")],
    )
    thoughts = TextAreaField("Причина выхода", validators=[Optional()], default="")
    mistakes = TextAreaField("Ошибки", validators=[Optional()], default="")
    submit = SubmitField("Закрыть сделку")
