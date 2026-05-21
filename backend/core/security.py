"""Password hashing + JWT helpers + current_user dependency."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.db import get_session
from backend.models import User

JWT_ALGORITHM = "HS256"
COOKIE_NAME = "auth_token"


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings.jwt_lifetime_seconds)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    """Returns user_id from a valid token, raises HTTPException otherwise."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or expired token",
        ) from e


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    auth_token: Annotated[str | None, Cookie(alias=COOKIE_NAME)] = None,
) -> User:
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated"
        )
    user_id = decode_access_token(auth_token)
    user = session.get(User, user_id)
    if user is None or not user.active or user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user inactive or blocked"
        )
    return user


def require_role(*role_names: str):
    """Dependency factory that asserts the current user has one of the given role names."""

    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        user_roles = {r.name for r in user.roles}
        if not user_roles.intersection(role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"requires one of roles: {role_names}",
            )
        return user

    return dependency


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_role("admin"))]
ProfessionalUser = Annotated[User, Depends(require_role("professional"))]
CustomerUser = Annotated[User, Depends(require_role("user"))]


def serialize_user_for_login(session: Session, user: User) -> dict:
    """Match the legacy login response shape so the new FastAPI works as a drop-in."""
    from backend.models import ServiceProfessional

    role = user.roles[0].name if user.roles else None
    payload = {
        "id": user.id,
        "email": user.email,
        "role": role,
        "full_name": user.full_name,
        "address": user.address,
        "pincode": user.pincode,
        "is_blocked": user.is_blocked,
        "avatar_url": user.avatar_url,
    }
    if role == "professional":
        pro = session.scalars(
            select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
        ).first()
        if pro:
            payload["service_id"] = pro.service_id
            payload["approval_status"] = pro.approval_status
    return payload
