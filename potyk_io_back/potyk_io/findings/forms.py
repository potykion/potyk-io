from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL

FINDING_KIND_CHOICES = [
    ("🎵", "🎵 — музончик: клипы, сеты и тд"),
    ("📹", "📹 — ютуб видик"),
    ("🎮", "🎮 — игрушки"),
    ("🎥", "🎥 — кинцо"),
    ("🖼️", "🖼️ — картинка"),
]


class AddFindingForm(FlaskForm):
    kind = SelectField(
        "Тип",
        choices=FINDING_KIND_CHOICES,
        default="📹",
        validators=[DataRequired()],
    )
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
    submit = SubmitField(
        "👁️",
        render_kw={"aria-label": "Просмотрено", "title": "Просмотрено"},
    )


class DeleteFindingForm(FlaskForm):
    submit = SubmitField("×")
