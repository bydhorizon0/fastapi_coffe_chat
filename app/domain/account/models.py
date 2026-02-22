from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# 순환 참조 방지를 위해 TYPE_CHECKING
# 타입 힌트는 필요하지만, 런타임 import는 피하고 싶을 때 사용한다.
if TYPE_CHECKING:
    from app.domain.calendar.models import Booking, Calendar


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False, comment="사용자 계정 ID"
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="사용자 이메일"
    )
    display_name: Mapped[str] = mapped_column(String(40), comment="사용자 표시 이름")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="사용자 비밀번호")
    is_host: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
        comment="사용자가 호스트인지 여부",
    )

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    # uselist : 1 : 1 관계
    # single_parent : 1 : 1 관계
    calendar: Mapped[Calendar] = relationship(
        back_populates="host", uselist=False, single_parent=True
    )

    booking: Mapped[list[Booking]] = relationship(back_populates="guest")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_account_id",
            name="uq_provider_provider_account_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=None)

    provider: Mapped[str] = mapped_column(String(10), comment="OAuth 제공자")
    provider_account_id: Mapped[int] = mapped_column(Integer, comment="OAuth 제공자 계정 ID")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped[User] = relationship(back_populates="oauth_accounts")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
