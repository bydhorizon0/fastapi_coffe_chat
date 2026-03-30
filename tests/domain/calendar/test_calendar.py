import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.account.models import User
from app.domain.calendar.calendar_router import host_calendar_detail
from app.domain.calendar.exceptions import CalendarNotFoundError, HostNotFoundError
from app.domain.calendar.models import Calendar
from app.domain.calendar.schema import CalendarDetailResponse, CalendarResponse


@pytest.mark.parametrize(
    "user_key, expected_type",
    [
        ("host_user", CalendarDetailResponse),
        ("guest_user", CalendarResponse),
        (None, CalendarResponse),
    ],
)
async def test_호스트인_사용자의_email_으로_캘린더_정보를_가져온다(
    user_key: str | None,
    expected_type: type[CalendarResponse | CalendarDetailResponse],
    host_user: User,
    host_user_calendar: Calendar,
    guest_user: User,
    db_session: AsyncSession,
):
    users = {
        "host_user": host_user,  # 사용자가 호스트 자신
        "guest_user": guest_user,  # 사용자가 호스트 자신이 아님
        None: None,  # 로그인 안 한 사용자
    }
    user = users[user_key]

    result: CalendarResponse | CalendarDetailResponse = await host_calendar_detail(
        host_user.email, user, db_session
    )

    assert isinstance(result, expected_type)

    result_keys = frozenset(result.model_dump().keys())
    expected_keys = frozenset(expected_type.model_fields.keys())
    assert result_keys == expected_keys

    # assert result.topics == host_user_calendar.topics
    # assert result.description == host_user_calendar.description
    if isinstance(result, CalendarDetailResponse):
        assert result.google_calendar_id == host_user_calendar.google_calendar_id


async def test_존재하지_않는_사용자의_email_으로_캘린더_정보를_가져오려_하면_404_응답을_반환한다(
    client_with_auth: AsyncClient,
):
    response = await client_with_auth.get("/calendar/not_exist_user")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_호스트가_아닌_사용자의_email_으로_캘린더_정보를_가져오려_하면_404_응답을_반환한다(
    guest_user, client_with_auth
):
    response = await client_with_auth.get(f"/calendar/{guest_user.email}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
