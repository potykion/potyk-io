from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

COVER_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "mp4",
    "webm",
    "mov",
    "m4v",
    "ogg",
    "ogv",
]


class NewPostForm(FlaskForm):
    title = StringField(
        "Название",
        validators=[
            DataRequired(message="Укажи название"),
            Length(max=200),
        ],
        render_kw={"placeholder": "Гора трупов", "autocomplete": "off"},
    )
    cover = FileField(
        "Обложка (картинка или видео)",
        validators=[
            FileRequired(message="Выбери файл"),
            FileAllowed(COVER_EXTENSIONS, message="Нужна картинка или видео"),
        ],
    )
    submit = SubmitField("Создать пост")


class CommitPushForm(FlaskForm):
    submit = SubmitField("Закоммитить и запушить")
