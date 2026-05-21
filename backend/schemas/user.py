from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str | None = None
    full_name: str
    address: str | None = None
    pincode: str | None = None
    is_blocked: bool
    is_active: bool = Field(default=True, alias="active")
    approval_status: str | None = None
    experience: int | None = None
    description: str | None = None
    service_id: int | None = None
    service_name: str | None = None
    avatar_url: str | None = None
    rating: float | None = None
    review_count: int | None = None


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    address: str | None = None
    pincode: str | None = None


class UserAdminUpdate(BaseModel):
    is_blocked: bool | None = None
    approval_status: str | None = None  # "approved" | "rejected" | "pending"
