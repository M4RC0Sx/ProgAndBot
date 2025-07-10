from __future__ import annotations

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlmodel import Field
from sqlmodel import SQLModel


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    guild_id: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("guild_configs.guild_id"),
            primary_key=True,
            autoincrement=False,
        ),
    )
    user_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
    )

    xp: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    level: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    message_count: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    warning_count: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
