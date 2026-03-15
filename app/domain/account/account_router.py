from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, select

from app.database import DbSessionDep
from app.domain.account.dependencies import CurrentUserDep
from app.domain.account.exceptions import (
    DuplicatedEmail,
    DuplicatedUsername,
    PasswordMissmatchError,
    UserNotFoundError,
)
from app.domain.account.models import User
from app.domain.account.schema import (
    LoginRequest,
    TokenResponse,
    UpdateUserRequest,
    UserCreateRequest,
    UserDetailResponse,
    UserResponse,
)
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
        key="auth_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 30,
    )

    return TokenResponse(access_token=access_token)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserDetailResponse)
async def me(user: CurrentUserDep):
    return user


@router.patch("/update", response_model=UserDetailResponse)
async def update_user(user: CurrentUserDep, body: UpdateUserRequest, db: DbSessionDep):
    # 이렇게 하면 None도 포함되어, NULL로 업데이트 됨.
    # updated_data = body.model_dump(include={"username", "display_name"})
    updated_data = body.model_dump(exclude_unset=True, exclude={"password", "password_repeat"})

    for k, v in updated_data.items():
        setattr(user, k, v)

    if body.password:
        user.hashed_password = hash_password(body.password)

    # SQLAlchemy가 변경을 감지(dirty tracking) 하기 때문에 commit() 하면 DB에 업데이트된다.
    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout(user: CurrentUserDep, response: Response):
    response.delete_cookie("auth_token")


@router.delete("/unregister", status_code=status.HTTP_204_NO_CONTENT)
async def unregister(user: CurrentUserDep, db: DbSessionDep):
    await db.execute(delete(User).where(User.email == user.email))
    await db.commit()
