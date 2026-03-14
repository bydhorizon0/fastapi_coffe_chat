from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select

from app.database import DbSessionDep
from app.domain.account.exceptions import (
    DuplicatedEmail,
    DuplicatedUsername,
    PasswordMissmatchError,
    UserNotFoundError,
)
from app.domain.account.models import User
from app.domain.account.schema import LoginRequest, TokenResponse, UserCreateRequest, UserResponse
from app.domain.core.utils import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/account")


@router.get("/users/{username}", response_model=UserResponse)
async def user_detail(username: str, db: DbSessionDep):
    result = await db.execute(select(User).where(User.username == username))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserCreateRequest, db: DbSessionDep):
    existing_user: User | None = await db.scalar(
        select(User).where((User.email == body.email) | (User.username == body.username))
    )

    if existing_user:
        if existing_user.username == body.username:
            raise DuplicatedUsername
        else:
            raise DuplicatedEmail

    user = User(
        **body.model_dump(exclude={"password", "password_repeat"}),
        hashed_password=hash_password(body.password),
    )
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(body: LoginRequest, db: DbSessionDep, response: Response):
    result = await db.execute(select(User).where(User.email == body.email))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundError()

    if not verify_password(body.password, user.hashed_password):
        raise PasswordMissmatchError()

    access_token = create_access_token(user.email)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 30
    )

    return TokenResponse(access_token=access_token)
