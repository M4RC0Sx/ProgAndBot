from __future__ import annotations

import discord
import structlog

from discord.ext import commands

from progandbot.db.models.guild_config import GuildConfig
from progandbot.db.session import get_session


logger = structlog.get_logger(__name__)


class MemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        guild_id = member.guild.id
        self.logger.info(
            "Member joined to a guild", member_id=member.id, guild_id=guild_id
        )

        async with get_session() as session:
            guild_config = await session.get(GuildConfig, guild_id)
            if not guild_config:
                self.logger.warning(
                    "Guild config not found for member join",
                    member_id=member.id,
                    guild_id=guild_id,
                )
                return
            await self._send_welcome_message(member, guild_config)

    async def _send_welcome_message(
        self, member: discord.Member, guild_config: GuildConfig
    ) -> None:
        if not guild_config.welcome_enabled or not guild_config.welcome_channel_id:
            return

        welcome_channel = member.guild.get_channel(guild_config.welcome_channel_id)
        if not welcome_channel:
            return
        welcome_message = guild_config.welcome_message.replace(
            "%MEMBER%", member.mention
        )

        try:
            assert isinstance(welcome_channel, discord.TextChannel)
            await welcome_channel.send(welcome_message)
            self.logger.info(
                "Sent welcome message",
                member_id=member.id,
                guild_id=guild_config.guild_id,
                channel_id=welcome_channel.id,
            )
        except Exception as e:
            self.logger.error(
                "Failed to send welcome message",
                member_id=member.id,
                guild_id=guild_config.guild_id,
                channel_id=guild_config.welcome_channel_id,
                error=str(e),
            )
            return


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MemberJoin(bot))
