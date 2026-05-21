from pydantic import BaseModel, ConfigDict


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    base_price: float
    time_required: int
    description: str | None = None
    category: str | None = None
    is_active: bool
    image_url: str | None = None
    rating: float | None = None
    review_count: int | None = None


class ServiceCreate(BaseModel):
    name: str
    base_price: float
    time_required: int
    description: str | None = None
    category: str | None = None
    image_url: str | None = None
    rating: float | None = None
    review_count: int | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    base_price: float | None = None
    time_required: int | None = None
    description: str | None = None
    category: str | None = None
    is_active: bool | None = None
    image_url: str | None = None
    rating: float | None = None
    review_count: int | None = None
