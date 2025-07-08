from __future__ import annotations

import structlog

from progandbot.core.bot import ProgAndBot
from progandbot.core.config import settings
from progandbot.core.logging_config import setup_logging


setup_logging(settings.LOG_LEVEL)
logger = structlog.get_logger(__name__)


def main() -> None:
    token = settings.DISCORD_BOT_TOKEN
    bot = ProgAndBot()

    try:
        bot.run(token, log_handler=None)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
