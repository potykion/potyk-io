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


def register_rest_api(bp: Blueprint) -> None:
    @bp.get("/api/rest")
    @login_required
    def api_rest_list():
        return jsonify(_payload())

    @bp.post("/api/rest")
    @login_required
    def api_rest_create():
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

        if not name:
            return _error("Укажи название")
        if len(name) > 255:
            return _error("Название слишком длинное")
        if not cuisine:
            return _error("Укажи кухню")
        if len(cuisine) > 128:
            return _error("Кухня слишком длинная")
        if not tier:
            return _error("Укажи тир (S/A/B/C/D)")
        if len(maps_url) > 1024:
            return _error("Ссылка на карты слишком длинная")

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
