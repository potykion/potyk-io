from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from flask.helpers import get_debug_flag
from werkzeug.serving import is_running_from_reloader

REPO_ROOT = Path(__file__).resolve().parents[2]


def upgrade_to_head() -> None:
    cfg = Config(str(REPO_ROOT / "alembic.ini"))
    command.upgrade(cfg, "head")


def startup_migrate_if_local(*, debug: bool | None = None) -> None:
    """Миграции при старте worker'а `flask run --debug` (не parent reloader, не прод)."""
    if debug is None:
        debug = get_debug_flag()
    if not debug or not is_running_from_reloader():
        return
    try:
        upgrade_to_head()
        print("[migrate] alembic upgrade head — ok", flush=True)
    except Exception as exc:
        print(f"[migrate] ошибка: {exc}", flush=True)
