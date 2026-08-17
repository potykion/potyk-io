from datetime import date, timedelta

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Optional


def _yesterday() -> date:
    return date.today() - timedelta(days=1)


class ExpenseForm(FlaskForm):
    date = DateField("Дата", validators=[DataRequired()], default=_yesterday)
    amount = IntegerField(
        "Сумма",
        validators=[InputRequired(), NumberRange(min=1, message="Укажи положительную сумму")],
    )
    category = StringField(
        "Категория",
        validators=[DataRequired(message="Укажи категорию"), Length(max=64)],
    )
    description = StringField("Описание", validators=[Optional(), Length(max=255)], default="")
    optional = BooleanField("Необязательный расход")
    submit = SubmitField("Добавить трату")


class SavingForm(FlaskForm):
    amount = IntegerField(
        "Сумма",
        validators=[InputRequired(), NumberRange(min=1, message="Укажи положительную сумму")],
    )
    date = DateField("Дата", validators=[DataRequired()], default=date.today)
    note = StringField("Заметка", validators=[Optional(), Length(max=255)], default="")
    submit = SubmitField("Зафиксировать")


class BudgetForm(FlaskForm):
    daily_budget = IntegerField(
        "Новый бюджет (₽)",
        validators=[InputRequired(), NumberRange(min=1, message="Укажи положительный бюджет")],
    )
    submit = SubmitField("Сохранить")


class DeleteForm(FlaskForm):
    submit = SubmitField("✕")
