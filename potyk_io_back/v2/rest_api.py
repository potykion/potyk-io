from __future__ import annotations

import uuid
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_login import login_required
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from potyk_io_back.admin.posts import slugify_title
from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.restaurants.entities import (
    FoodRest,
    food_rest_cuisines,
    food_rest_to_dict,
    list_food_rest,
    normalize_tier,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
LOGO_DIR = REPO_ROOT / "static" / "potyk-io" / "img" / "restaurants"
LOGO_URL_PREFIX = "/static/potyk-io/img/restaurants"
ALLOWED_LOGO_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _payload() -> dict:
    rows = list_food_rest()
    return {
        "restaurants": [food_rest_to_dict(r) for r in rows],
        "cuisines": food_rest_cuisines(rows),
    }


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


def _save_logo(file: FileStorage, name: str) -> str:
    if file is None or not file.filename:
        return ""

    raw_name = secure_filename(file.filename) or "logo"
    ext = Path(raw_name).suffix.lower()
    if ext not in ALLOWED_LOGO_EXTS:
        raise ValueError("Лого: только png/jpg/webp/gif")

    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    stem = slugify_title(name)[:48] or "rest"
    filename = f"{stem}-{uuid.uuid4().hex[:8]}{ext}"
    path = LOGO_DIR / filename
    file.save(path)
    return f"{LOGO_URL_PREFIX}/{filename}"


def _read_fields() -> tuple[str, str, str, str, FileStorage | None]:
    if request.content_type and "multipart/form-data" in request.content_type:
        name = str(request.form.get("name") or "").strip()
        cuisine = str(request.form.get("cuisine") or "").strip()
        tier = normalize_tier(str(request.form.get("tier") or ""))
        maps_url = str(request.form.get("maps_url") or "").strip()
        logo_file = request.files.get("logo")
    else:
        data = request.get_json(silent=True) or {}
        name = str(data.get("name") or "").strip()
        cuisine = str(data.get("cuisine") or "").strip()
        tier = normalize_tier(str(data.get("tier") or ""))
        maps_url = str(data.get("maps_url") or "").strip()
        logo_file = None
    return name, cuisine, tier, maps_url, logo_file


def _validate_fields(
    name: str, cuisine: str, tier: str, maps_url: str
) -> str | None:
    if not name:
        return "Укажи название"
    if len(name) > 255:
        return "Название слишком длинное"
    if not cuisine:
        return "Укажи кухню"
    if len(cuisine) > 128:
        return "Кухня слишком длинная"
    if not tier:
        return "Укажи тир (S/A/B/C/D)"
    if len(maps_url) > 1024:
        return "Ссылка на карты слишком длинная"
    return None


def register_rest_api(bp: Blueprint) -> None:
    @bp.get("/api/rest")
    def api_rest_list():
        return jsonify(_payload())

    @bp.post("/api/rest")
    @login_required
    def api_rest_create():
        name, cuisine, tier, maps_url, logo_file = _read_fields()
        err = _validate_fields(name, cuisine, tier, maps_url)
        if err:
            return _error(err)

        try:
            logo = _save_logo(logo_file, name) if logo_file else ""
        except ValueError as exc:
            return _error(str(exc))
        except OSError:
            return _error("Не удалось сохранить лого", 500)

        row = FoodRest(
            name=name,
            cuisine=cuisine,
            tier=tier,
            logo=logo,
            maps_url=maps_url,
        )
        db.session.add(row)
        db.session.commit()
        body = _payload()
        body["created"] = food_rest_to_dict(row)
        return jsonify(body)

    @bp.put("/api/rest/<int:rest_id>")
    @login_required
    def api_rest_update(rest_id: int):
        row = db.session.get(FoodRest, rest_id)
        if row is None:
            return _error("Ресторан не найден", 404)

        name, cuisine, tier, maps_url, logo_file = _read_fields()
        err = _validate_fields(name, cuisine, tier, maps_url)
        if err:
            return _error(err)

        row.name = name
        row.cuisine = cuisine
        row.tier = tier
        row.maps_url = maps_url

        if logo_file and logo_file.filename:
            try:
                logo = _save_logo(logo_file, name)
            except ValueError as exc:
                return _error(str(exc))
            except OSError:
                return _error("Не удалось сохранить лого", 500)
            row.logo = logo

        db.session.commit()
        body = _payload()
        body["updated"] = food_rest_to_dict(row)
        return jsonify(body)

    @bp.delete("/api/rest/<int:rest_id>")
    @login_required
    def api_rest_delete(rest_id: int):
        row = db.session.get(FoodRest, rest_id)
        if row is None:
            return _error("Ресторан не найден", 404)
        db.session.delete(row)
        db.session.commit()
        return jsonify(_payload())
