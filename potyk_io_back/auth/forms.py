import os

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import AnyOf, DataRequired


class LoginForm(FlaskForm):
    secret = StringField(
        "Секрет",
        validators=[
            DataRequired(),
            AnyOf([os.environ["FLASK_SECRET"]], message="неверный секрет"),
        ],
        render_kw={
            "required": True,
            "placeholder": "секрет",
            "autocomplete": "current-password",
        },
    )
    submit = SubmitField("Войти")
