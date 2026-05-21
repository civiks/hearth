"""User-shape helpers for serializing User + professional fields together (legacy shape)."""

from backend.models import ServiceProfessional, User


def serialize_user(user: User) -> dict:
    role = user.roles[0].name if user.roles else None
    pro: ServiceProfessional | None = user.professionals[0] if user.professionals else None
    out = {
        "id": user.id,
        "email": user.email,
        "role": role,
        "full_name": user.full_name,
        "address": user.address,
        "pincode": user.pincode,
        "is_blocked": user.is_blocked,
        "active": user.active,
        "avatar_url": user.avatar_url,
        "rating": user.rating,
        "review_count": user.review_count,
    }
    if pro:
        out.update(
            {
                "approval_status": pro.approval_status,
                "experience": pro.experience,
                "description": pro.description,
                "service_id": pro.service_id,
                "service_name": pro.service.name if pro.service else None,
            }
        )
    return out
