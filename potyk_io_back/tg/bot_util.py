from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from telegram import Bot, Update
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BotConfig:
    name: str
    token: str
    enabled: bool = True


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


def bots_file_path() -> Path:
    raw = (os.environ.get("TELEGRAM_BOTS_FILE") or "").strip()
    if raw:
        return Path(raw)
    return Path("instance") / "telegram_bots.json"


def load_bot_configs() -> list[BotConfig]:
    """Load bots from JSON file, or legacy TELEGRAM_BOT_TOKEN as ``default``."""
    path = bots_file_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.exception("failed to read bots file %s", path)
            return []
        if not isinstance(data, list):
            logger.error("bots file %s: expected JSON array", path)
            return []
        configs: list[BotConfig] = []
        seen: set[str] = set()
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                logger.error("bots file entry %s: not an object", i)
                continue
            name = str(item.get("name") or "").strip()
            token = str(item.get("token") or "").strip()
            enabled = bool(item.get("enabled", True))
            if not name or not token:
                logger.error("bots file entry %s: name and token required", i)
                continue
            if name in seen:
                logger.error("bots file: duplicate name %r skipped", name)
                continue
            seen.add(name)
            configs.append(BotConfig(name=name, token=token, enabled=enabled))
        return configs

    legacy = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if legacy:
        return [BotConfig(name="default", token=legacy, enabled=True)]
    return []


def enabled_bots() -> list[BotConfig]:
    return [c for c in load_bot_configs() if c.enabled]


def create_bot(token: str) -> Bot:
    return Bot(
        token=token,
        base_url=api_base_url(),
        base_file_url=api_file_base_url(),
    )


def create_bot_from_env() -> Bot | None:
    """Single bot for Flask webhook fallback (first enabled, or legacy)."""
    bots = enabled_bots()
    if not bots:
        return None
    return create_bot(bots[0].token)


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
