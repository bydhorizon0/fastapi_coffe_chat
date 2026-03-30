from fastapi import APIRouter, status
from sqlalchemy import select

from app.database import DbSessionDep
from app.domain.account.dependencies import CurrentUserOptionalDep
from app.domain.account.models import User
from app.domain.calendar.exceptions import CalendarNotFoundError, HostNotFoundError
from app.domain.calendar.models import Calendar
from app.domain.calendar.schema import CalendarDetailResponse, CalendarResponse

router = APIRouter(prefix="/calendar")


@router.get(
    "/{host_email}",
    status_code=status.HTTP_200_OK,
    response_model=CalendarResponse | CalendarDetailResponse,
)
async def host_calendar_detail(
    host_email: str, user: CurrentUserOptionalDep, db_session: DbSessionDep
):
    result = await db_session.execute(select(User).where(User.email == host_email))
    host: User | None = result.scalar_one_or_none()

    if host is None:
        raise HostNotFoundError

    result = await db_session.execute(select(Calendar).where(Calendar.host_id == host.id))
    calendar: Calendar | None = result.scalar_one_or_none()

    if calendar is None:
        raise CalendarNotFoundError

    if user is not None and user.id == host.id:
        return CalendarDetailResponse.model_validate(calendar)
    return CalendarResponse.model_validate(calendar)
