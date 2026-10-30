from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class AntiPostForm(FlaskForm):
    body = TextAreaField(
        "Текст",
        validators=[
            DataRequired(message="Напиши что-нибудь"),
            Length(max=4000),
        ],
        render_kw={
            "rows": 5,
            "placeholder": "Что происходит?",
            "required": True,
            "maxlength": 4000,
        },
    )
    submit = SubmitField("Запостить")
