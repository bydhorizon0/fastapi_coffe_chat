from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    display_name: str

    model_config = ConfigDict(from_attributes=True)
