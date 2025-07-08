from __future__ import annotations

import discord
import structlog

from discord.ext import commands

from progandbot.core.config import settings


logger = structlog.get_logger(__name__)


class ProgAndBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix=settings.COMMAND_PREFIX, intents=intents)

    async def on_ready(self) -> None:
        assert self.user is not None, "Bot user is not initialized"
        logger.info(f"Logged in as {self.user.name}!", user_id=self.user.id)
