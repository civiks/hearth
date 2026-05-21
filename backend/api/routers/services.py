from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import get_session
from backend.core.security import AdminUser
from backend.models import Service
from backend.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceRead])
def list_services(session: Annotated[Session, Depends(get_session)]):
    return list(session.scalars(select(Service).where(Service.is_active.is_(True))).all())


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, session: Annotated[Session, Depends(get_session)]):
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    _admin: AdminUser,
    session: Annotated[Session, Depends(get_session)],
):
    existing = session.scalars(select(Service).where(Service.name == payload.name.strip())).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="a service with this name already exists",
        )
    service = Service(
        name=payload.name.strip(),
        base_price=payload.base_price,
        time_required=payload.time_required,
        description=(payload.description or "").strip() or None,
        category=payload.category,
    )
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    _admin: AdminUser,
    session: Annotated[Session, Depends(get_session)],
):
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    session.commit()
    session.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    _admin: AdminUser,
    session: Annotated[Session, Depends(get_session)],
):
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    session.delete(service)
    session.commit()
