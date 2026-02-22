from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import include_routers

TEST_DATABASE_URL = "mysql+aiomysql://root:root123@localhost:3306/myapi_test?charset=utf8mb4"

test_async_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


def create_app() -> FastAPI:
    app = FastAPI()
    include_routers(app)
    return app


# @pytest.fixture(scope="session")
"""
pytest-asyncio 1.x부터는

내부에서 이벤트 루프를 자동 관리

mode=auto면 async test/fixture 전부 자동 처리
"""
# def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
#     """
#     테스트 세션 동안 유지될 이벤트 루프를 생성
#     :return:
#     """
#     loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_database() -> AsyncGenerator[None, None]:
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_engine.connect() as conn:
        trans = await conn.begin()

        async_session = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )

        async with async_session() as session:
            yield session

        await trans.rollback()


@pytest.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    test_app = create_app()

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://localhost:8000/"
    ) as ac:
        yield ac

    test_app.dependency_overrides.clear()
