from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.domain.account.models import User


class Calendar(Base):
    __tablename__ = "calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=None)
    topics: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="게스트와 나눌 주제들")

    description: Mapped[str] = mapped_column(Text, comment="게스트에게 보여줄 설명")
    google_calendar_id: Mapped[str] = mapped_column(String(1024), comment="Google Calendar ID")

    host_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    host: Mapped[User] = relationship(back_populates="calendar")

    time_slots: Mapped[list[TimeSlot]] = relationship(back_populates="calendar")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=None)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    weekdays: Mapped[list[int]] = mapped_column(JSON, comment="예약 가능한 요일들")

    calendar_id: Mapped[int] = mapped_column(ForeignKey("calendars.id"))
    calendar: Mapped[Calendar] = relationship(back_populates="time_slots")

    booking: Mapped[list[Booking]] = relationship(back_populates="time_slot")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=None)
    when: Mapped[date] = mapped_column(Date)
    topic: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, comment="예약 설명")

    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slots.id"))
    time_slot: Mapped[TimeSlot] = relationship(back_populates="booking")

    guest_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    guest: Mapped[User] = relationship(back_populates="booking")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
