from __future__ import annotations

import discord
import structlog

from discord import app_commands
from discord.ext import commands

from progandbot.db.models.guild_config import GuildConfig
from progandbot.db.session import get_session


logger = structlog.get_logger(__name__)


@app_commands.default_permissions(administrator=True)
@app_commands.guild_only()
class SettingsManagement(commands.GroupCog, group_name="settings"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    welcome_subgroup = app_commands.Group(
        name="welcome",
        description="Manage welcome settings for this server.",
    )

    @welcome_subgroup.command(
        name="enabled", description="Enable or disable welcome messages."
    )
    @app_commands.describe(
        enabled="True or False to enable or disable welcome messages."
    )
    async def set_welcome_enabled(
        self, interaction: discord.Interaction, enabled: bool
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        self.logger.info(
            "Setting welcome messages enabled",
            guild_id=interaction.guild.id,
            enabled=enabled,
        )

        async with get_session() as session:
            guild_config = await session.get(GuildConfig, interaction.guild.id)
            if not guild_config:
                guild_config = GuildConfig(guild_id=interaction.guild.id)
                session.add(guild_config)

            guild_config.welcome_enabled = enabled
            await session.commit()

        await interaction.response.send_message(
            f"Welcome messages set to {'enabled' if enabled else 'disabled'}",
            ephemeral=True,
        )

    @welcome_subgroup.command(
        name="channel", description="Set the welcome channel for this server."
    )
    @app_commands.describe(channel="The channel to set as the welcome channel.")
    async def set_welcome_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "You must specify a valid text channel.", ephemeral=True
            )
            return

        self.logger.info(
            "Setting welcome channel",
            guild_id=interaction.guild.id,
            channel_id=channel.id,
        )

        async with get_session() as session:
            guild_config = await session.get(GuildConfig, interaction.guild.id)
            if not guild_config:
                guild_config = GuildConfig(guild_id=interaction.guild.id)
                session.add(guild_config)

            guild_config.welcome_channel_id = channel.id
            await session.commit()

        await interaction.response.send_message(
            f"Welcome channel set to {channel.mention}", ephemeral=True
        )

    @welcome_subgroup.command(
        name="message", description="Set the welcome message for this server."
    )
    @app_commands.describe(message="The message to set as the welcome message.")
    async def set_welcome_message(
        self, interaction: discord.Interaction, message: str
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        if len(message) == 0:
            await interaction.response.send_message(
                "You must specify non-empty message.", ephemeral=True
            )
            return
        if len(message) > 2000:
            await interaction.response.send_message(
                "The message is too long. Please limit it to 2000 characters.",
                ephemeral=True,
            )
            return

        self.logger.info(
            "Setting welcome message",
            guild_id=interaction.guild.id,
        )

        async with get_session() as session:
            guild_config = await session.get(GuildConfig, interaction.guild.id)
            if not guild_config:
                guild_config = GuildConfig(guild_id=interaction.guild.id)
                session.add(guild_config)

            guild_config.welcome_message = message
            await session.commit()

        await interaction.response.send_message(
            f"Welcome message set to '{message}'", ephemeral=True
        )

    polls_subgroup = app_commands.Group(
        name="polls",
        description="Manage polls settings for this server.",
    )

    @polls_subgroup.command(
        name="channel", description="Set the polls channel for this server."
    )
    @app_commands.describe(channel="The channel to set as the polls channel.")
    async def set_polls_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                "You must specify a valid text channel.", ephemeral=True
            )
            return

        self.logger.info(
            "Setting polls channel",
            guild_id=interaction.guild.id,
            channel_id=channel.id,
        )

        async with get_session() as session:
            guild_config = await session.get(GuildConfig, interaction.guild.id)
            if not guild_config:
                guild_config = GuildConfig(guild_id=interaction.guild.id)
                session.add(guild_config)

            guild_config.polls_channel_id = channel.id
            await session.commit()

        await interaction.response.send_message(
            f"Polls channel set to {channel.mention}", ephemeral=True
        )

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context[commands.Bot]) -> None:
        self.logger.info("Syncing application commands")
        try:
            await self.bot.tree.sync()
            await ctx.send("Application commands synced successfully.")
        except Exception as e:
            self.logger.error("Failed to sync application commands", error=str(e))
            await ctx.send(f"Failed to sync application commands: {e}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SettingsManagement(bot))
