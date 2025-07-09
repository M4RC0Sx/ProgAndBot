from __future__ import annotations

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import String
from sqlmodel import Field
from sqlmodel import SQLModel


DEFAULT_WELCOME_MESSAGE = (
    "Welcome %MEMBER% to the server! Enjoy your stay!"
    " If you have any questions, feel free to ask."
)
DEFAULT_POLLS_MESSAGE = "A new poll has been created! @everyone"


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
        max_length=2000,
        sa_column=Column(
            String(2000), server_default=DEFAULT_WELCOME_MESSAGE, nullable=False
        ),
    )

    polls_channel_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, index=True)
    )
    polls_message: str = Field(
        default=DEFAULT_POLLS_MESSAGE,
        max_length=2000,
        sa_column=Column(
            String(2000), server_default=DEFAULT_POLLS_MESSAGE, nullable=False
        ),
    )
