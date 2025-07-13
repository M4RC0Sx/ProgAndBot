from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import discord
import requests
import structlog

from discord.ext import commands
from discord.ext import tasks

from progandbot.core.config import settings


if TYPE_CHECKING:
    from collections.abc import Coroutine


logger = structlog.get_logger(__name__)


class TwitchNotifier(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logger.bind(cog_name=self.__class__.__name__)

        self.logger.info(f"Initialized {self.__class__.__name__} cog")

        self.twitch_access_token: str | None = None
        self.is_notified: bool = False

        self.check_twitch_live.start()

    def cog_unload(self) -> Coroutine[Any, Any, None]:
        self.check_twitch_live.cancel()
        return super().cog_unload()

    @tasks.loop(minutes=1)
    async def check_twitch_live(self) -> None:
        if not self.twitch_access_token:
            self._get_twitch_access_token()
            if not self.twitch_access_token:
                self.logger.error("Twitch access token is not available")
                return

        headers = {
            "Client-ID": settings.TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.twitch_access_token}",
        }
        params = {
            "user_login": settings.TWITCH_USERNAME,
            "first": "1",
        }
        url = "https://api.twitch.tv/helix/streams?type=live"

        try:
            response = requests.get(url, headers=headers, params=params)
        except requests.RequestException as e:
            self.logger.error(
                "Failed to fetch Twitch stream data",
                error=str(e),
            )
            return
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching Twitch stream data",
                error=str(e),
            )
            return

        if response.status_code == 401:
            self.logger.warning("Twitch access token expired, refreshing...")
            self._get_twitch_access_token()
            if not self.twitch_access_token:
                self.logger.error("Failed to refresh Twitch access token")
                return

        response.raise_for_status()
        data = response.json()

        if data["data"]:
            if self.is_notified:
                self.logger.info("Twitch stream is live, but already notified")
                return

            stream_info = data["data"][0]
            stream_title = stream_info["title"]
            stream_category = stream_info["game_name"]
            self.logger.info(
                "Twitch stream is live",
                title=stream_title,
                category=stream_category,
            )
            self._send_notification_to_channel(stream_title, stream_category)

        else:
            if self.is_notified:
                self.logger.info(
                    "Twitch stream is not live, resetting notification status"
                )
                self.is_notified = False
                return

    def _get_twitch_access_token(self) -> None:
        twitch_url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": settings.TWITCH_CLIENT_ID,
            "client_secret": settings.TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }

        try:
            response = requests.post(twitch_url, params=params)
            response.raise_for_status()
            data = response.json()
            self.twitch_access_token = data.get("access_token")
        except requests.RequestException as e:
            self.logger.error(
                "Failed to get Twitch access token",
                error=str(e),
            )
            self.twitch_access_token = None

    def _send_notification_to_channel(self, title: str, category: str) -> None:
        channel = self.bot.get_channel(settings.NOTIFICATIONS_CHANNEL_ID)
        if channel is None or not isinstance(channel, discord.TextChannel):
            self.logger.error(
                "Notification channel not found",
                channel_id=settings.NOTIFICATIONS_CHANNEL_ID,
            )
            return
        if self.bot.user is None:
            self.logger.error("Bot user is not available for notification")
            return

        message = f"**¡Ey!** ¡{settings.TWITCH_USERNAME} está en directo! ¿A qué esperas para ir a verlo? ||@everyone||\n"
        embed = (
            discord.Embed(
                title="¡Nuevo directo en Twitch!",
                url=f"https://www.twitch.tv/{settings.TWITCH_USERNAME}",
                description=f"{title}\n",
                color=discord.Color.purple(),
                timestamp=discord.utils.utcnow(),
            )
            .set_thumbnail(url=self.bot.user.display_avatar.url)
            .set_footer(
                text="ProgAndBot Twitch Notifier",
                icon_url=self.bot.user.display_avatar.url,
            )
            .add_field(name="Categoría", value=category, inline=True)
            .add_field(
                name="Canal de Twitch",
                value=f"https://www.twitch.tv/{settings.TWITCH_USERNAME}",
                inline=True,
            )
            .set_image(url="https://media.tenor.com/0yuiqR9nENMAAAAM/twitch-logo.gif")
        )

        self.bot.loop.create_task(channel.send(message, embed=embed))
        self.is_notified = True
        self.logger.info(
            "Twitch live notification sent to channel", channel_id=channel.id
        )

    @check_twitch_live.before_loop
    async def before_check(self) -> None:
        await self.bot.wait_until_ready()
        self.logger.info("Starting Twitch live check loop")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TwitchNotifier(bot))
