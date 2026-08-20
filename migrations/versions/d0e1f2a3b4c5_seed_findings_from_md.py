"""Seed findings from findings.md archive (nostalgia + weekly links).

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-08-20 15:30:00.000000

"""
from __future__ import annotations

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, Sequence[str], None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (url, title, created_at, watched_at) — спарсено из findings.md
# «Кушаем ностальгию» → очередь (watched_at=None);
# недельные секции → просмотрено с датой конца недели.
# Только http(s); дубликаты URL опущены; картинки и relative (code/ai) не трогаем.
SEED: list[tuple[str, str, datetime, datetime | None]] = [
    # Кушаем ностальгию 😋
    (
        "https://www.youtube.com/watch?v=XI0JU_1yLzk",
        "📹 КОНЕЦ КЛИПОВ: как в России погибла целая индустрия",
        datetime(2026, 8, 6, 12, 0, 0),
        None,
    ),
    (
        "https://www.youtube.com/watch?v=E7caDC4CzZg",
        '📹 Когда "ДАЁШЬ МОЛОДЁЖЬ" точнее учебников истории',
        datetime(2026, 8, 6, 11, 59, 59),
        None,
    ),
    (
        "https://www.youtube.com/watch?v=vg_aG0TbFxg",
        "📹 Глубокий лор «Аншлага»",
        datetime(2026, 8, 6, 11, 59, 58),
        None,
    ),
    (
        "https://www.youtube.com/watch?v=HKXMv5_wVoI",
        "📹 Провал российских кинопародий 00-х",
        datetime(2026, 8, 6, 11, 59, 57),
        None,
    ),
    (
        "https://www.youtube.com/watch?v=OSiwDWyEiK8",
        "📹 Глубокий лор «Что? Где? Когда?» Часть 1",
        datetime(2026, 8, 6, 11, 59, 56),
        None,
    ),
    (
        "https://youtu.be/FwKNv6xz16c?si=3kJTE64p-8vQJEw3",
        "📹 Глубокий лор «Что? Где? Когда?» Часть 2",
        datetime(2026, 8, 6, 11, 59, 55),
        None,
    ),
    (
        "https://music.yandex.ru/album/26382063?utm_source=desktop&utm_medium=copy_link",
        "🗣️ Подкаст Продактка",
        datetime(2026, 8, 6, 11, 59, 54),
        None,
    ),
    # 2026-08-03 — 2026-08-09
    (
        "https://www.youtube.com/watch?v=vhzLh84iElg",
        "🎵 SLAM BAND - PEEWEE JERKIN (Featuring Filth, Official Video)",
        datetime(2026, 8, 9, 12, 0, 0),
        datetime(2026, 8, 9, 12, 0, 0),
    ),
    (
        "https://www.youtube.com/watch?v=xWiqNVJsYTw",
        "📹 Убежище Кунякина — нейросети из советских мультиков",
        datetime(2026, 8, 9, 11, 59, 59),
        datetime(2026, 8, 9, 11, 59, 59),
    ),
    (
        "https://www.youtube.com/watch?v=lhRR76v9ang",
        "📹 Олег Кармунин — БЫТЬ НЕФОРОМ. Флекс и нищета русских субкультур",
        datetime(2026, 8, 9, 11, 59, 58),
        datetime(2026, 8, 9, 11, 59, 58),
    ),
    (
        "https://arbuzfest.ru",
        "🥳 Камышинский Арбузный фестиваль",
        datetime(2026, 8, 9, 11, 59, 57),
        datetime(2026, 8, 9, 11, 59, 57),
    ),
    # 2026-07-27 — 2026-08-02
    (
        "https://www.youtube.com/watch?v=xHPML_WkGmY",
        "📹 диаболик — БРАУЗЕРНЫЕ ИГРЫ....",
        datetime(2026, 8, 2, 12, 0, 0),
        datetime(2026, 8, 2, 12, 0, 0),
    ),
    (
        "https://www.youtube.com/watch?v=udv3BoxLSjw",
        "📹 Олег Кармунин — Вселенная раннего Сергея Минаева",
        datetime(2026, 8, 2, 11, 59, 59),
        datetime(2026, 8, 2, 11, 59, 59),
    ),
    (
        "https://www.youtube.com/watch?v=Xop-22b9XPI",
        "📹 Олег Кармунин — Артемий Лебедев, которого мы потеряли",
        datetime(2026, 8, 2, 11, 59, 58),
        datetime(2026, 8, 2, 11, 59, 58),
    ),
    (
        "https://www.youtube.com/shorts/xS3KC0QTotE",
        "📹 Was Jim Carrey Right About Napalm Death?",
        datetime(2026, 8, 2, 11, 59, 57),
        datetime(2026, 8, 2, 11, 59, 57),
    ),
    # 2026-07-20 — 2026-07-26
    (
        "https://www.youtube.com/watch?v=JMkzw_Xmst8",
        "📹 jpegviolence — гаспар ноэ: режиссер твоих кошмаров",
        datetime(2026, 7, 26, 12, 0, 0),
        datetime(2026, 7, 26, 12, 0, 0),
    ),
    (
        "https://youtu.be/NNhKO7DBQfs?si=QUIGp9fSy19oGJXL",
        "📹 Хулиномика — Китайский ИИ рвёт амеров, КРАХ Мосбиржи, динозавр на аукционе",
        datetime(2026, 7, 26, 11, 59, 59),
        datetime(2026, 7, 26, 11, 59, 59),
    ),
    # 2026-07-13 — 2026-07-19
    (
        "https://youtu.be/9j-bqxhCLJk?si=34oMUMaVIeHDpAh4",
        "🎵 Viper - Money Is As Addicted To Me As I Am To Tha Rap Game",
        datetime(2026, 7, 19, 12, 0, 0),
        datetime(2026, 7, 19, 12, 0, 0),
    ),
    (
        "https://youtu.be/A6dg28hpbKU?si=0HIRDIRwSzRRSQkJ",
        "🎵 Viper - I Sell A1 Cocaine",
        datetime(2026, 7, 19, 11, 59, 59),
        datetime(2026, 7, 19, 11, 59, 59),
    ),
    (
        "https://www.youtube.com/watch?v=JL2oOVe33fQ",
        "📹 Олег Кармунин — Крах ТРАХТЕНБЕРГА. Как уничтожить свою карьеру",
        datetime(2026, 7, 19, 11, 59, 58),
        datetime(2026, 7, 19, 11, 59, 58),
    ),
    (
        "https://www.youtube.com/watch?v=_ucBXSSNEj8",
        "📹 Новый видик от танакабосс",
        datetime(2026, 7, 19, 11, 59, 57),
        datetime(2026, 7, 19, 11, 59, 57),
    ),
    (
        "https://www.youtube.com/watch?v=mhe8gxHkuoI",
        '📹 Бимбо-обзор на "Технологическую республику" от CEO Palantir',
        datetime(2026, 7, 19, 11, 59, 56),
        datetime(2026, 7, 19, 11, 59, 56),
    ),
    (
        "https://www.youtube.com/watch?v=FjEcJ3hIaik",
        "Кисунь, дата-центры нас уничтожат(",
        datetime(2026, 7, 19, 11, 59, 55),
        datetime(2026, 7, 19, 11, 59, 55),
    ),
    (
        "https://youtu.be/e81LZCHhNKQ?si=WKFXpxMofA3L4oJl",
        "🎵 Napalm Death: Tiny Desk Concert",
        datetime(2026, 7, 19, 11, 59, 54),
        datetime(2026, 7, 19, 11, 59, 54),
    ),
    (
        "https://store.steampowered.com/app/2527160/Desktop_Explorer/",
        "🎮 Desktop Explorer",
        datetime(2026, 7, 19, 11, 59, 53),
        datetime(2026, 7, 19, 11, 59, 53),
    ),
    (
        "https://youtu.be/yWYgvXV18VA?si=jEDEmH3R4cAkAdE8",
        "🎮 Uncanny Cat Golf RELEASE TRAILER",
        datetime(2026, 7, 19, 11, 59, 52),
        datetime(2026, 7, 19, 11, 59, 52),
    ),
    (
        "https://www.youtube.com/watch?v=TJ_-Q1tE--I&t=235s",
        "🎮 The First Ever Sub 10 Claw% Speedrun",
        datetime(2026, 7, 19, 11, 59, 51),
        datetime(2026, 7, 19, 11, 59, 51),
    ),
    # 2026-07-06 - 2026-07-12
    (
        "https://www.youtube.com/watch?v=r8PHsRhESr4",
        '🎵 Dying Fetus "From Womb To Waste" | FishCenter | Adult Swim',
        datetime(2026, 7, 12, 12, 0, 0),
        datetime(2026, 7, 12, 12, 0, 0),
    ),
    (
        "https://www.youtube.com/watch?v=qk3YtXIEFrw",
        "🎵 Мэшап-сет с Абстрактного Фестиваля 2026 | kanash",
        datetime(2026, 7, 12, 11, 59, 59),
        datetime(2026, 7, 12, 11, 59, 59),
    ),
    (
        "https://music.yandex.ru/album/39946538/track/146645672",
        "🎵 УННВ — RAP 2026",
        datetime(2026, 7, 12, 11, 59, 58),
        datetime(2026, 7, 12, 11, 59, 58),
    ),
    (
        "https://www.youtube.com/watch?v=FMwK7x1D6kI",
        "📹 Disco Elysium — Дневник русской озвучки №1",
        datetime(2026, 7, 12, 11, 59, 57),
        datetime(2026, 7, 12, 11, 59, 57),
    ),
    # 2026-06-29 - 2026-07-05
    (
        "https://www.kinopoisk.ru/film/278156/",
        "🎥 Русалка (2007)",
        datetime(2026, 7, 5, 12, 0, 0),
        datetime(2026, 7, 5, 12, 0, 0),
    ),
    (
        "https://m.youtube.com/watch?v=PRJnv60SP00",
        "📹 kriper2004 и Влад Кунякин | Первый подкаст",
        datetime(2026, 7, 5, 11, 59, 59),
        datetime(2026, 7, 5, 11, 59, 59),
    ),
    (
        "https://youtu.be/YsvxDukEJF4",
        "📹 pen_pal — Жизнь вне стриминговых сервисов",
        datetime(2026, 7, 5, 11, 59, 58),
        datetime(2026, 7, 5, 11, 59, 58),
    ),
    # 2026-06-11
    (
        "https://www.youtube.com/watch?v=a3iGY7BoUvY",
        "🎵 мс улыбочка - бретелька (music video)",
        datetime(2026, 6, 11, 12, 0, 0),
        datetime(2026, 6, 11, 12, 0, 0),
    ),
]


def upgrade() -> None:
    findings = sa.table(
        "findings",
        sa.column("url", sa.String),
        sa.column("title", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("watched_at", sa.DateTime),
    )
    conn = op.get_bind()
    for url, title, created_at, watched_at in SEED:
        exists = conn.execute(
            sa.select(findings.c.url).where(findings.c.url == url)
        ).scalar()
        if exists:
            continue
        conn.execute(
            sa.insert(findings).values(
                url=url,
                title=title[:512],
                created_at=created_at,
                watched_at=watched_at,
            )
        )


def downgrade() -> None:
    findings = sa.table("findings", sa.column("url", sa.String))
    urls = [url for url, *_ in SEED]
    if urls:
        op.execute(sa.delete(findings).where(findings.c.url.in_(urls)))
