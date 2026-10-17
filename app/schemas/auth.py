from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import UserSummary


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(default="", max_length=50)
    middle_name: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary
