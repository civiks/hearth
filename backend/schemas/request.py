from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ServiceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    service_name: str | None = None
    customer_id: int
    customer_name: str | None = None
    professional_id: int | None = None
    date_of_request: date
    date_of_completion: datetime | None = None
    service_status: str
    scheduled_time: datetime | None = None
    address: str
    pincode: str
    remarks: str | None = None


class ServiceRequestCreate(BaseModel):
    service_id: int
    scheduled_time: datetime
    address: str
    pincode: str
    remarks: str | None = None


class ServiceRequestUpdate(BaseModel):
    service_status: str | None = None
    scheduled_time: datetime | None = None
    address: str | None = None
    pincode: str | None = None
    remarks: str | None = None
    professional_id: int | None = None
