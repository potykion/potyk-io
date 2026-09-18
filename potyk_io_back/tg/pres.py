from __future__ import annotations

import asyncio
import logging
import os
import threading

from flask import Blueprint, request
from telegram import Bot, Update
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

tg_bp = Blueprint("tg", __name__, url_prefix="/tg")

_bot: Bot | None = None
_bot_ready = False
_bot_lock = threading.Lock()
_loop = asyncio.new_event_loop()


def _token() -> str | None:
    value = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    return value or None


def _api_base_url() -> str:
    # PTB appends TOKEN/method → …/bot<TOKEN>/getMe
    value = (os.environ.get("TELEGRAM_API_BASE_URL") or "").strip().rstrip("/")
    if value:
        return value if value.endswith("/bot") else f"{value}/bot"
    return "https://api.telegram.org/bot"


def _api_file_base_url() -> str:
    value = (os.environ.get("TELEGRAM_API_FILE_BASE_URL") or "").strip().rstrip("/")
    if value:
        return value if value.endswith("/file/bot") else f"{value}/file/bot"
    base = _api_base_url()
    if base.endswith("/bot"):
        return base[: -len("/bot")] + "/file/bot"
    return "https://api.telegram.org/file/bot"


def _run(coro):
    return _loop.run_until_complete(coro)


def get_bot() -> Bot | None:
    global _bot, _bot_ready
    token = _token()
    if not token:
        return None
    with _bot_lock:
        if _bot is None:
            _bot = Bot(
                token=token,
                base_url=_api_base_url(),
                base_file_url=_api_file_base_url(),
            )
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
    message = update.effective_message if update else None
    if message is None:
        return "", 200

    try:
        _run(
            bot.copy_message(
                chat_id=message.chat_id,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )
        )
    except TelegramError:
        logger.exception("telegram echo failed")
        if message.text:
            try:
                _run(bot.send_message(chat_id=message.chat_id, text=message.text))
            except TelegramError:
                logger.exception("telegram text echo failed")

    return "", 200
