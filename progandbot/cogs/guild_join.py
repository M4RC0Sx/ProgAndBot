from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from discord.ext import commands

from progandbot.db.models.guild_config import GuildConfig
from progandbot.db.session import get_session


if TYPE_CHECKING:
    import discord


logger = structlog.get_logger(__name__)


class GuildJoin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.logger.info("Joined a new guild", guild_id=guild.id, guild_name=guild.name)

        async with get_session() as session:
            guild_config = await session.get(GuildConfig, guild.id)
            if guild_config:
                self.logger.info(
                    "Skipping guild config creation, already exists", guild_id=guild.id
                )
                return

            guild_config = GuildConfig(guild_id=guild.id)
            session.add(guild_config)
            await session.commit()
            self.logger.info("Created new guild config", guild_id=guild.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GuildJoin(bot))
