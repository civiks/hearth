from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from backend.core.db import get_session
from backend.core.security import AdminUser, CurrentUser
from backend.models import ApprovalStatus, Review, Service, ServiceProfessional
from backend.schemas.service import (
    ReviewRead,
    ServiceCreate,
    ServiceProfessionalRead,
    ServiceRead,
    ServiceUpdate,
)

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceRead])
def list_services(
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 100,
):
    limit = min(limit, 200)
    return list(
        session.scalars(
            select(Service).where(Service.is_active.is_(True)).offset(skip).limit(limit)
        ).all()
    )


@router.get("/all", response_model=list[ServiceRead])
def list_all_services(
    _admin: AdminUser,
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    limit: int = 100,
):
    limit = min(limit, 200)
    return list(session.scalars(select(Service).offset(skip).limit(limit)).all())


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, session: Annotated[Session, Depends(get_session)]):
    service = session.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="service not found")
    return service


@router.get("/{service_id}/professionals", response_model=list[ServiceProfessionalRead])
def list_service_professionals(
    service_id: int,
    _user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    """Approved, unblocked professionals offering this service (for the booking detail view)."""
    pros = session.scalars(
        select(ServiceProfessional)
        .options(selectinload(ServiceProfessional.user))
        .where(
            ServiceProfessional.service_id == service_id,
            ServiceProfessional.approval_status == ApprovalStatus.APPROVED.value,
        )
    ).all()
    return [
        ServiceProfessionalRead(
            id=p.id,
            full_name=p.user.full_name,
            service_id=p.service_id,
            avatar_url=p.user.avatar_url,
            rating=p.user.rating,
            review_count=p.user.review_count,
            experience=p.experience,
            description=p.description,
        )
        for p in pros
        if p.user and not p.user.is_blocked
    ]


@router.get("/{service_id}/reviews", response_model=list[ReviewRead])
def list_service_reviews(
    service_id: int,
    _user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    limit: int = 20,
):
    """Most recent customer reviews for a service."""
    limit = min(limit, 50)
    return list(
        session.scalars(
            select(Review)
            .options(selectinload(Review.author))
            .where(Review.service_id == service_id)
            .order_by(desc(Review.date_created))
            .limit(limit)
        ).all()
    )


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
