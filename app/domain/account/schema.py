import random
import string
from calendar import month
from datetime import datetime
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from app.domain.core.utils import hash_password


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    display_name: str
    is_host: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    display_name: str | None = Field(min_length=4, max_length=40, description="사용자 표시명")
    password: str = Field(min_length=3, max_length=128)
    password_repeat: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("username은 숫자만으로 구성될 수 없습니다.")
        if len(v) > 40:
            raise ValueError("username은 40자를 넘을 수 없습니다.")
        return v

    @model_validator(mode="before")
    @classmethod
    def generate_display_name(cls, data: dict):
        if not data.get("display_name"):
            data["display_name"] = "".join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )

        return data

    @model_validator(mode="after")
    def password_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str


class UserDetailResponse(BaseModel):
    email: EmailStr
    username: str
    display_name: str
    created_at: datetime
    updated_at: datetime


class UpdateUserRequest(BaseModel):
    username: str | None = Field(default=None, min_length=4, max_length=40)
    display_name: str | None = Field(default=None, min_length=4, max_length=128)
    password: str | None = Field(default=None, min_length=3, max_length=128)
    password_repeat: str | None = Field(default=None)

    @model_validator(mode="after")
    def check_all_fields_are_none(self) -> Self:
        if not self.model_dump(exclude_none=True):
            raise ValueError("최소 하나의 필드는 반드시 제공되어야 합니다.")
        return self

    @model_validator(mode="after")
    def password_match(self) -> Self:
        if self.password and self.password != self.password_repeat:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        return self
