from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from discord.ext import commands

from progandbot.db.models.user_profile import UserProfile
from progandbot.db.session import get_session


if TYPE_CHECKING:
    import discord


logger = structlog.get_logger(__name__)


class MessageTracker(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        user_id = message.author.id
        async with get_session() as session:
            user_profile = await session.get(UserProfile, (guild_id, user_id))
            if not user_profile:
                user_profile = UserProfile(guild_id=guild_id, user_id=user_id)
                session.add(user_profile)
                self.logger.info(
                    "Created new user profile", guild_id=guild_id, user_id=user_id
                )

            user_profile.message_count += 1
            await session.commit()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MessageTracker(bot))
