from pathlib import Path

from flask import Blueprint, abort, current_app, jsonify, send_from_directory
from flask_login import current_user, login_required

from potyk_io_back.v2.fin_api import register_fin_api
from potyk_io_back.v2.rest_api import register_rest_api

v2_bp = Blueprint("v2", __name__, url_prefix="/v2")

DIST_DIR = Path(__file__).resolve().parents[2] / "potyk-io-front" / "dist"


@v2_bp.get("/api/me")
@login_required
def api_me():
    return jsonify({"authenticated": True, "id": current_user.get_id()})


register_fin_api(v2_bp)
register_rest_api(v2_bp)


@v2_bp.route("/", defaults={"asset_path": ""})
@v2_bp.route("/<path:asset_path>")
def spa(asset_path: str):
    """SPA shell публичный: закрытые разделы режет vue-router + API login_required."""
    if asset_path.startswith("api/"):
        abort(404)

    if not DIST_DIR.is_dir():
        return (
            "potyk-io-front не собран. Локально: cd potyk-io-front && npm run dev "
            "(или npm run build для раздачи из Flask).",
            503,
            {"Content-Type": "text/plain; charset=utf-8"},
        )

    if asset_path:
        candidate = DIST_DIR / asset_path
        if candidate.is_file():
            return send_from_directory(DIST_DIR, asset_path)

    index = DIST_DIR / "index.html"
    if not index.is_file():
        abort(503)
    response = send_from_directory(DIST_DIR, "index.html")
    if current_app.debug:
        response.headers["Cache-Control"] = "no-store"
    return response
