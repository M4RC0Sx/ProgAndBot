from __future__ import annotations

import structlog

from progandbot.core.bot import ProgAndBot
from progandbot.core.config import settings
from progandbot.core.logging_config import setup_logging


def main() -> None:
    setup_logging(settings.LOG_LEVEL)

    token = settings.DISCORD_BOT_TOKEN
    bot = ProgAndBot()

    try:
        bot.run(token)
    except (KeyboardInterrupt, SystemExit):
        logger = structlog.get_logger()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
