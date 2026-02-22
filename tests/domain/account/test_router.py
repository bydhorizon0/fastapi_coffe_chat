from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.domain.account.models import User

# async def test_user_detail_not_found():
#     """
#     pytest.raises 로 예외 오류가 발생했는지 검사한다.
#     :return:
#     """
#     with pytest.raises(HTTPException) as exc_info:
#         await user_detail("not_found")
#     assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


async def test_user_detail_by_http(db_session: AsyncSession, client: AsyncClient):
    user = User(
        username="test",
        email="test@example.com",
        password="test",
        display_name="test",
        is_host=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.get("/account/users/test")

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["username"] == "test"
    assert result["email"] == "test@example.com"
    assert result["display_name"] == "test"


async def test_user_detail_by_http_not_found(client: AsyncClient):
    response = await client.get("/account/users/not_found")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}
