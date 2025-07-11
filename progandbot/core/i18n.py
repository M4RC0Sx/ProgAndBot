from __future__ import annotations

import json

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import structlog

from progandbot.core.enums import SupportedLanguage
from progandbot.db.models.guild_config import GuildConfig
from progandbot.db.session import get_session


if TYPE_CHECKING:
    TranslationDict = dict[str, str | "TranslationDict"]


logger = structlog.get_logger(__name__)


class I18nManager:
    def __init__(self, locales_dir: str = "progandbot/locales") -> None:
        self.locales_dir = locales_dir
        self.locales: TranslationDict = {}
        self.load_locales()

    def load_locales(self) -> None:
        for file in Path(self.locales_dir).glob("*.json"):
            if not file.is_file():
                continue

            with open(file, encoding="utf-8") as f:
                try:
                    locale_data = json.load(f)
                    self.locales[file.stem] = locale_data
                    logger.info("Loaded locale file!", locale=file.stem)
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to load locale file!", file=file.stem, error=str(e)
                    )

    async def get_translated_str(self, guild_id: int, key: str, **kwargs: Any) -> str:
        lang_code = SupportedLanguage.EN
        async with get_session() as session:
            guild_config = await session.get(GuildConfig, guild_id)
            if guild_config and guild_config.language in SupportedLanguage:
                lang_code = guild_config.language

        keys = key.split(".")
        try:
            value = self.locales[lang_code]
            for k in keys:
                assert isinstance(value, dict)
                value = value[k]
            if not isinstance(value, str):
                logger.warning(
                    "Translation value is not a string",
                    lang_code=lang_code,
                    key=key,
                    value=value,
                )
                return key
            return value.format(**kwargs) if kwargs else value
        except (KeyError, TypeError) as e:
            logger.warning(
                "Translation key not found or invalid format",
                lang_code=lang_code,
                key=key,
                error=str(e),
            )
            return key
