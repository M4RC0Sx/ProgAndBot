from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import discord
import structlog

from discord import app_commands
from discord.ext import commands

from progandbot.db.models.guild_config import GuildConfig
from progandbot.db.session import get_session


if TYPE_CHECKING:
    from progandbot.core.bot import ProgAndBot


logger = structlog.get_logger(__name__)


class Polls(commands.Cog):
    def __init__(self, bot: ProgAndBot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

    @app_commands.command(
        name="poll",
        description="Create a poll in the polls defined channel.",
    )
    @app_commands.describe(
        question="The question for the poll.",
        answer_1="The first answer option. It is mandatory.",
        answer_2="The second answer option. It is mandatory.",
        answer_3="The third answer option. Optional.",
        answer_4="The fourth answer option. Optional.",
        answer_5="The fifth answer option. Optional.",
        answer_6="The sixth answer option. Optional.",
        answer_7="The seventh answer option. Optional.",
        answer_8="The eighth answer option. Optional.",
        answer_9="The ninth answer option. Optional.",
        answer_10="The tenth answer option. Optional.",
        duration_hours="Duration of the poll in hours. Default is 24 hours.",
        allow_multiple="Allow users to select multiple answers. Default is False.",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def create_poll(
        self,
        interaction: discord.Interaction,
        question: str,
        answer_1: str,
        answer_2: str,
        answer_3: str | None = None,
        answer_4: str | None = None,
        answer_5: str | None = None,
        answer_6: str | None = None,
        answer_7: str | None = None,
        answer_8: str | None = None,
        answer_9: str | None = None,
        answer_10: str | None = None,
        duration_hours: int = 24,
        allow_multiple: bool = False,
    ) -> None:
        if interaction.guild is None:
            await self.bot.send_guild_only_or_error(interaction)
            return
        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            await self.bot.send_text_channel_only_error(interaction)
            return

        async with get_session() as session:
            guild_config = await session.get(GuildConfig, interaction.guild.id)
            if not guild_config:
                await interaction.response.send_message(
                    "Guild configuration not found. Please set up the bot first.",
                    ephemeral=True,
                )
                return

            if not guild_config.polls_channel_id:
                await interaction.response.send_message(
                    "Polls channel is not set. Please configure it first.",
                    ephemeral=True,
                )
                return

            polls_channel = interaction.guild.get_channel(guild_config.polls_channel_id)
            if not polls_channel or not isinstance(polls_channel, discord.TextChannel):
                await interaction.response.send_message(
                    "Polls channel is invalid or not found.", ephemeral=True
                )
                return

            if not question:
                await interaction.response.send_message(
                    "You must provide a question for the poll.", ephemeral=True
                )
                return

            raw_answers = [
                answer_1,
                answer_2,
                answer_3,
                answer_4,
                answer_5,
                answer_6,
                answer_7,
                answer_8,
                answer_9,
                answer_10,
            ]
            answers = [answer for answer in raw_answers if answer]
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

            if len(answers) not in range(2, 10 + 1):
                await interaction.response.send_message(
                    "You must provide at least two answer options and at most 10 options!",
                    ephemeral=True,
                )
                return

            try:
                poll = discord.Poll(
                    question=question,
                    duration=timedelta(hours=duration_hours),
                    multiple=allow_multiple,
                )

                for i, answer in enumerate(answers):
                    poll.add_answer(text=answer, emoji=emojis[i])

                await polls_channel.send(poll=poll, content=guild_config.polls_message)
                await interaction.response.send_message(
                    f"Poll created successfully in {polls_channel.mention}!",
                    ephemeral=True,
                )

                logger.info(
                    "Poll created",
                    guild_id=interaction.guild.id,
                    channel_id=polls_channel.id,
                    question=question,
                    answers=answers,
                    duration_hours=duration_hours,
                    allow_multiple=allow_multiple,
                )

            except Exception as e:
                logger.error(
                    "Failed to create poll",
                    guild_id=interaction.guild.id,
                    channel_id=polls_channel.id,
                    error=str(e),
                )
                await interaction.response.send_message(
                    f"An error occurred while creating the poll: {e!s}",
                    ephemeral=True,
                )
                return


async def setup(bot: ProgAndBot) -> None:
    await bot.add_cog(Polls(bot))
