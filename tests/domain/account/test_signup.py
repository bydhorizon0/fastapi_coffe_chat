import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.account.account_router import signup
from app.domain.account.exceptions import DuplicatedEmail, DuplicatedUsername
from app.domain.account.schema import UserCreate


@pytest.mark.asyncio
async def test_모든_입력_항목을_유효한_값으로_입력하면_계정이_생성된다(
    client: AsyncClient,
    db_session: AsyncSession,
):
    body = UserCreate(
        email="text@example.com",
        username="test",
        display_name="test",
        password="123",
        password_repeat="123",
    )

    result = await signup(body, db_session)

    response = await client.get(f"/account/users/{result.username}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == result.username
    assert data["email"] == result.email
    assert data["display_name"] == result.display_name
    assert data["is_host"] is False


@pytest.mark.parametrize("username", ["asdfsfwerkfdsksdfkwefkwekfsadfkskwekrkwer", "123456"])
async def test_사용자명이_유효하지_않으면_사용자명이_유효하지_않다는_메시지를_담은_오류를_일으킨다(
    username: str,
):
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            email="test@example.com",
            username=username,
            display_name="test",
            password="123",
            password_repeat="123",
        )

        assert "username은 숫자만으로 구성될 수 없습니다." in str(exc.value)


@pytest.mark.asyncio
async def test_중복된_ID_계정_오류(db_session: AsyncSession):
    body = UserCreate(
        email="test@example.com",
        username="test",
        display_name="test",
        password="123",
        password_repeat="123",
    )
    await signup(body, db_session)

    body.email = "aaa@example.com"

    # 두 번째 생성은 UNIQUE 제약 위반
    with pytest.raises(DuplicatedUsername) as exc:
        await signup(body, db_session)

    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "중복된 계정 ID입니다." in exc.value.detail


@pytest.mark.asyncio
async def test_중복된_이메일_계정_오류(db_session: AsyncSession):
    body = UserCreate(
        email="test@example.com",
        username="test",
        display_name="test",
        password="123",
        password_repeat="123",
    )
    await signup(body, db_session)

    body.username = "test1111"

    # 두 번째 생성은 UNIQUE 제약 위반
    with pytest.raises(DuplicatedEmail) as exc:
        await signup(body, db_session)

    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "중복된 계정 이메일입니다." in exc.value.detail


@pytest.mark.asyncio
async def test_표시명을_입력하지_않으면_무작위_문자열_8글자로_대신한다(db_session: AsyncSession):
    body = UserCreate(
        email="test@example.com",
        username="test",
        password="123",
        password_repeat="123",
    )

    user = await signup(body, db_session)

    assert isinstance(user.display_name, str)
    assert len(user.display_name) == 8
