from __future__ import annotations

import discord
import structlog

from discord import app_commands
from discord.ext import commands

from progandbot.db.models.user_profile import UserProfile
from progandbot.db.session import get_session


logger = structlog.get_logger(__name__)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    @app_commands.command(
        name="kick",
        description="Kick a member from the server.",
    )
    @app_commands.describe(
        member="The member to kick from the server.",
        reason="The reason for kicking the member.",
    )
    @app_commands.default_permissions(kick_members=True)
    async def kick_member(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Unspecified reason",
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            return

        if member == interaction.user:
            await interaction.response.send_message(
                "You cannot kick yourself!", ephemeral=True
            )
            return

        try:
            assert self.bot.user is not None, "Bot user is not initialized"
            embed = (
                discord.Embed(
                    title="Moderation: Member Kicked",
                    description=f"{member.mention} has been kicked from the server.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow(),
                )
                .set_thumbnail(url=member.display_avatar.url)
                .set_footer(
                    text="ProgAndBot Moderation",
                    icon_url=interaction.user.display_avatar.url,
                )
                .add_field(
                    name="Kicked By", value=interaction.user.mention, inline=True
                )
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=True)
            await interaction.channel.send(embed=embed)

            await member.kick(reason=reason)

            await interaction.response.send_message(
                f"Successfully kicked {member.mention} from the server."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to kick this member.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while trying to kick the member: {e!s}",
                ephemeral=True,
            )

    @app_commands.command(
        name="ban",
        description="Ban a member from the server.",
    )
    @app_commands.describe(
        member="The member to ban from the server.",
        reason="The reason for banning the member.",
        clear_messages="Whether to clear the member's messages.",
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban_member(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Unspecified reason",
        clear_messages: bool = False,
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            return

        if member == interaction.user:
            await interaction.response.send_message(
                "You cannot ban yourself!", ephemeral=True
            )
            return

        try:
            assert self.bot.user is not None, "Bot user is not initialized"
            embed = (
                discord.Embed(
                    title="Moderation: Member Banned",
                    description=f"{member.mention} has been banned from the server.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow(),
                )
                .set_thumbnail(url=member.display_avatar.url)
                .set_footer(
                    text="ProgAndBot Moderation",
                    icon_url=interaction.user.display_avatar.url,
                )
                .add_field(
                    name="Banned By", value=interaction.user.mention, inline=True
                )
                .set_image(
                    url="https://i2.kym-cdn.com/photos/images/masonry/000/791/407/40c.gif"
                )
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=True)
            await interaction.channel.send(embed=embed)

            await member.ban(
                reason=reason, delete_message_days=7 if clear_messages else 0
            )

            await interaction.response.send_message(
                f"Successfully banned {member.mention} from the server."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to ban this member.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while trying to ban the member: {e!s}",
                ephemeral=True,
            )

    @app_commands.command(
        name="warn",
        description="Warn a member in the server.",
    )
    @app_commands.describe(
        member="The member to ban from the server.",
        reason="The reason for banning the member.",
    )
    @app_commands.default_permissions(kick_members=True)
    async def warn_member(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Unspecified reason",
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            await interaction.response.send_message(
                "This command can only be used in a text channel.", ephemeral=True
            )
            return

        if member == interaction.user:
            await interaction.response.send_message(
                "You cannot warn yourself!", ephemeral=True
            )
            return

        try:
            async with get_session() as session:
                user_profile = await session.get(
                    UserProfile, (interaction.guild.id, member.id)
                )
                if not user_profile:
                    user_profile = UserProfile(
                        guild_id=interaction.guild.id, user_id=member.id
                    )
                    session.add(user_profile)
                    self.logger.info(
                        "Created new user profile",
                        guild_id=interaction.guild.id,
                        user_id=member.id,
                    )

                user_profile.warning_count += 1
                await session.commit()

            assert self.bot.user is not None, "Bot user is not initialized"
            embed = (
                discord.Embed(
                    title="Moderation: Member Warned",
                    description=f"{member.mention} has been warned.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow(),
                )
                .set_thumbnail(url=member.display_avatar.url)
                .set_footer(
                    text="ProgAndBot Moderation",
                    icon_url=interaction.user.display_avatar.url,
                )
                .add_field(
                    name="Warned By", value=interaction.user.mention, inline=True
                )
                .set_image(
                    url="https://media.tenor.com/sLgNruA4tsgAAAAM/warning-lights.gif"
                )
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=True)
            await interaction.channel.send(embed=embed)

            await interaction.response.send_message(
                f"Successfully warned {member.mention}."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I do not have permission to warn this member.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while trying to warn the member: {e!s}",
                ephemeral=True,
            )

    @app_commands.command(
        name="clear",
        description="Clear a specified number of messages from the channel.",
    )
    @app_commands.describe(
        amount="The number of messages to clear (1-100).",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def clear_messages(
        self,
        interaction: discord.Interaction,
        amount: int = 10,
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            return

        if amount not in range(1, 100 + 1):
            await interaction.response.send_message(
                "You must specify a number between 1 and 100.", ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True, ephemeral=True)

        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(
                f"Successfully cleared {len(deleted)} messages from the channel."
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "I do not have permission to clear messages in this channel.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"An error occurred while trying to clear messages: {e!s}",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
