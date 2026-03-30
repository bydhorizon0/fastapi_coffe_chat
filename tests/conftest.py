from typing import AsyncGenerator

import pytest_asyncio
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import Base, get_db
from app.domain.account.models import User
from app.domain.account.schema import LoginRequest
from app.domain.calendar.models import Calendar
from app.domain.core.utils import hash_password

TEST_DATABASE_URL = "mysql+aiomysql://root:root123@localhost:3306/myapi_test?charset=utf8mb4"

test_async_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=True, pool_pre_ping=False)

    from app.domain.account import models
    from app.domain.calendar import models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        async_session = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            class_=AsyncSession,
            join_transaction_mode="create_savepoint",
        )

        async with async_session() as session:
            yield session

        await conn.rollback()


@pytest_asyncio.fixture
async def app(db_session: AsyncSession) -> AsyncGenerator[FastAPI, None]:
    from app.main import app

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def host_user(db_session: AsyncSession):
    user = User(
        username="test",
        email="test@example.com",
        display_name="test_fixture",
        hashed_password=hash_password("123"),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def client_with_auth(client: AsyncClient, host_user):
    body = LoginRequest(email="test@example.com", password="123")

    response = await client.post("/account/login", json=body.model_dump())

    assert response.status_code == status.HTTP_200_OK

    token = response.cookies.get("auth_token")
    assert token is not None

    client.cookies["auth_token"] = token
    yield client


@pytest_asyncio.fixture()
async def guest_user(db_session):
    user = User(
        username="guest",
        hashed_password=hash_password("root123"),
        email="guest@gmail.com",
        display_name="guest",
        is_host=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user


@pytest_asyncio.fixture()
async def host_user_calendar(db_session, host_user: User):
    calendar = Calendar(
        host_id=host_user.id,
        description=f"{host_user.username}의 캘린더입니다.",
        topics=["fastapi", "sqlalchemy"],
        google_calendar_id="123123",
    )

    db_session.add(calendar)
    await db_session.commit()
    await db_session.refresh(host_user)
    await db_session.flush()
    return calendar
