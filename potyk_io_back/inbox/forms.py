from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

PROJECT_CHOICES = [
    ("potyk-io", "potyk-io"),
    ("potyk-invest", "potyk-invest"),
    ("potyk-fin", "potyk-fin"),
    ("potyk-food", "potyk-food"),
    ("potyk-mu", "potyk-mu"),
    ("task-man", "task-man"),
]


class SendForm(FlaskForm):
    project = SelectField(
        "Проект",
        choices=PROJECT_CHOICES,
        default="potyk-io",
        validators=[DataRequired()],
    )
    text = TextAreaField(
        "Текст",
        validators=[DataRequired(message="Напиши текст"), Length(max=20_000)],
        render_kw={"rows": 8, "placeholder": "идея, баг, что починить…"},
    )
    submit = SubmitField("Отправить")


class PullForm(FlaskForm):
    secret = StringField(
        "Секрет прода",
        validators=[DataRequired(message="Нужен секрет прода")],
        render_kw={
            "type": "password",
            "placeholder": "секрет",
            "autocomplete": "off",
        },
    )
    submit = SubmitField("Выгрузить с прода")
