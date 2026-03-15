from datetime import timedelta

from fastapi import status
from httpx import AsyncClient

from app.domain.account.schema import (
    LoginRequest,
    TokenResponse,
    UserCreateRequest,
    UserDetailResponse,
    UserResponse,
)
from app.domain.core.utils import create_access_token, decode_token


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


async def test_로그인_성공(client: AsyncClient, test_user):
    body = LoginRequest(email="test@example.com", password="123")

    response = await client.post("/account/login", json=body.model_dump())

    assert response.status_code == status.HTTP_200_OK

    data = TokenResponse(**response.json())

    assert data.access_token is not None

    cookie = response.cookies.get("auth_token")
    assert cookie is not None
    assert cookie == data.access_token


async def test_내_정보_조회(client_with_auth):
    response = await client_with_auth.get("/account/me")

    assert response.status_code == status.HTTP_200_OK

    data = UserDetailResponse(**response.json())


async def test_토큰이_없는_경우_의심스런_접근_오류를_일으킨다(client: AsyncClient):
    response = await client.get("/account/me")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_유효하지_않은_토큰인_경우_인증_오류를_일으킨다(client_with_auth):
    client_with_auth.cookies["auth_token"] = "invalid_token"
    response = await client_with_auth.get("/account/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_만료된_토큰으로_내_정보_조회(client_with_auth):
    token = client_with_auth.cookies.get("auth_token", domain="", path="/")
    decoded = decode_token(token)
    jwt = create_access_token(decoded["sub"], timedelta(hours=-1))
    client_with_auth.cookies["auth_token"] = jwt

    response = await client_with_auth.get("/account/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_유저가_존재하지_않는_경우_내_정보_조회(client_with_auth):
    token = client_with_auth.cookies.get("auth_token", domain="", path="/")
    decode = decode_token(token)
    decode["sub"] = "invalid_user_email"
    jwt = create_access_token(decode["sub"])
    client_with_auth.cookies["auth_token"] = jwt

    response = await client_with_auth.get("/account/me")
    assert response.status_code == status.HTTP_404_NOT_FOUND
