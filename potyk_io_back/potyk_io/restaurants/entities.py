from sqlalchemy import select

from potyk_io_back.core.db import db

SEED_RESTAURANTS = [
    {
        "name": "Суп-кафе",
        "maps_url": "https://yandex.ru/maps/-/CPF~MEj8",
        "metro": "Белорусская",
        "tags": ["супчики"],
    },
    {
        "name": "She",
        "maps_url": "https://yandex.ru/maps/-/CPF~MEj8",
        "metro": "Белорусская",
        "tags": ["азия", "средиземноморская"],
    },
    {
        "name": "Torro",
        "maps_url": "https://yandex.ru/maps/-/CPF~M6OK",
        "metro": "Белорусская",
        "tags": ["мясо"],
    },
    {
        "name": "Boston",
        "maps_url": "https://yandex.ru/maps/-/CPF~MWnR",
        "metro": "Белорусская",
        "tags": ["креветки"],
    },
    {
        "name": "Steak it easy",
        "maps_url": "https://yandex.ru/maps/-/CPF~MDP8",
        "metro": "Белорусская",
        "tags": ["мясо"],
    },
    {
        "name": "The Бык",
        "maps_url": "https://yandex.ru/maps/-/CPF~QKiA",
        "metro": "Белорусская",
        "tags": ["мясо"],
    },
    {
        "name": "Ломи",
        "maps_url": "https://yandex.ru/maps/-/CPF~UAL2",
        "metro": "Белорусская",
        "tags": ["грузия"],
    },
    {
        "name": "Тхали и карри",
        "maps_url": "https://yandex.ru/maps/-/CPF~IA2Q",
        "metro": "Пушкинская / Тверская / Чеховская",
        "tags": ["индийка"],
    },
]


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    maps_url = db.Column(db.String(1024), nullable=False)
    metro = db.Column(db.String(128), nullable=False, default="", index=True)
    tags = db.Column(db.JSON, nullable=False, default=list)


def seed_restaurants_if_empty() -> None:
    if db.session.scalar(select(Restaurant.id).limit(1)) is not None:
        return
    for row in SEED_RESTAURANTS:
        db.session.add(Restaurant(**row))
    db.session.commit()


def restaurant_vocab() -> tuple[list[str], list[str]]:
    restaurants = db.session.scalars(select(Restaurant)).all()
    metros: set[str] = set()
    tags: set[str] = set()
    for r in restaurants:
        if r.metro:
            metros.add(r.metro)
        for tag in r.tags or []:
            if tag:
                tags.add(tag)
    return sorted(metros, key=str.casefold), sorted(tags, key=str.casefold)


def normalize_restaurant_tags(raw: list[str] | None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in raw or []:
        tag = (item or "").strip()
        if not tag:
            continue
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(tag)
    return result
