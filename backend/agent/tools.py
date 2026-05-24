"""Server-side tool registry for the agent.

Each Tool is a sync callable that the agent runner invokes when Gemini emits
a `functionCall` chunk. Tools take a SQLAlchemy session + the authenticated
user and return a JSON-serializable dict whose shape mirrors what the
in-browser tools in `frontend/src/lib/genai.ts` return today — that way the
chat UI's tool-result cards render identically regardless of which backend
produces the data.

Role gating is enforced **here**, not (only) on the model. The runner refuses
to invoke a tool whose `roles` set doesn't include the caller's role, even if
the model tries to call it. The model gets a `forbidden` tool result back so
it can adjust its plan.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.models import (
    Role,
    Service,
    ServiceProfessional,
    ServiceRequest,
    ServiceStatus,
    User,
)

ToolFn = Callable[[Session, User, dict[str, Any]], Any]


class ToolError(Exception):
    """Tool-level failure surfaced to the model as `{ok: false, error: ...}`."""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    # JSON schema (Gemini-compatible) for the tool's arguments.
    params_schema: dict[str, Any]
    # Roles allowed to invoke this tool. Authoritative — see module docstring.
    roles: frozenset[str]
    run: ToolFn


# ─────────────────────────────────────────────── shared serializers
# Match the shapes the in-browser tools in lib/genai.ts return so the chat
# UI's tool-result cards render identically.


def _ser_service(s: Service) -> dict[str, Any]:
    return {
        "id": s.id,
        "name": s.name,
        "category": s.category,
        "description": s.description,
        "base_price": s.base_price,
        "time_required": s.time_required,
        "is_active": s.is_active,
        "image_url": s.image_url,
        "rating": s.rating,
        "review_count": s.review_count,
    }


def _ser_request(req: ServiceRequest) -> dict[str, Any]:
    return {
        "id": req.id,
        "service_id": req.service_id,
        "service_name": req.service.name if req.service else None,
        "customer_id": req.customer_id,
        "customer_name": req.customer.full_name if req.customer else None,
        "professional_id": req.professional_id,
        "professional_name": (
            req.professional.user.full_name
            if req.professional and req.professional.user
            else None
        ),
        "service_status": req.service_status,
        "scheduled_time": req.scheduled_time.isoformat() if req.scheduled_time else None,
        "address": req.address,
        "pincode": req.pincode,
        "remarks": req.remarks,
        "date_of_request": req.date_of_request.isoformat() if req.date_of_request else None,
        "date_of_completion": (
            req.date_of_completion.isoformat() if req.date_of_completion else None
        ),
    }


def _ser_pro_as_user(pro: ServiceProfessional) -> dict[str, Any]:
    """Serialize a ServiceProfessional as the legacy UserShape the chat
    UI expects on the pending-approvals card."""
    u = pro.user
    return {
        "id": u.id if u else pro.user_id,
        "email": u.email if u else None,
        "full_name": u.full_name if u else None,
        "role": "professional",
        "pincode": u.pincode if u else None,
        "approval_status": pro.approval_status,
        "experience": pro.experience,
        "description": pro.description,
        "service_id": pro.service_id,
        "service_name": pro.service.name if pro.service else None,
    }


def _require_int(args: dict[str, Any], key: str) -> int:
    v = args.get(key)
    if v is None:
        raise ToolError(f"missing required arg: {key}")
    try:
        return int(v)
    except (TypeError, ValueError) as e:
        raise ToolError(f"{key} must be an integer") from e


def _require_str(args: dict[str, Any], key: str) -> str:
    v = args.get(key)
    if not isinstance(v, str) or not v.strip():
        raise ToolError(f"missing required arg: {key}")
    return v.strip()


def _pro_for_user(session: Session, user: User) -> ServiceProfessional:
    pro = session.scalars(
        select(ServiceProfessional).where(ServiceProfessional.user_id == user.id)
    ).first()
    if pro is None:
        raise ToolError("no professional record for this user")
    return pro


# ─────────────────────────────────────────────── customer tools


def _search_services(session: Session, _user: User, args: dict[str, Any]) -> list[dict[str, Any]]:
    query = str(args.get("query") or "").strip().lower()
    stmt = select(Service).where(Service.is_active.is_(True))
    if query:
        like = f"%{query}%"
        stmt = stmt.where(
            or_(
                Service.name.ilike(like),
                Service.category.ilike(like),
                Service.description.ilike(like),
            )
        )
    rows = list(session.scalars(stmt))[:6]
    return [_ser_service(s) for s in rows]


def _list_my_requests(session: Session, user: User, _args: dict[str, Any]) -> list[dict[str, Any]]:
    rows = session.scalars(
        select(ServiceRequest)
        .where(ServiceRequest.customer_id == user.id)
        .order_by(ServiceRequest.id.desc())
    ).all()
    return [_ser_request(r) for r in list(rows)[:8]]


def _check_request_status(
    session: Session, user: User, args: dict[str, Any]
) -> dict[str, Any]:
    req_id = _require_int(args, "id")
    req = session.get(ServiceRequest, req_id)
    if req is None:
        raise ToolError(f"request #{req_id} not found")
    if req.customer_id != user.id:
        # Use the same message as "not found" so we don't leak existence of
        # other users' requests.
        raise ToolError(f"request #{req_id} not found")
    return _ser_request(req)


def _book_service(session: Session, user: User, args: dict[str, Any]) -> dict[str, Any]:
    if user.is_blocked:
        raise ToolError("your account is blocked; please contact support")
    service_id = _require_int(args, "service_id")
    address = _require_str(args, "address")
    pincode = _require_str(args, "pincode")
    scheduled_raw = _require_str(args, "scheduled_time")
    remarks = args.get("remarks")
    if remarks is not None and not isinstance(remarks, str):
        raise ToolError("remarks must be a string")

    try:
        scheduled_time = datetime.fromisoformat(scheduled_raw.replace("Z", "+00:00"))
    except ValueError as e:
        raise ToolError(
            "scheduled_time must be an ISO datetime like 2026-05-25T14:00"
        ) from e

    service = session.get(Service, service_id)
    if service is None:
        raise ToolError(f"service #{service_id} not found")
    if not service.is_active:
        raise ToolError(f"service '{service.name}' is no longer available")

    req = ServiceRequest(
        service_id=service_id,
        customer_id=user.id,
        scheduled_time=scheduled_time,
        address=address,
        pincode=pincode,
        remarks=remarks,
        date_of_request=date.today(),
        service_status=ServiceStatus.REQUESTED.value,
    )
    session.add(req)
    session.commit()
    session.refresh(req)
    return _ser_request(req)


# ─────────────────────────────────────────────── professional tools


def _list_pending_requests(
    session: Session, user: User, _args: dict[str, Any]
) -> list[dict[str, Any]]:
    pro = _pro_for_user(session, user)
    rows = session.scalars(
        select(ServiceRequest).where(
            ServiceRequest.service_id == pro.service_id,
            ServiceRequest.service_status == ServiceStatus.REQUESTED.value,
        )
    ).all()
    return [_ser_request(r) for r in rows]


def _accept_request(session: Session, user: User, args: dict[str, Any]) -> dict[str, Any]:
    pro = _pro_for_user(session, user)
    req_id = _require_int(args, "id")
    req = session.get(ServiceRequest, req_id)
    if req is None or req.service_id != pro.service_id:
        # Hide existence of requests outside this pro's category.
        raise ToolError(f"request #{req_id} not available to you")
    if req.service_status != ServiceStatus.REQUESTED.value:
        raise ToolError(
            f"request #{req_id} is already '{req.service_status}' and can't be accepted"
        )
    req.service_status = ServiceStatus.ACCEPTED.value
    req.professional_id = pro.id
    session.commit()
    session.refresh(req)
    return _ser_request(req)


def _weekly_summary(session: Session, user: User, _args: dict[str, Any]) -> dict[str, Any]:
    pro = _pro_for_user(session, user)
    cutoff = datetime.now() - timedelta(days=7)

    base = select(ServiceRequest).where(ServiceRequest.service_id == pro.service_id)

    completed = session.scalar(
        select(func.count()).select_from(
            base.where(
                ServiceRequest.service_status == ServiceStatus.COMPLETED.value,
                ServiceRequest.date_of_completion >= cutoff,
            ).subquery()
        )
    ) or 0
    in_flight = session.scalar(
        select(func.count()).select_from(
            base.where(
                ServiceRequest.service_status.in_(
                    [ServiceStatus.ACCEPTED.value, ServiceStatus.IN_PROGRESS.value]
                )
            ).subquery()
        )
    ) or 0
    pending = session.scalar(
        select(func.count()).select_from(
            base.where(ServiceRequest.service_status == ServiceStatus.REQUESTED.value).subquery()
        )
    ) or 0

    return {
        "completed_count": int(completed),
        "in_flight_count": int(in_flight),
        "pending_count": int(pending),
        "window_days": 7,
    }


# ─────────────────────────────────────────────── admin tools


def _get_metrics(session: Session, _user: User, _args: dict[str, Any]) -> dict[str, Any]:
    """Mirror /api/analytics/admin response shape exactly so the chat UI
    that consumes this can stay identical to the demo path."""
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
        .where(User.date_created.between(start_date, end_date), Role.name != "admin")
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


def _list_pending_approvals(
    session: Session, _user: User, _args: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = session.scalars(
        select(ServiceProfessional).where(ServiceProfessional.approval_status == "pending")
    ).all()
    return [_ser_pro_as_user(p) for p in rows]


def _approve_professional(
    session: Session, _user: User, args: dict[str, Any]
) -> dict[str, Any]:
    user_id = _require_int(args, "id")
    pro = session.scalars(
        select(ServiceProfessional).where(ServiceProfessional.user_id == user_id)
    ).first()
    if pro is None:
        raise ToolError(f"no professional record for user #{user_id}")
    pro.approval_status = "approved"
    session.commit()
    session.refresh(pro)
    return _ser_pro_as_user(pro)


# ─────────────────────────────────────────────── registry


SEARCH_SERVICES = Tool(
    name="search_services",
    description=(
        "Find active services in the catalogue matching a free-text query. "
        "Returns up to 6 results. Use this whenever the customer asks to find, "
        "browse, or book a service."
    ),
    params_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Free-text search. Matches name, category, and description. "
                    "Empty string browses all active services."
                ),
            }
        },
    },
    roles=frozenset({"user"}),
    run=_search_services,
)

LIST_MY_REQUESTS = Tool(
    name="list_my_requests",
    description="List the customer's most recent service requests (up to 8).",
    params_schema={"type": "object", "properties": {}},
    roles=frozenset({"user"}),
    run=_list_my_requests,
)

CHECK_REQUEST_STATUS = Tool(
    name="check_request_status",
    description="Get the full details of one of the customer's requests by id.",
    params_schema={
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "The numeric service-request id (e.g. 42).",
            }
        },
        "required": ["id"],
    },
    roles=frozenset({"user"}),
    run=_check_request_status,
)

BOOK_SERVICE = Tool(
    name="book_service",
    description=(
        "Create a new service request on behalf of the customer. Only call "
        "this after confirming the service_id (from search_services), the "
        "scheduled time, and the address with the user."
    ),
    params_schema={
        "type": "object",
        "properties": {
            "service_id": {"type": "integer", "description": "id from search_services"},
            "address": {"type": "string"},
            "pincode": {"type": "string"},
            "scheduled_time": {
                "type": "string",
                "description": "ISO datetime, e.g. '2026-05-25T14:00'.",
            },
            "remarks": {"type": "string"},
        },
        "required": ["service_id", "address", "pincode", "scheduled_time"],
    },
    roles=frozenset({"user"}),
    run=_book_service,
)

LIST_PENDING_REQUESTS = Tool(
    name="list_pending_requests",
    description=(
        "List service requests in the professional's category that haven't "
        "been claimed yet."
    ),
    params_schema={"type": "object", "properties": {}},
    roles=frozenset({"professional"}),
    run=_list_pending_requests,
)

ACCEPT_REQUEST = Tool(
    name="accept_request",
    description="Accept a pending request by id. The pro becomes assigned to it.",
    params_schema={
        "type": "object",
        "properties": {"id": {"type": "integer"}},
        "required": ["id"],
    },
    roles=frozenset({"professional"}),
    run=_accept_request,
)

WEEKLY_SUMMARY = Tool(
    name="weekly_summary",
    description=(
        "Summarize the professional's last 7 days: completed jobs, jobs in "
        "flight, and pending requests waiting in their category."
    ),
    params_schema={"type": "object", "properties": {}},
    roles=frozenset({"professional"}),
    run=_weekly_summary,
)

GET_METRICS = Tool(
    name="get_metrics",
    description=(
        "Fetch system-wide analytics: request trends, service popularity, "
        "user registrations, and professional approval-status counts."
    ),
    params_schema={"type": "object", "properties": {}},
    roles=frozenset({"admin"}),
    run=_get_metrics,
)

LIST_PENDING_APPROVALS = Tool(
    name="list_pending_approvals",
    description="List professional applicants whose approval_status is 'pending'.",
    params_schema={"type": "object", "properties": {}},
    roles=frozenset({"admin"}),
    run=_list_pending_approvals,
)

APPROVE_PROFESSIONAL = Tool(
    name="approve_professional",
    description="Mark a professional applicant as approved by their user id.",
    params_schema={
        "type": "object",
        "properties": {
            "id": {
                "type": "integer",
                "description": "The user id of the professional (not the ServiceProfessional id).",
            }
        },
        "required": ["id"],
    },
    roles=frozenset({"admin"}),
    run=_approve_professional,
)


TOOLS: dict[str, Tool] = {
    t.name: t
    for t in (
        SEARCH_SERVICES,
        LIST_MY_REQUESTS,
        CHECK_REQUEST_STATUS,
        BOOK_SERVICE,
        LIST_PENDING_REQUESTS,
        ACCEPT_REQUEST,
        WEEKLY_SUMMARY,
        GET_METRICS,
        LIST_PENDING_APPROVALS,
        APPROVE_PROFESSIONAL,
    )
}


def tools_for_role(role: str | None) -> list[Tool]:
    if not role:
        return []
    return [t for t in TOOLS.values() if role in t.roles]


def get_tool(name: str, role: str | None) -> Tool | None:
    """Return the tool if it exists *and* the role is allowed to call it.

    Returns None for both "no such tool" and "wrong role" so the runner
    can emit a single `forbidden` result either way.
    """
    tool = TOOLS.get(name)
    if tool is None:
        return None
    if not role or role not in tool.roles:
        return None
    return tool
