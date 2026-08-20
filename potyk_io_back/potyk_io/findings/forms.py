from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL


class AddFindingForm(FlaskForm):
    url = StringField(
        "Ссылка",
        validators=[
            DataRequired(message="Нужна ссылка"),
            URL(message="Это не похоже на URL"),
            Length(max=1024),
        ],
        render_kw={"placeholder": "https://youtu.be/…", "autocomplete": "off"},
    )
    submit = SubmitField("Добавить")


class MarkWatchedForm(FlaskForm):
    submit = SubmitField("Просмотрено")


class DeleteFindingForm(FlaskForm):
    submit = SubmitField("×")
