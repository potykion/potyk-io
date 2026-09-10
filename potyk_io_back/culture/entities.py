from datetime import date

from sqlalchemy import select

from potyk_io_back.core.db import db

SEED_VISITS = [
    {
        "title": "Ничего не бойся, я с тобой",
        "title_url": None,
        "kind": "Мюзикл",
        "author": None,
        "venue": "Мдм",
        "venue_url": None,
        "duration_hours": 3.0,
        "has_intermission": True,
        "visited_at": date(2026, 5, 14),
        "comment": None,
    },
    {
        "title": "Женитьба Бальзаминова",
        "title_url": None,
        "kind": "Спектакль",
        "author": "Островский",
        "venue": "Театр Комедии",
        "venue_url": "https://yandex.ru/maps/org/teatr_komedii/31217187029?si=potyk-io",
        "duration_hours": 2.0,
        "has_intermission": True,
        "visited_at": date(2026, 3, 28),
        "comment": "Простая комедия",
    },
    {
        "title": "Смерть комивояжера",
        "title_url": None,
        "kind": "Спектакль",
        "author": "Артур Миллер",
        "venue": "Воронежский Камерный театр",
        "venue_url": "https://yandex.ru/maps/org/voronezhskiy_kamerny_teatr/1312757484?si=potyk-io",
        "duration_hours": 3.0,
        "has_intermission": True,
        "visited_at": date(2026, 4, 18),
        "comment": None,
    },
    {
        "title": "Мама мимо",
        "title_url": None,
        "kind": "Мюзикл",
        "author": None,
        "venue": "Театр Маска",
        "venue_url": "https://yandex.ru/maps/-/CPgX4GIw",
        "duration_hours": 2.0,
        "has_intermission": False,
        "visited_at": date(2026, 3, 20),
        "comment": None,
    },
    {
        "title": "Машенька",
        "title_url": "https://mossoveta.ru/performance/Mashenka/",
        "kind": "Спектакль",
        "author": None,
        "venue": "Театр Моссовета",
        "venue_url": None,
        "duration_hours": 3.0,
        "has_intermission": True,
        "visited_at": date(2026, 7, 22),
        "comment": None,
    },
]


class CultureVisit(db.Model):
    __tablename__ = "culture_visits"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    title_url = db.Column(db.String(1024), nullable=True)
    kind = db.Column(db.String(64), nullable=False, index=True)
    author = db.Column(db.String(255), nullable=True)
    venue = db.Column(db.String(255), nullable=False)
    venue_url = db.Column(db.String(1024), nullable=True)
    duration_hours = db.Column(db.Float, nullable=False)
    has_intermission = db.Column(db.Boolean, nullable=False, default=False)
    visited_at = db.Column(db.Date, nullable=False, index=True)
    comment = db.Column(db.Text, nullable=True)


def seed_culture_visits_if_empty() -> None:
    if db.session.scalar(select(CultureVisit.id).limit(1)) is not None:
        return
    for row in SEED_VISITS:
        db.session.add(CultureVisit(**row))
    db.session.commit()
