"""Long-poll Telegram updates via TELEGRAM_API_BASE_URL (CF Worker).

Supports multiple bots from instance/telegram_bots.json (enable/disable).
"""

from __future__ import annotations

import asyncio
import logging
import sys

from dotenv import load_dotenv
from telegram.error import NetworkError, RetryAfter, TimedOut

from potyk_io_back.tg.bot_util import (
    BotConfig,
    create_bot,
    echo_update,
    enabled_bots,
    load_bot_configs,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("tg.poller")

RELOAD_EVERY_SEC = 5.0


async def poll_one(cfg: BotConfig, stop: asyncio.Event) -> None:
    bot = create_bot(cfg.token)
    await bot.initialize()
    # getUpdates conflicts if a remote delivery URL is still registered
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("[%s] long polling", cfg.name)

    offset: int | None = None
    while not stop.is_set():
        try:
            updates = await bot.get_updates(
                offset=offset,
                timeout=50,
                allowed_updates=["message"],
            )
            for update in updates:
                offset = update.update_id + 1
                await echo_update(bot, update)
        except asyncio.CancelledError:
            raise
        except RetryAfter as exc:
            logger.warning("[%s] flood wait %ss", cfg.name, exc.retry_after)
            await asyncio.sleep(float(exc.retry_after) + 1)
        except (TimedOut, NetworkError):
            logger.warning("[%s] network hiccup, retry", cfg.name, exc_info=True)
            await asyncio.sleep(2)
        except Exception:
            logger.exception("[%s] poller loop error", cfg.name)
            await asyncio.sleep(3)

    try:
        await bot.shutdown()
    except Exception:
        logger.exception("[%s] bot shutdown failed", cfg.name)


async def supervisor() -> None:
    """Start/stop poll loops as bots are enabled/disabled in the config file."""
    running: dict[str, tuple[BotConfig, asyncio.Task, asyncio.Event]] = {}
    idle_logged = False

    async def stop_bot(name: str) -> None:
        entry = running.pop(name, None)
        if entry is None:
            return
        cfg, task, stop = entry
        stop.set()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        logger.info("[%s] stopped", cfg.name)

    while True:
        desired = {c.name: c for c in enabled_bots()}

        for name in list(running):
            cfg, _task, _stop = running[name]
            want = desired.get(name)
            if want is None or want.token != cfg.token:
                await stop_bot(name)

        for name, cfg in desired.items():
            if name in running:
                continue
            stop = asyncio.Event()
            task = asyncio.create_task(poll_one(cfg, stop), name=f"tg-{name}")
            running[name] = (cfg, task, stop)
            logger.info("[%s] started", name)
            idle_logged = False

        if not desired and not running and not idle_logged:
            configs = load_bot_configs()
            if not configs:
                logger.warning("no bots configured; waiting for bots file / TELEGRAM_BOT_TOKEN")
            else:
                logger.warning("all bots disabled; waiting")
            idle_logged = True

        await asyncio.sleep(RELOAD_EVERY_SEC)


async def run() -> None:
    load_dotenv()
    await supervisor()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
