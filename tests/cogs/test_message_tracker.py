from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from progandbot.cogs.message_tracker import MessageTracker
from progandbot.db.models.user_profile import UserProfile
from progandbot.db.session import get_session


pytestmark = pytest.mark.asyncio


async def test_on_message_increments_message_count() -> None:
    bot_mock = MagicMock()
    cog = MessageTracker(bot_mock)

    guild_id = 12343
    user_id = 5678

    mock_message = MagicMock()
    mock_message.author.bot = False
    mock_message.guild.id = guild_id
    mock_message.author.id = user_id

    await cog.on_message(mock_message)

    async with get_session() as session:
        profile = await session.get(UserProfile, (guild_id, user_id))
        assert profile is not None
        assert profile.message_count == 1
