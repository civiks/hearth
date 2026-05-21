import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.db import get_session
from backend.core.security import (
    COOKIE_NAME,
    CurrentUser,
    create_access_token,
    hash_password,
    serialize_user_for_login,
    verify_password,
)
from backend.models import Role, Service, ServiceProfessional, User
from backend.schemas.auth import LoginRequest, LoginResponse, RegisterRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.jwt_lifetime_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.env != "local",
        path="/",
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
):
    user = session.scalars(select(User).where(User.email == payload.email)).first()
    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="account is blocked")

    token = create_access_token(user.id)
    _set_auth_cookie(response, token)
    return serialize_user_for_login(session, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=LoginResponse)
def me(user: CurrentUser, session: Annotated[Session, Depends(get_session)]):
    return serialize_user_for_login(session, user)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=LoginResponse)
def register(
    payload: RegisterRequest,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
):
    if session.scalars(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user already exists")

    if payload.role == "professional":
        if payload.service_id is None or payload.experience is None or not payload.description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="service_id, experience, and description are required for professionals",
            )
        service = session.get(Service, payload.service_id)
        if service is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid service_id"
            )

    role = session.scalars(select(Role).where(Role.name == payload.role)).first()
    if role is None:
        role = Role(name=payload.role, description=payload.role.capitalize())
        session.add(role)
        session.flush()

    import urllib.parse

    avatar_seed = urllib.parse.quote(payload.full_name)
    user = User(
        email=payload.email,
        password=hash_password(payload.password),
        full_name=payload.full_name,
        address=payload.address,
        pincode=payload.pincode,
        fs_uniquifier=secrets.token_hex(16),
        active=True,
        is_blocked=False,
        avatar_url=f"https://api.dicebear.com/9.x/notionists/svg?seed={avatar_seed}",
    )
    user.roles.append(role)
    session.add(user)
    session.flush()

    if payload.role == "professional":
        session.add(
            ServiceProfessional(
                user_id=user.id,
                service_id=payload.service_id,
                experience=payload.experience,
                description=payload.description,
                approval_status="pending",
            )
        )

    session.commit()
    session.refresh(user)

    token = create_access_token(user.id)
    _set_auth_cookie(response, token)
    return serialize_user_for_login(session, user)
