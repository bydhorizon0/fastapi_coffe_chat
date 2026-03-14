import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.account.models import User
from app.domain.account.schema import LoginRequest, TokenResponse, UserCreateRequest, UserResponse
from app.domain.core.utils import hash_password


async def test_회원가입_성공(client: AsyncClient):
    body = UserCreateRequest(
        username="test",
        email="test@example.com",
        password="123",
        password_repeat="123",
    )

    response = await client.post("/account/signup", json=body.model_dump())

    data = UserResponse(**response.json())

    assert response.status_code == status.HTTP_201_CREATED
    assert data.username == body.username
    assert data.email == body.email


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
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


async def test_로그인_성공(client: AsyncClient, test_user):
    body = LoginRequest(email="test@example.com", password="123")

    response = await client.post("/account/login", json=body.model_dump())

    assert response.status_code == status.HTTP_200_OK

    data = TokenResponse(**response.json())

    assert data.access_token is not None

    cookie = response.cookies.get("access_token")
    assert cookie is not None
    assert cookie == data.access_token
