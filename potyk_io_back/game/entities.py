from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Mapped

from potyk_io_back.core.db import db

MSK = ZoneInfo("Europe/Moscow")
MAX_HP = 3

MEAL_TYPES: dict[str, str] = {
    "breakfast": "завтрак",
    "lunch": "обед",
    "snack": "перекус",
    "dinner": "ужин",
}

game_meal_foods = db.Table(
    "game_meal_foods",
    db.Column("meal_id", db.Integer, db.ForeignKey("game_meals.id"), primary_key=True),
    db.Column("food_id", db.Integer, db.ForeignKey("game_foods.id"), primary_key=True),
)


class GameState(db.Model):
    __tablename__ = "game_state"

    id = db.Column(db.Integer, primary_key=True)
    hp = db.Column(db.Integer, nullable=False, default=0)
    game_day = db.Column(db.Date, nullable=False)


class GameFood(db.Model):
    __tablename__ = "game_foods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)


class GameMeal(db.Model):
    __tablename__ = "game_meals"

    id = db.Column(db.Integer, primary_key=True)
    eaten_at = db.Column(db.DateTime, nullable=False, index=True)
    meal_type = db.Column(db.String(32), nullable=False)
    game_day = db.Column(db.Date, nullable=False, index=True)

    foods: Mapped[list[GameFood]] = db.relationship(
        "GameFood",
        secondary=game_meal_foods,
        lazy="joined",
    )


def current_game_day(now: datetime | None = None) -> date:
    now_msk = (now or datetime.now(tz=MSK)).astimezone(MSK)
    return (now_msk - timedelta(hours=6)).date()


def emoji_for_hp(hp: int) -> str:
    return "🙂" if hp > 0 else "💀"


def ensure_game_state() -> GameState:
    today = current_game_day()
    state = db.session.get(GameState, 1)
    if state is None:
        state = GameState(id=1, hp=0, game_day=today)
        db.session.add(state)
        db.session.commit()
        return state
    if state.game_day != today:
        state.hp = 0
        state.game_day = today
        db.session.commit()
    return state


def get_or_create_foods(names: list[str]) -> list[GameFood]:
    foods: list[GameFood] = []
    seen: set[str] = set()
    for raw in names:
        name = (raw or "").strip()
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        seen.add(key)
        food = db.session.scalar(select(GameFood).where(GameFood.name == name))
        if food is None:
            food = GameFood(name=name)
            db.session.add(food)
            db.session.flush()
        foods.append(food)
    return foods
