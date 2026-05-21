from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import get_session
from backend.core.security import CurrentUser
from backend.models import Service, ServiceProfessional, ServiceRequest, ServiceStatus
from backend.schemas.request import (
    ServiceRequestCreate,
    ServiceRequestRead,
    ServiceRequestUpdate,
)

router = APIRouter(prefix="/api/requests", tags=["requests"])


VALID_STATUS_TRANSITIONS = {
    "user": {ServiceStatus.CANCELLED.value},
    "professional": {
        ServiceStatus.ACCEPTED.value,
        ServiceStatus.IN_PROGRESS.value,
        ServiceStatus.COMPLETED.value,
    },
    "admin": {s.value for s in ServiceStatus},
}


def _serialize(req: ServiceRequest) -> dict:
    return {
        "id": req.id,
        "service_id": req.service_id,
        "service_name": req.service.name if req.service else None,
        "customer_id": req.customer_id,
        "customer_name": req.customer.full_name if req.customer else None,
        "professional_id": req.professional_id,
        "date_of_request": req.date_of_request,
        "date_of_completion": req.date_of_completion,
        "service_status": req.service_status,
        "scheduled_time": req.scheduled_time,
        "address": req.address,
        "pincode": req.pincode,
        "remarks": req.remarks,
    }


def _user_role(user) -> str:
    return user.roles[0].name if user.roles else ""


def _visible_to(user, req: ServiceRequest, session: Session) -> bool:
    role = _user_role(user)
    if role == "admin":
        return True
    if role == "user":
        return req.customer_id == user.id
    if role == "professional":
        pro = session.scalars(
            select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
        ).first()
        return bool(pro and pro.service_id == req.service_id)
    return False


@router.get("", response_model=list[ServiceRequestRead])
def list_requests(
    user: CurrentUser, session: Annotated[Session, Depends(get_session)]
):
    role = _user_role(user)
    if role == "admin":
        rows = session.scalars(select(ServiceRequest)).all()
    elif role == "user":
        rows = session.scalars(
            select(ServiceRequest).where(ServiceRequest.customer_id == user.id)
        ).all()
    elif role == "professional":
        pro = session.scalars(
            select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
        ).first()
        if pro is None:
            return []
        rows = session.scalars(
            select(ServiceRequest).where(ServiceRequest.service_id == pro.service_id)
        ).all()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid role")
    return [_serialize(r) for r in rows]


@router.get("/{request_id}", response_model=ServiceRequestRead)
def get_request(
    request_id: int,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    req = session.get(ServiceRequest, request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    if not _visible_to(user, req, session):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")
    return _serialize(req)


@router.post("", response_model=ServiceRequestRead, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: ServiceRequestCreate,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="your account has been blocked. Please contact support.",
        )
    service = session.get(Service, payload.service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")

    req = ServiceRequest(
        service_id=payload.service_id,
        customer_id=user.id,
        scheduled_time=payload.scheduled_time,
        address=payload.address,
        pincode=payload.pincode,
        remarks=payload.remarks,
        date_of_request=datetime.now().date(),
        service_status=ServiceStatus.REQUESTED.value,
    )
    session.add(req)
    session.commit()
    session.refresh(req)
    return _serialize(req)


@router.put("/{request_id}", response_model=ServiceRequestRead)
def update_request(
    request_id: int,
    payload: ServiceRequestUpdate,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    req = session.get(ServiceRequest, request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    role = _user_role(user)

    if role == "professional":
        pro = session.scalars(
            select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
        ).first()
        if pro is None or pro.service_id != req.service_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")
    elif role == "user":
        if req.customer_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")
    elif role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")

    allowed: dict[str, set[str]] = {
        "user": {"remarks", "service_status", "scheduled_time", "address", "pincode"},
        "professional": {"service_status", "remarks"},
        "admin": {"service_status", "professional_id", "scheduled_time", "remarks"},
    }
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if field not in allowed[role]:
            continue
        if field == "service_status":
            if value not in VALID_STATUS_TRANSITIONS[role]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"invalid service status for {role}",
                )
            req.service_status = value
            if value == ServiceStatus.COMPLETED.value:
                req.date_of_completion = datetime.now()
        else:
            setattr(req, field, value)

    session.commit()
    session.refresh(req)
    return _serialize(req)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: int,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    req = session.get(ServiceRequest, request_id)
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    role = _user_role(user)
    if role != "admin" and req.customer_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized")
    if req.service_status in (ServiceStatus.IN_PROGRESS.value, ServiceStatus.COMPLETED.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot delete requests that are in progress or completed",
        )
    session.delete(req)
    session.commit()
