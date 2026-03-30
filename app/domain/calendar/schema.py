from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CalendarResponse(BaseModel):
    topics: list[str]
    description: str

    model_config = ConfigDict(from_attributes=True)


class CalendarDetailResponse(BaseModel):
    host_id: int
    google_calendar_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
