from __future__ import annotations

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlmodel import Field
from sqlmodel import SQLModel


DEFAULT_WELCOME_MESSAGE = (
    "Welcome %MEMBER% to the server! Enjoy your stay!"
    " If you have any questions, feel free to ask."
)


class GuildConfig(SQLModel, table=True):
    __tablename__ = "guild_configs"

    guild_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
    )

    welcome_enabled: bool = Field(
        default=False, sa_column_kwargs={"server_default": "false"}
    )
    welcome_channel_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, index=True)
    )
    welcome_message: str = Field(
        default=DEFAULT_WELCOME_MESSAGE,
        sa_column_kwargs={"server_default": DEFAULT_WELCOME_MESSAGE},
    )

    polls_channel_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, index=True)
    )
