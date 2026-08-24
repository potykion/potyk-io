from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL


class RestaurantForm(FlaskForm):
    name = StringField(
        "Название",
        validators=[DataRequired(message="Укажи название"), Length(max=255)],
    )
    maps_url = StringField(
        "Яндекс.Карты",
        validators=[
            DataRequired(message="Нужна ссылка на карту"),
            URL(message="Это не похоже на URL"),
            Length(max=1024),
        ],
        render_kw={"placeholder": "https://yandex.ru/maps/-/…", "autocomplete": "off"},
    )
    metro = SelectField(
        "Метро",
        choices=[],
        validators=[Optional()],
        validate_choice=False,
    )
    tags = SelectMultipleField(
        "Теги",
        choices=[],
        validators=[Optional()],
        validate_choice=False,
    )
    submit = SubmitField("Добавить")
