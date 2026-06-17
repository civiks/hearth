import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.core import crypto
from backend.core.db import get_session
from backend.core.security import AdminUser, CurrentUser
from backend.core.storage import AVATAR_DIR
from backend.models import Role, ServiceProfessional, ServiceRequest, User
from backend.schemas.user import UserAdminUpdate, UserProfileUpdate, UserRead
from backend.services.users import serialize_user

router = APIRouter(prefix="/api/users", tags=["users"])

VALID_APPROVAL_STATUSES = {"approved", "rejected", "pending"}

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}
MAX_AVATAR_BYTES = 5 * 1024 * 1024
AVATAR_URL_PREFIX = "/media/avatars/"


class GeminiKeyStatus(BaseModel):
    """Whether the caller has a stored Gemini key. The key itself is never
    returned — once stored, the only operations are 'replace' and 'delete'."""

    configured: bool


class GeminiKeySet(BaseModel):
    api_key: str = Field(min_length=20, max_length=200)


@router.get("/me", response_model=UserRead)
def get_me(user: CurrentUser):
    return serialize_user(user)


@router.get("/me/gemini-key", response_model=GeminiKeyStatus)
def get_my_gemini_key_status(user: CurrentUser) -> GeminiKeyStatus:
    return GeminiKeyStatus(configured=bool(user.gemini_api_key_encrypted))


@router.put("/me/gemini-key", response_model=GeminiKeyStatus)
def set_my_gemini_key(
    payload: GeminiKeySet,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> GeminiKeyStatus:
    """Encrypt and store the user's Gemini API key.

    503 if the server has no encryption key configured — without one we
    refuse to write plaintext-equivalent secrets to the DB.
    """
    try:
        token = crypto.encrypt(payload.api_key.strip())
    except crypto.EncryptionUnavailable as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        ) from e
    user.gemini_api_key_encrypted = token
    session.commit()
    return GeminiKeyStatus(configured=True)


@router.delete("/me/gemini-key", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_gemini_key(
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> None:
    user.gemini_api_key_encrypted = None
    session.commit()


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


@router.post("/me/avatar", response_model=UserRead)
async def upload_my_avatar(
    request: Request,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    file: Annotated[UploadFile, File()],
):
    ext = ALLOWED_AVATAR_TYPES.get(file.content_type or "")
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image type. Use JPEG, PNG, WebP, or GIF.",
        )
    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file.")
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must be 5 MB or smaller.",
        )

    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{user.id}-{secrets.token_hex(8)}.{ext}"
    (AVATAR_DIR / filename).write_bytes(data)

    old = user.avatar_url or ""
    if AVATAR_URL_PREFIX in old:
        old_path = AVATAR_DIR / old.rsplit("/", 1)[-1]
        if old_path.is_file():
            old_path.unlink(missing_ok=True)

    base = str(request.base_url).rstrip("/")
    user.avatar_url = f"{base}{AVATAR_URL_PREFIX}{filename}"
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
    skip: int = 0,
    limit: int = 100,
):
    limit = min(limit, 200)
    query = select(User).options(
        selectinload(User.roles),
        selectinload(User.professionals).selectinload(ServiceProfessional.service),
    )
    if role:
        query = query.join(User.roles).where(Role.name == role)
    users = session.scalars(query.offset(skip).limit(limit)).all()
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
