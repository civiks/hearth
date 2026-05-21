from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import get_session
from backend.core.security import AdminUser, CurrentUser
from backend.models import Role, ServiceProfessional, ServiceRequest, User
from backend.schemas.user import UserAdminUpdate, UserProfileUpdate, UserRead
from backend.services.users import serialize_user

router = APIRouter(prefix="/api/users", tags=["users"])

VALID_APPROVAL_STATUSES = {"approved", "rejected", "pending"}


@router.get("/me", response_model=UserRead)
def get_me(user: CurrentUser):
    return serialize_user(user)


@router.put("/me", response_model=UserRead)
def update_me(
    payload: UserProfileUpdate,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    session.commit()
    session.refresh(user)
    return serialize_user(user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(user: CurrentUser, session: Annotated[Session, Depends(get_session)]):
    session.execute(
        ServiceProfessional.__table__.delete().where(ServiceProfessional.user_id == user.id)
    )
    session.execute(
        ServiceRequest.__table__.delete().where(ServiceRequest.customer_id == user.id)
    )
    session.delete(user)
    session.commit()


@router.get("", response_model=list[UserRead])
def list_users(
    _admin: AdminUser,
    session: Annotated[Session, Depends(get_session)],
    role: str | None = None,
):
    query = select(User)
    if role:
        query = query.join(User.roles).where(Role.name == role)
    users = session.scalars(query).all()
    return [serialize_user(u) for u in users]


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int, _admin: AdminUser, session: Annotated[Session, Depends(get_session)]
):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return serialize_user(user)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserAdminUpdate,
    _admin: AdminUser,
    session: Annotated[Session, Depends(get_session)],
):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    if payload.is_blocked is not None:
        user.is_blocked = payload.is_blocked

    if payload.approval_status is not None:
        if payload.approval_status not in VALID_APPROVAL_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid approval status"
            )
        if not any(r.name == "professional" for r in user.roles):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="user is not a professional"
            )
        pro = session.scalars(
            select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
        ).first()
        if pro is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="service professional record not found",
            )
        pro.approval_status = payload.approval_status

    session.commit()
    session.refresh(user)
    return serialize_user(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, _admin: AdminUser, session: Annotated[Session, Depends(get_session)]
):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    session.execute(
        ServiceProfessional.__table__.delete().where(ServiceProfessional.user_id == user.id)
    )
    session.delete(user)
    session.commit()
