from __future__ import annotations

from pathlib import Path

import discord
import structlog

from discord.ext import commands

from progandbot.core.config import settings
from progandbot.core.i18n import I18nManager


logger = structlog.get_logger(__name__)


class ProgAndBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=settings.COMMAND_PREFIX, intents=intents)

        self.translator = I18nManager()

    async def on_ready(self) -> None:
        assert self.user is not None, "Bot user is not initialized"
        logger.info(f"Logged in as {self.user.name}!", user_id=self.user.id)

    async def setup_hook(self) -> None:
        cogs_path = Path(__file__).parent.parent / "cogs"
        logger.info("Setting up bot cogs", cogs_path=str(cogs_path))
        for file in cogs_path.glob("*.py"):
            if file.name.startswith("_"):
                continue

            try:
                module_path = ".".join(file.with_suffix("").parts[-3:])
                await self.load_extension(module_path)
                logger.info(f"Loaded cog: {module_path}")
            except Exception as e:
                logger.error(f"Failed to load cog {file.name}", error=str(e))
                raise e

    async def send_guild_only_or_error(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            "This command can only be used in a server.", ephemeral=True
        )
        return

    async def send_text_channel_only_error(
        self, interaction: discord.Interaction
    ) -> None:
        if not interaction.guild:
            await self.send_guild_only_or_error(interaction)
            return

        guild_id = interaction.guild.id
        translated_msg = await self.translator.get_translated_str(
            guild_id, "error_cmd_text_channel_only"
        )
        await interaction.response.send_message(translated_msg, ephemeral=True)
