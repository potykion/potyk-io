"""Import movies from local watch_later collection.

Берём текущие фильмы из коллекции `movie_collections.id = watch_later` (массив `movie_ids`)
и:
  1) добавляем уникальный constraint на `movies.kinopoisk`
  2) вставляем фильмы в `movies`, используя `INSERT OR IGNORE` (игнор по уникальным ограничениям)
  3) выставляем `watch_later.movie_ids` в порядок с локалки (с дописыванием любых уже существующих id).
"""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


WATCH_LATER_ID = "watch_later"


# Снимок текущего состояния БД на локалке (source: instance/main.db)
IDS = ['7229988', '105813', '5073923', '7701', '78871', '590022', '8134', '7378605', '11979274', '7519616', '5106451', '7327911', '555', '493098', '6103378', '519', '7525290', '1395841', '7421341', '257376', '839954', '6012599', '362', '1198736', '35786', '57336', '26501', '63912', '5446941', '7088374', '2000102', '2868', '4455', '6175', '88190', '55830', '1053967', '2013', '51388', '18805', '4396438', '258687', '1219852', '1394680', '4807', '5932', '714248', '10646404', '1343318', '9691', '819101', '3547', '8366', '6137', '222209', '325549', '724982', '469214', '325465', '1112153', '1148990', '325598', '5106807', '77202', '1807', '495892', '1068448', '741214', '273302', '374718']

MOVIES = [{'id': '7229988', 'title_ru': 'Гадкая сестра', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7229988/'}, {'id': '105813', 'title_ru': 'Запределье', 'title_en': None, 'year': 2006, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/105813/'}, {'id': '5073923', 'title_ru': 'Непокой', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/5073923/'}, {'id': '7701', 'title_ru': 'Секс, ложь и видео', 'title_en': None, 'year': 1989, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7701/'}, {'id': '78871', 'title_ru': 'Сайлент Хилл', 'title_en': None, 'year': 2006, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/78871/'}, {'id': '590022', 'title_ru': 'Синистер', 'title_en': None, 'year': 2012, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/590022/'}, {'id': '8134', 'title_ru': 'Ведьма из Блэр: Курсовая с того света', 'title_en': None, 'year': 1999, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/8134/'}, {'id': '7378605', 'title_ru': 'Обитель зла', 'title_en': None, 'year': 2026, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7378605/'}, {'id': '11979274', 'title_ru': 'Паша Техник. За кем стоит андеграунд?', 'title_en': None, 'year': 2026, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/11979274/'}, {'id': '7519616', 'title_ru': 'Выход 8', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7519616/'}, {'id': '5106451', 'title_ru': 'Быть присяжным', 'title_en': None, 'year': 2023, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/5106451/'}, {'id': '7327911', 'title_ru': 'Фэкхем-Холл', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7327911/'}, {'id': '555', 'title_ru': 'Большой Лебовски', 'title_en': None, 'year': 1998, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/555/'}, {'id': '493098', 'title_ru': 'Школа', 'title_en': None, 'year': 2010, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/493098/'}, {'id': '6103378', 'title_ru': 'Сводишь с ума', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/6103378/'}, {'id': '519', 'title_ru': 'Человек дождя', 'title_en': None, 'year': 1988, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/519/'}, {'id': '7525290', 'title_ru': 'Двое в одной жизни, не считая собаки', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7525290/'}, {'id': '1395841', 'title_ru': 'Человек из Подольска', 'title_en': None, 'year': 2020, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1395841/'}, {'id': '7421341', 'title_ru': 'Коммерсант', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7421341/'}, {'id': '257376', 'title_ru': 'Берсерк', 'title_en': None, 'year': 1997, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/257376/'}, {'id': '839954', 'title_ru': 'Легенда', 'title_en': None, 'year': 2015, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/839954/'}, {'id': '6012599', 'title_ru': 'Одна из многих', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/6012599/'}, {'id': '362', 'title_ru': 'Подводная лодка', 'title_en': None, 'year': 1981, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/362/'}, {'id': '1198736', 'title_ru': 'Я иду искать', 'title_en': None, 'year': 2019, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1198736/'}, {'id': '35786', 'title_ru': 'Общество', 'title_en': None, 'year': 1989, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/35786/'}, {'id': '57336', 'title_ru': 'Счастье', 'title_en': None, 'year': 1965, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/57336/'}, {'id': '26501', 'title_ru': 'Мужское-женское', 'title_en': None, 'year': 1966, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/26501/'}, {'id': '63912', 'title_ru': 'Укрощение строптивого', 'title_en': None, 'year': 1980, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/63912/'}, {'id': '5446941', 'title_ru': 'Материалистка', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/5446941/'}, {'id': '7088374', 'title_ru': 'Одно целое', 'title_en': None, 'year': 2025, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/7088374/'}, {'id': '2000102', 'title_ru': 'Киберпанк: Бегущие по краю', 'title_en': None, 'year': 2022, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/2000102/'}, {'id': '2868', 'title_ru': 'Эйс Вентура: Розыск домашних животных', 'title_en': None, 'year': 1993, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/2868/'}, {'id': '4455', 'title_ru': 'Аптечный ковбой', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/4455/'}, {'id': '6175', 'title_ru': 'Дневник баскетболиста', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/6175/'}, {'id': '88190', 'title_ru': 'Кэнди', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/88190/'}, {'id': '55830', 'title_ru': 'Я Кристина', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/55830/'}, {'id': '1053967', 'title_ru': 'Рейв', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1053967/'}, {'id': '2013', 'title_ru': 'Экстази', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/2013/'}, {'id': '51388', 'title_ru': 'В отрыв', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/51388/'}, {'id': '18805', 'title_ru': 'Кислотный дом', 'title_en': None, 'year': None, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/18805/'}, {'id': '4396438', 'title_ru': 'Бедные-несчастные', 'title_en': None, 'year': 2023, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/4396438/'}, {'id': '258687', 'title_ru': 'Интерстеллар', 'title_en': None, 'year': 2014, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/258687/'}, {'id': '1219852', 'title_ru': 'Думаю, как всё закончить', 'title_en': None, 'year': 2020, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1219852/'}, {'id': '1394680', 'title_ru': 'Сцены из супружеской жизни', 'title_en': None, 'year': 2021, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1394680/'}, {'id': '4807', 'title_ru': 'Не грози Южному Централу, попивая сок у себя в квартале', 'title_en': None, 'year': 1995, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/4807/'}, {'id': '5932', 'title_ru': 'Очень страшное кино', 'title_en': None, 'year': 2000, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/5932/'}, {'id': '714248', 'title_ru': 'Песнь моря', 'title_en': None, 'year': 2014, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/714248/'}, {'id': '10646404', 'title_ru': 'Рустер', 'title_en': None, 'year': 2026, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/10646404/'}, {'id': '1343318', 'title_ru': 'Разделение', 'title_en': None, 'year': 2022, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1343318/'}, {'id': '9691', 'title_ru': 'Бесславные ублюдки', 'title_en': None, 'year': 2009, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/9691/'}, {'id': '819101', 'title_ru': 'Омерзительная восьмерка', 'title_en': None, 'year': 2015, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/819101/'}, {'id': '3547', 'title_ru': 'Факультет', 'title_en': None, 'year': 1998, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/3547/'}, {'id': '8366', 'title_ru': 'Нечто', 'title_en': None, 'year': 1982, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/8366/'}, {'id': '6137', 'title_ru': 'Любовный напиток № 9', 'title_en': None, 'year': 1992, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/6137/'}, {'id': '222209', 'title_ru': 'Маша', 'title_en': None, 'year': 2004, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/222209/'}, {'id': '325549', 'title_ru': 'Беззаботная', 'title_en': None, 'year': 2008, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/325549/'}, {'id': '724982', 'title_ru': 'Звезда', 'title_en': None, 'year': 2014, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/724982/'}, {'id': '469214', 'title_ru': 'Будь со мной', 'title_en': None, 'year': 2009, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/469214/'}, {'id': '325465', 'title_ru': 'Жестокость', 'title_en': None, 'year': 2007, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/325465/'}, {'id': '1112153', 'title_ru': 'Психиатрическая больница Конджиам', 'title_en': None, 'year': 2018, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1112153/'}, {'id': '1148990', 'title_ru': 'Глотай', 'title_en': None, 'year': 2019, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1148990/'}, {'id': '325598', 'title_ru': 'Репортаж', 'title_en': None, 'year': 2007, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/325598/'}, {'id': '5106807', 'title_ru': 'Ложка сахара', 'title_en': None, 'year': 2022, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/5106807/'}, {'id': '77202', 'title_ru': 'Место встречи изменить нельзя', 'title_en': None, 'year': 1979, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/77202/'}, {'id': '1807', 'title_ru': 'Крик', 'title_en': 'Scream', 'year': 1996, 'cover': '/static/potyk-io/img/movies/scream.jpg', 'kinopoisk': 'https://www.kinopoisk.ru/film/1807/'}, {'id': '495892', 'title_ru': 'Астрал', 'title_en': None, 'year': 2010, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/495892/'}, {'id': '1068448', 'title_ru': 'Оцепеневшие от страха', 'title_en': None, 'year': 2018, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/1068448/'}, {'id': '741214', 'title_ru': 'Птичий короб', 'title_en': None, 'year': 2018, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/741214/'}, {'id': '273302', 'title_ru': 'Мгла', 'title_en': None, 'year': 2007, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/273302/'}, {'id': '374718', 'title_ru': 'Монстро', 'title_en': None, 'year': 2007, 'cover': None, 'kinopoisk': 'https://www.kinopoisk.ru/film/374718/'}]


KINOPOSK_UNIQ_INDEX = "ix_movies_kinopoisk_unique"


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # 1) unique по kinopoisk
    existing_indexes = {idx["name"] for idx in insp.get_indexes("movies")}
    if KINOPOSK_UNIQ_INDEX not in existing_indexes:
        op.create_index(KINOPOSK_UNIQ_INDEX, "movies", ["kinopoisk"], unique=True)

    # 2) вставляем фильмы (игнорируем если уже есть по уникальному kinopoisk)
    for m in MOVIES:
        bind.execute(
            sa.text(
                """
                INSERT OR IGNORE INTO movies (id, title_ru, title_en, year, cover, kinopoisk)
                VALUES (:id, :title_ru, :title_en, :year, :cover, :kinopoisk)
                """
            ),
            {
                "id": m["id"],
                "title_ru": m["title_ru"],
                "title_en": m["title_en"],
                "year": m["year"],
                "cover": m["cover"],
                "kinopoisk": m["kinopoisk"],
            },
        )

    # 3) выставляем watch_later.movie_ids в порядок локалки + добавляем всё что уже было
    row = bind.execute(
        sa.text("SELECT movie_ids FROM movie_collections WHERE id = :cid"),
        {"cid": WATCH_LATER_ID},
    ).fetchone()

    existing_ids: list[str] = []
    if row is not None:
        raw = row[0]
        if isinstance(raw, str):
            existing_ids = json.loads(raw) if raw else []
        elif raw is None:
            existing_ids = []
        else:
            existing_ids = list(raw)

    local_set = set(IDS)
    updated_ids = [mid for mid in IDS if mid] + [mid for mid in existing_ids if mid not in local_set]

    if row is None:
        bind.execute(
            sa.text(
                """
                INSERT INTO movie_collections (id, title, quote, youtube, movie_ids, watch_later, sort_order)
                VALUES (:id, :title, :quote, :youtube, :movie_ids, 1, 0)
                """
            ),
            {
                "id": WATCH_LATER_ID,
                "title": "Посмотреть позже",
                "quote": None,
                "youtube": None,
                "movie_ids": json.dumps(updated_ids, ensure_ascii=False),
            },
        )
    else:
        bind.execute(
            sa.text(
                "UPDATE movie_collections SET movie_ids = :movie_ids, watch_later = 1, sort_order = 0 WHERE id = :cid"
            ),
            {"movie_ids": json.dumps(updated_ids, ensure_ascii=False), "cid": WATCH_LATER_ID},
        )


def downgrade() -> None:
    # Оставляем данные, но убираем unique index.
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_indexes = {idx["name"] for idx in insp.get_indexes("movies")}
    if KINOPOSK_UNIQ_INDEX in existing_indexes:
        op.drop_index(KINOPOSK_UNIQ_INDEX, table_name="movies")

