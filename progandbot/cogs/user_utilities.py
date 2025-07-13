from __future__ import annotations

from random import randint
from typing import TYPE_CHECKING

import discord
import structlog

from discord import app_commands
from discord.ext import commands


if TYPE_CHECKING:
    from progandbot.core.bot import ProgAndBot


logger = structlog.get_logger(__name__)


class UserUtilities(commands.Cog):
    def __init__(self, bot: ProgAndBot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    @app_commands.command(
        name="dice",
        description="Roll a dice and get a random number between 1 and 6.",
    )
    async def dice(
        self,
        interaction: discord.Interaction,
    ) -> None:
        if not self.bot.user:
            await interaction.response.send_message(
                "Bot user is not available. Please try again later.", ephemeral=True
            )
            return

        if interaction.guild is None:
            await self.bot.send_guild_only_or_error(interaction)
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            await self.bot.send_text_channel_only_error(interaction)
            return

        result = randint(1, 6)
        img_path = f"assets/dice/{result}.png"
        file_name = f"dice_{result}.png"
        discord_file = discord.File(img_path, filename=file_name)

        embed = discord.Embed(
            title="Dice Roll 🎲",
            description=f"{interaction.user.mention} rolled a dice and got: **{result}**",
            color=discord.Color.yellow(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=f"attachment://{file_name}")
        embed.set_footer(
            text="ProgAndBot Dice Roll",
            icon_url=self.bot.user.display_avatar.url,
        )

        await interaction.response.send_message(
            embed=embed,
            file=discord_file,
        )

    @app_commands.command(
        name="coinflip",
        description="Flip a coin and get either Heads or Tails.",
    )
    async def coinflip(
        self,
        interaction: discord.Interaction,
    ) -> None:
        if not self.bot.user:
            await interaction.response.send_message(
                "Bot user is not available. Please try again later.", ephemeral=True
            )
            return

        if interaction.guild is None:
            await self.bot.send_guild_only_or_error(interaction)
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            await self.bot.send_text_channel_only_error(interaction)
            return

        result = randint(1, 2)
        result_text = "Heads" if result == 1 else "Tails"

        file_name = f"{result_text.lower()}.png"

        img_path = f"assets/coin/{file_name}"
        discord_file = discord.File(img_path, filename=file_name)

        embed = discord.Embed(
            title="Coin Flip 🪙",
            description=f"{interaction.user.mention} flipped a coin and got: **{result_text.upper()}**",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=f"attachment://{file_name}")
        embed.set_footer(
            text="ProgAndBot Coin Flip",
            icon_url=self.bot.user.display_avatar.url,
        )

        await interaction.response.send_message(
            embed=embed,
            file=discord_file,
        )


async def setup(bot: ProgAndBot) -> None:
    await bot.add_cog(UserUtilities(bot))
