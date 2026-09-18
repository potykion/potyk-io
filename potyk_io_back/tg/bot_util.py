from __future__ import annotations

import logging
import os

from telegram import Bot, Update
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


def token() -> str | None:
    value = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    return value or None


def api_base_url() -> str:
    value = (os.environ.get("TELEGRAM_API_BASE_URL") or "").strip().rstrip("/")
    if value:
        return value if value.endswith("/bot") else f"{value}/bot"
    return "https://api.telegram.org/bot"


def api_file_base_url() -> str:
    value = (os.environ.get("TELEGRAM_API_FILE_BASE_URL") or "").strip().rstrip("/")
    if value:
        return value if value.endswith("/file/bot") else f"{value}/file/bot"
    base = api_base_url()
    if base.endswith("/bot"):
        return base[: -len("/bot")] + "/file/bot"
    return "https://api.telegram.org/file/bot"


def create_bot() -> Bot | None:
    tok = token()
    if not tok:
        return None
    return Bot(
        token=tok,
        base_url=api_base_url(),
        base_file_url=api_file_base_url(),
    )


async def echo_update(bot: Bot, update: Update) -> None:
    message = update.effective_message
    if message is None:
        return
    try:
        await bot.copy_message(
            chat_id=message.chat_id,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
        )
    except TelegramError:
        logger.exception("telegram echo failed")
        if message.text:
            try:
                await bot.send_message(chat_id=message.chat_id, text=message.text)
            except TelegramError:
                logger.exception("telegram text echo failed")
