from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.db import get_session
from backend.core.security import AdminUser, ProfessionalUser
from backend.models import (
    Role,
    Service,
    ServiceProfessional,
    ServiceRequest,
    ServiceStatus,
    User,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/admin")
def admin_analytics(
    _admin: AdminUser, session: Annotated[Session, Depends(get_session)]
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    request_trends = session.execute(
        select(
            func.date(ServiceRequest.date_of_request).label("date"),
            func.count(ServiceRequest.id).label("count"),
        )
        .where(ServiceRequest.date_of_request.between(start_date.date(), end_date.date()))
        .group_by(func.date(ServiceRequest.date_of_request))
        .order_by(func.date(ServiceRequest.date_of_request))
    ).all()

    service_popularity = session.execute(
        select(Service.name, func.count(ServiceRequest.id).label("count"))
        .join(ServiceRequest, Service.id == ServiceRequest.service_id)
        .group_by(Service.name)
    ).all()

    user_registrations = session.execute(
        select(
            func.date(User.date_created).label("date"),
            func.count(User.id).label("count"),
        )
        .join(User.roles)
        .where(
            User.date_created.between(start_date, end_date),
            Role.name != "admin",
        )
        .group_by(func.date(User.date_created))
        .order_by(func.date(User.date_created))
    ).all()

    professional_status = session.execute(
        select(
            ServiceProfessional.approval_status,
            func.count(ServiceProfessional.id).label("count"),
        ).group_by(ServiceProfessional.approval_status)
    ).all()

    user_status = session.execute(
        select(User.is_blocked, func.count(User.id).label("count"))
        .join(User.roles)
        .where(Role.name != "admin")
        .group_by(User.is_blocked)
    ).all()

    return {
        "request_trends": [{"date": str(r.date), "count": r.count} for r in request_trends],
        "service_popularity": [
            {"name": r.name, "count": r.count} for r in service_popularity
        ],
        "user_registrations": [
            {"date": str(r.date), "count": r.count} for r in user_registrations
        ],
        "professional_status": [
            {"status": r.approval_status, "count": r.count} for r in professional_status
        ],
        "user_status": [
            {"status": "Blocked" if r.is_blocked else "Active", "count": r.count}
            for r in user_status
        ],
    }


@router.get("/professional")
def professional_analytics(
    user: ProfessionalUser, session: Annotated[Session, Depends(get_session)]
):
    pro = session.scalars(
        select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
    ).first()
    if pro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="professional record not found"
        )

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    requests = session.scalars(
        select(ServiceRequest).where(ServiceRequest.service_id == pro.service_id)
    ).all()

    total = len(requests)
    completed = len([r for r in requests if r.service_status == ServiceStatus.COMPLETED.value])
    completion_rate = (completed / total * 100) if total else 0.0

    monthly_earnings = session.execute(
        select(
            func.date(ServiceRequest.date_of_completion).label("date"),
            func.sum(Service.base_price).label("earnings"),
        )
        .join(Service, ServiceRequest.service_id == Service.id)
        .where(
            ServiceRequest.service_id == pro.service_id,
            ServiceRequest.service_status == ServiceStatus.COMPLETED.value,
            ServiceRequest.date_of_completion.between(start_date, end_date),
        )
        .group_by(func.date(ServiceRequest.date_of_completion))
        .order_by(func.date(ServiceRequest.date_of_completion))
    ).all()

    status_distribution = session.execute(
        select(
            ServiceRequest.service_status, func.count(ServiceRequest.id).label("count")
        )
        .where(ServiceRequest.service_id == pro.service_id)
        .group_by(ServiceRequest.service_status)
    ).all()

    return {
        "completion_rate": completion_rate,
        "monthly_earnings": [
            {"date": str(r.date), "earnings": float(r.earnings or 0)} for r in monthly_earnings
        ],
        "status_distribution": [
            {"status": r.service_status, "count": r.count} for r in status_distribution
        ],
    }
