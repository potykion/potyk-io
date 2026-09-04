from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from flask_wtf import FlaskForm
from wtforms import DateField, DateTimeField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional, ValidationError

MAX_VOLUME_PCT = Decimal("5")
QTY_QUANT = Decimal("0.000001")
MONEY_QUANT = Decimal("0.01")
PRICE_QUANT = Decimal("0.000001")

_PCT_RE = re.compile(r"^([+-]?\d+(?:\.\d+)?)\s*%$")
_OFFSET_RE = re.compile(r"^([+-]\d+(?:\.\d+)?)$")
_ABS_RE = re.compile(r"^(\d+(?:\.\d+)?)$")

LEVEL_UNIT_CHOICES = [
    ("", "—"),
    ("pct", "%"),
    ("price", "₽"),
]


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


def encode_level(value: str | None, unit: str | None, *, is_stop: bool) -> str:
    val_text = _normalize_number(value or "")
    unit = (unit or "").strip()
    if not val_text and not unit:
        return ""
    if val_text and not unit:
        raise ValueError("Выбери единицу: % или ₽")
    if unit and not val_text:
        raise ValueError("Укажи значение")

    try:
        n = Decimal(val_text)
    except InvalidOperation as exc:
        raise ValueError("Укажи число") from exc

    if unit == "pct":
        n = -abs(n) if is_stop else abs(n)
        return f"{n}%"
    if unit == "price":
        if n <= 0:
            raise ValueError("Цена должна быть больше нуля")
        return val_text
    raise ValueError("Выбери единицу: % или ₽")


def decode_level(raw: str | None) -> tuple[str, str]:
    text = _normalize_number(raw or "")
    if not text:
        return ("", "")
    if match := _PCT_RE.match(text):
        pct = Decimal(match.group(1))
        return (str(abs(pct)), "pct")
    if match := _OFFSET_RE.match(text):
        offset = Decimal(match.group(1))
        return (str(abs(offset)), "rub")
    if match := _ABS_RE.match(text):
        return (match.group(1), "price")
    return ("", "")


def _format_price_value(value) -> str:
    text = format(Decimal(value).normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def level_from_fields(
    value: str | None,
    unit: str | None,
    buy_price: Decimal,
    *,
    is_stop: bool,
) -> tuple[str, Decimal | None]:
    raw = encode_level(value, unit, is_stop=is_stop)
    if not raw:
        return ("", None)
    return raw, parse_level(raw, buy_price)


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
    ticker = SelectField(
        "Тикер",
        validators=[DataRequired(message="Укажи тикер"), Length(max=32)],
        filters=[lambda value: value.strip() if isinstance(value, str) else value],
        validate_choice=False,
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
    take_profit_value = StringField(
        "Тейк-профит",
        validators=[Optional(), Length(max=16)],
    )
    take_profit_unit = SelectField(
        "Ед.",
        choices=LEVEL_UNIT_CHOICES,
        validators=[Optional()],
        default="",
    )
    stop_loss_value = StringField(
        "Стоп-лосс",
        validators=[Optional(), Length(max=16)],
    )
    stop_loss_unit = SelectField(
        "Ед.",
        choices=LEVEL_UNIT_CHOICES,
        validators=[Optional()],
        default="",
    )
    thoughts = TextAreaField("Причина входа", validators=[Optional()], default="")
    submit = SubmitField("Добавить сделку")

    def __init__(
        self,
        deposit: Decimal | None = None,
        ticker_choices: list[tuple[str, str]] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.deposit = deposit if deposit is not None else Decimal("0")
        self.ticker.choices = [("", "")] + (ticker_choices or [])
        self.take_profit_raw: str = ""
        self.take_profit_price: Decimal | None = None
        self.stop_loss_raw: str = ""
        self.stop_loss_price: Decimal | None = None
        self.volume_amount: Decimal | None = None

    def populate_from_deal(self, deal) -> None:
        self.ticker.data = deal.ticker
        self.opened_at.data = deal.opened_at
        self.volume.data = deal.volume
        self.buy_price.data = deal.buy_price
        self.qty.data = deal.qty
        self.entry_level.data = deal.entry_level
        self.exit_level.data = deal.exit_level
        tp_value, tp_unit = decode_level(deal.take_profit_raw)
        if tp_unit == "rub":
            if deal.take_profit_price is not None:
                tp_value = _format_price_value(deal.take_profit_price)
                tp_unit = "price"
            else:
                tp_value, tp_unit = "", ""
        self.take_profit_value.data = tp_value
        self.take_profit_unit.data = tp_unit
        sl_value, sl_unit = decode_level(deal.stop_loss_raw)
        if sl_unit == "rub":
            if deal.stop_loss_price is not None:
                sl_value = _format_price_value(deal.stop_loss_price)
                sl_unit = "price"
            else:
                sl_value, sl_unit = "", ""
        self.stop_loss_value.data = sl_value
        self.stop_loss_unit.data = sl_unit
        self.thoughts.data = deal.thoughts

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
            self.take_profit_raw, self.take_profit_price = level_from_fields(
                self.take_profit_value.data,
                self.take_profit_unit.data,
                buy_price,
                is_stop=False,
            )
        except ValueError as exc:
            self.take_profit_value.errors.append(str(exc))
            return False

        try:
            self.stop_loss_raw, self.stop_loss_price = level_from_fields(
                self.stop_loss_value.data,
                self.stop_loss_unit.data,
                buy_price,
                is_stop=True,
            )
        except ValueError as exc:
            self.stop_loss_value.errors.append(str(exc))
            return False

        return True


class EditDealForm(DealForm):
    submit = SubmitField("Сохранить изменения")


class DealDeleteForm(FlaskForm):
    submit = SubmitField("×")


class ApplyDealBalanceForm(FlaskForm):
    submit = SubmitField("🔄")


def compute_pnl(qty: Decimal, buy_price: Decimal, sell_price: Decimal) -> Decimal:
    return ((sell_price - buy_price) * qty).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


class TickerLevelForm(FlaskForm):
    ticker = SelectField(
        "Тикер",
        validators=[DataRequired(message="Укажи тикер"), Length(max=32)],
        filters=[lambda value: value.strip().upper() if isinstance(value, str) else value],
        validate_choice=False,
    )
    entry_level = CommaDecimalField(
        "Поддержка",
        places=6,
        rounding=ROUND_HALF_UP,
        validators=[Optional(), NumberRange(min=0)],
    )
    exit_level = CommaDecimalField(
        "Сопротивление",
        places=6,
        rounding=ROUND_HALF_UP,
        validators=[Optional(), NumberRange(min=0)],
    )
    submit = SubmitField("Сохранить уровни")

    def __init__(self, ticker_choices: list[tuple[str, str]] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.ticker.choices = [("", "")] + (ticker_choices or [])

    def validate(self, extra_validators=None) -> bool:
        if not super().validate(extra_validators):
            return False
        if self.entry_level.data is None and self.exit_level.data is None:
            message = "Укажи хотя бы один уровень"
            self.entry_level.errors.append(message)
            self.exit_level.errors.append(message)
            return False
        return True


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


class NewsFilterForm(FlaskForm):
    class Meta:
        csrf = False

    date_from = DateField(
        "С",
        format="%Y-%m-%d",
        validators=[Optional()],
        render_kw={"type": "date"},
    )
    date_to = DateField(
        "По",
        format="%Y-%m-%d",
        validators=[Optional()],
        render_kw={"type": "date"},
    )
    sentiment = SelectField(
        "Сентимент",
        choices=[
            ("", "Все"),
            ("🟢", "🟢 Позитив"),
            ("🟡", "🟡 Нейтрально"),
            ("🔴", "🔴 Негатив"),
        ],
        validators=[Optional()],
        default="",
    )
    ticker = SelectField(
        "Тикер",
        validators=[Optional()],
        validate_choice=False,
        default="",
    )
    sector = SelectField(
        "Сектор",
        validators=[Optional()],
        validate_choice=False,
        default="",
    )
    submit = SubmitField("Применить")

    def __init__(
        self,
        formdata=None,
        *args,
        ticker_choices: list[tuple[str, str]] | None = None,
        sector_choices: list[tuple[str, str]] | None = None,
        **kwargs,
    ):
        super().__init__(formdata, *args, **kwargs)
        self.ticker.choices = [("", "Все")] + (ticker_choices or [])
        self.sector.choices = [("", "Все")] + (sector_choices or [])


class NewsForm(FlaskForm):
    datetime = DateTimeField(
        "Дата и время",
        format="%Y-%m-%dT%H:%M",
        # Чтоб в input[type=datetime-local] всегда было значение.
        default=datetime.now,
        validators=[DataRequired()],
        render_kw={"type": "datetime-local"},
    )

    ticker = SelectField(
        "Тикер",
        validators=[DataRequired(message="Укажи тикер"), Length(max=64)],
        filters=[lambda value: value.strip().upper() if isinstance(value, str) else value],
        validate_choice=False,
    )

    source = SelectField(
        "Источник",
        validators=[Optional(), Length(max=255)],
        validate_choice=False,
    )

    summary = TextAreaField(
        "Коротко",
        validators=[InputRequired(), Length(max=2000)],
    )

    price = StringField(
        "Цена",
        validators=[Optional(), Length(max=64)],
        description="Можно оставить пустым",
    )

    sentiment = SelectField(
        "Сентимент",
        choices=[
            ("", "—"),
            ("🟢", "🟢 Позитив"),
            ("🟡", "🟡 Нейтрально"),
            ("🔴", "🔴 Негатив"),
        ],
        validators=[Optional()],
    )

    action = SelectField(
        "Действие",
        choices=[
            ("Покупать", "Покупать"),
            ("держать", "держать"),
            ("наблюдать", "наблюдать"),
            ("продавать", "продавать"),
        ],
        validators=[DataRequired()],
        default="наблюдать",
    )

    body = TextAreaField(
        "Текст новости (markdown)",
        validators=[Optional()],
        default="",
    )

    submit = SubmitField("Добавить")

    def __init__(
        self,
        ticker_choices: list[tuple[str, str]] | None = None,
        source_choices: list[tuple[str, str]] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.ticker.choices = [("", "")] + (ticker_choices or [])
        self.source.choices = [("", "")] + (source_choices or [])
