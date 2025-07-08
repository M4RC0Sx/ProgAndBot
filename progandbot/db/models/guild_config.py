from __future__ import annotations

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlmodel import Field
from sqlmodel import SQLModel


class GuildConfig(SQLModel, table=True):
    __tablename__ = "guild_configs"

    guild_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
    )

    welcome_channel_id: int | None = Field(default=None, index=True)
