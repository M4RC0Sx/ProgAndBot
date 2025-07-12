from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from progandbot.db import session as db_session


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from collections.abc import Generator


@pytest.fixture(scope="session")
def event_loop(
    request: pytest.FixtureRequest,
) -> Generator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_session_override(
    event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[None]:
    test_engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    TestSessionFactory = async_sessionmaker(  # noqa: N806
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    db_session.AsyncSessionFactory = TestSessionFactory

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
