from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)
    role: Literal["user", "professional"]
    full_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    pincode: str = Field(min_length=3, max_length=10)

    # Professional-only
    service_id: int | None = None
    experience: int | None = None
    description: str | None = None


class LoginResponse(BaseModel):
    id: int
    email: str
    role: str | None
    full_name: str
    address: str | None
    pincode: str | None
    is_blocked: bool
    service_id: int | None = None
    approval_status: str | None = None
    avatar_url: str | None = None
