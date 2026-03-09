from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.database import DbSessionDep
from app.domain.account.exceptions import DuplicatedEmail, DuplicatedUsername
from app.domain.account.models import User
from app.domain.account.schema import UserCreate, UserResponse

router = APIRouter(prefix="/account")


@router.get("/users/{username}", response_model=UserResponse)
async def user_detail(username: str, db: DbSessionDep):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get("/signup", response_model=UserResponse)
async def signup(body: UserCreate, db: DbSessionDep):
    existing_user: User = await db.scalar(
        select(User).where((User.email == body.email) | (User.username == body.username))
    )

    if existing_user:
        if existing_user.username == body.username:
            raise DuplicatedUsername
        else:
            raise DuplicatedEmail

    user = User(**body.model_dump(exclude={"password_repeat"}))
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user
