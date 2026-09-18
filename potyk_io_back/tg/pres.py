from __future__ import annotations

import asyncio
import logging
import os
import threading

from flask import Blueprint, request
from telegram import Update
from telegram.error import TelegramError

from potyk_io_back.tg.bot_util import create_bot_from_env, echo_update

logger = logging.getLogger(__name__)

tg_bp = Blueprint("tg", __name__, url_prefix="/tg")

_bot = None
_bot_ready = False
_bot_lock = threading.Lock()
_loop = asyncio.new_event_loop()


def _run(coro):
    return _loop.run_until_complete(coro)


def get_bot():
    global _bot, _bot_ready
    with _bot_lock:
        if _bot is None:
            _bot = create_bot_from_env()
        if _bot is None:
            return None
        if not _bot_ready:
            try:
                _run(_bot.initialize())
            except TelegramError:
                logger.exception("telegram bot initialize failed")
                raise
            _bot_ready = True
        return _bot


@tg_bp.post("/webhook")
def webhook():
    """Optional webhook path; prod uses long-polling (potyk-tg.service)."""
    try:
        bot = get_bot()
    except TelegramError:
        return "telegram api unavailable", 502

    if bot is None:
        return "bot not configured", 503

    secret = (os.environ.get("TELEGRAM_WEBHOOK_SECRET") or "").strip()
    if secret:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header != secret:
            return "forbidden", 403

    data = request.get_json(force=True, silent=True)
    if not data:
        return "", 200

    update = Update.de_json(data, bot)
    if update is None:
        return "", 200

    _run(echo_update(bot, update))
    return "", 200
