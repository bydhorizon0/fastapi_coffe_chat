from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Cookie, Depends
from sqlalchemy import select

from app.database import DbSessionDep
from app.domain.account.exceptions import ExpiredTokenError, InvalidTokenError, UserNotFoundError
from app.domain.account.models import User
from app.domain.core.settings import get_settings
from app.domain.core.utils import decode_token


async def get_current_user(
    auth_token: Annotated[str | None, Cookie()],
    db_session: DbSessionDep,
):
    if auth_token is None:
        raise InvalidTokenError()

    try:
        decoded = decode_token(auth_token)
    except Exception:
        raise InvalidTokenError()

    expires_at = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    if now + timedelta(minutes=get_settings().access_token_expire_minute) < expires_at:
        raise ExpiredTokenError()

    result = await db_session.execute(select(User).where(User.email == decoded["sub"]))
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundError()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
