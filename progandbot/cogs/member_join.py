from __future__ import annotations

import io

import discord
import structlog

from discord.ext import commands
from PIL import Image
from PIL import ImageDraw

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

    async def _create_welcome_image(self, member: discord.Member) -> io.BytesIO | None:
        if member.avatar is None:
            return None

        background = Image.open("assets/welcome_background.jpg")

        draw = ImageDraw.Draw(background)

        avatar_size = (150, 150)

        avatar_bytes = await member.avatar.read()
        avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
        avatar_image = avatar_image.resize(avatar_size)

        avatar_mask = Image.new("L", avatar_size, 0)
        draw_mask = ImageDraw.Draw(avatar_mask)
        draw_mask.ellipse((0, 0, *avatar_size), fill=255)

        background.paste(avatar_image, (50, 50), mask=avatar_mask)

        draw.text(
            (220, 80),
            "WELCOME!",
            fill="white",
            font=None,
        )
        draw.text(
            (220, 150),
            f"{member.name}#{member.discriminator}",
            fill="white",
            font=None,
        )

        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

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

        image_buffer = await self._create_welcome_image(member)
        if image_buffer:
            picture = discord.File(image_buffer, filename="welcome.png")

        try:
            assert isinstance(welcome_channel, discord.TextChannel)
            if image_buffer:
                await welcome_channel.send(content=welcome_message, file=picture)
            else:
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
