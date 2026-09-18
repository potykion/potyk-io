"""Long-poll Telegram updates via TELEGRAM_API_BASE_URL (CF Worker).

Webhook inbound to Yandex often times out from Telegram DCs; polling only
needs outbound HTTPS through the Worker.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from dotenv import load_dotenv
from telegram.error import NetworkError, RetryAfter, TimedOut

from potyk_io_back.tg.bot_util import create_bot, echo_update

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("tg.poller")


async def run() -> None:
    load_dotenv()
    bot = create_bot()
    if bot is None:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

    await bot.initialize()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("webhook deleted; starting long polling")

    offset: int | None = None
    while True:
        try:
            updates = await bot.get_updates(
                offset=offset,
                timeout=50,
                allowed_updates=["message"],
            )
            for update in updates:
                offset = update.update_id + 1
                await echo_update(bot, update)
        except RetryAfter as exc:
            logger.warning("flood wait %ss", exc.retry_after)
            await asyncio.sleep(float(exc.retry_after) + 1)
        except (TimedOut, NetworkError):
            logger.warning("network hiccup, retry", exc_info=True)
            await asyncio.sleep(2)
        except Exception:
            logger.exception("poller loop error")
            await asyncio.sleep(3)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
