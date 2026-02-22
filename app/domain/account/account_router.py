from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.database import get_db
from app.domain.account.models import User
from app.domain.account.schema import UserResponse

router = APIRouter(prefix="/account")


@router.get("/users/{username}", response_model=UserResponse)
async def user_detail(username: str, db: Annotated[AsyncSession, Depends(get_db)]) -> dict:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
