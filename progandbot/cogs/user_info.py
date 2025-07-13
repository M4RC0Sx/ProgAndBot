from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import structlog

from discord import app_commands
from discord.ext import commands

from progandbot.db.models.user_profile import UserProfile
from progandbot.db.session import get_session


if TYPE_CHECKING:
    from progandbot.core.bot import ProgAndBot


logger = structlog.get_logger(__name__)


class UserInfo(commands.Cog):
    def __init__(self, bot: ProgAndBot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    @app_commands.command(
        name="userinfo",
        description="Get user profile info.",
    )
    @app_commands.describe(
        target_user="User to get info for. Defaults to the user who invoked the command.",
    )
    async def user_info(
        self,
        interaction: discord.Interaction,
        target_user: discord.Member | discord.User | None = None,
    ) -> None:
        if interaction.guild is None:
            await self.bot.send_guild_only_or_error(interaction)
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            await self.bot.send_text_channel_only_error(interaction)
            return

        if target_user is None:
            target_user = interaction.user

        async with get_session() as session:
            user_profile = await session.get(
                UserProfile, (interaction.guild.id, target_user.id)
            )
            if not user_profile:
                await interaction.response.send_message(
                    f"No profile found for {target_user.mention}.", ephemeral=True
                )
                return

            assert self.bot.user is not None, "Bot user is not initialized"
            embed = (
                discord.Embed(
                    title="User Information",
                    description=f"Showing {target_user.mention} profile.",
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow(),
                )
                .set_thumbnail(url=target_user.display_avatar.url)
                .set_footer(
                    text="ProgAndBot UserInfo",
                    icon_url=self.bot.user.display_avatar.url,
                )
                .add_field(name="ID", value=target_user.id, inline=True)
                .add_field(
                    name="Signup Date",
                    value=target_user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    inline=True,
                )
                .add_field(inline=False, name="", value="")
                .add_field(name="Username", value=target_user.name, inline=True)
                .add_field(
                    name="Warnings", value=user_profile.warning_count, inline=True
                )
                .add_field(
                    name="Messages", value=user_profile.message_count, inline=True
                )
            )

            await interaction.response.send_message(embed=embed)


async def setup(bot: ProgAndBot) -> None:
    await bot.add_cog(UserInfo(bot))
