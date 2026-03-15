import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.account.models import User
from app.domain.account.schema import UserDetailResponse

UPDATABLE_FIELDS = frozenset(["display_name", "username"])


@pytest.mark.parametrize(
    "body",
    [
        {"display_name": "golang"},
        {"username": "고랭고랭"},
        {"display_name": "golang", "username": "고랭고랭"},
    ],
)
async def test_사용자가_변경하는_항목만_변경되고_나머지는_기존_값을_유지한다(
    client_with_auth,
    body: dict,
    test_user: User,
):
    response = await client_with_auth.patch("/account/update", json=body)

    assert response.status_code == status.HTTP_200_OK

    data = UserDetailResponse(**response.json())

    # 변경된 항목은 변경된 값으로 변경되어야 한다.
    for k, v in body.items():
        assert getattr(data, k) == v
    # 변경되지 않은 항목은 기존 값을 유지한다.
    for k in UPDATABLE_FIELDS - frozenset(body.keys()):
        assert getattr(data, k) == getattr(test_user, k)


async def test_최소_하나_이상_항목을_변경해야_하며_그렇지_않으면_오류를_일으킨다(client_with_auth):
    response = await client_with_auth.patch("/account/update", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_비밀번호_변경_시_해싱_처리한_비밀번호가_저장되어야_한다(
    client_with_auth,
    test_user,
    db_session: AsyncSession,
):
    before_password = test_user.hashed_password
    body = {"password": "new_password", "password_repeat": "new_password"}

    response = await client_with_auth.patch("/account/update", json=body)

    assert response.status_code == status.HTTP_200_OK
    assert test_user.hashed_password != before_password


async def test_로그아웃_시_인증_토큰이_삭제되어야_한다(client_with_auth):
    response = await client_with_auth.delete("/account/logout")

    assert response.status_code == status.HTTP_200_OK


async def test_회원탈퇴_시_유저가_삭제되어야_한다(client_with_auth, test_user, db_session):
    user_id = test_user.id

    assert await db_session.get(User, user_id) is not None

    response = await client_with_auth.delete("/account/unregister")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await db_session.get(User, user_id) is None
