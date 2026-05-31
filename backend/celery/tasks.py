from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.celery.mail_service import send_email
from backend.core.db import session_scope
from backend.models import Role, ServiceProfessional, ServiceRequest, User

EXPORTS_DIR = Path(__file__).parent / "user-downloads"


@shared_task(bind=True, ignore_result=False)
def create_csv(self):
    """Export all service requests to CSV. Returns the filename."""
    EXPORTS_DIR.mkdir(exist_ok=True)
    filename = f"service_requests_{self.request.id}.csv"
    path = EXPORTS_DIR / filename

    with session_scope() as session:
        rows = session.scalars(select(ServiceRequest)).all()
        df = pd.DataFrame(
            [
                {col.name: getattr(row, col.name) for col in ServiceRequest.__table__.columns}
                for row in rows
            ]
        )
        df.to_csv(path, index=False)
    return filename


@shared_task(bind=True, ignore_result=True, max_retries=3, name="email_reminder")
def email_reminder(self, to: str, subject: str, content: str) -> None:
    try:
        send_email(to, subject, content)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * 2 ** self.request.retries) from None


@shared_task(bind=True, ignore_result=True, max_retries=3, name="send_daily_reminders")
def send_daily_reminders(self) -> None:
    with session_scope() as session:
        professionals = session.scalars(
            select(ServiceProfessional)
            .options(selectinload(ServiceProfessional.user))
            .join(ServiceRequest, ServiceProfessional.service_id == ServiceRequest.service_id)
            .where(ServiceRequest.service_status == "requested")
            .distinct()
        ).all()

        for professional in professionals:
            subject = "Pending Service Requests - Action Required"
            content = (
                f"Hello {professional.user.full_name},\n\n"
                "You have pending service requests that require your attention.\n"
                "Please login to your dashboard to accept or reject these requests.\n\n"
                "Best regards,\nhearth Team"
            )
            try:
                send_email(professional.user.email, subject, content)
            except Exception as exc:
                raise self.retry(exc=exc, countdown=60 * 2 ** self.request.retries) from None


@shared_task(bind=True, ignore_result=True, max_retries=3, name="generate_monthly_report")
def generate_monthly_report(self) -> None:
    today = datetime.now()
    first_of_month = datetime(today.year, today.month, 1)
    last_month_end = first_of_month - timedelta(days=1)
    last_month_start = datetime(last_month_end.year, last_month_end.month, 1)

    with session_scope() as session:
        customers = session.scalars(
            select(User).join(User.roles).where(Role.name == "user")
        ).all()

        customer_ids = [c.id for c in customers]
        all_requests = session.scalars(
            select(ServiceRequest)
            .options(selectinload(ServiceRequest.service))
            .where(
                ServiceRequest.customer_id.in_(customer_ids),
                ServiceRequest.date_of_request >= last_month_start.date(),
                ServiceRequest.date_of_request <= last_month_end.date(),
            )
        ).all()

        by_customer: dict[int, list] = defaultdict(list)
        for r in all_requests:
            by_customer[r.customer_id].append(r)

        for customer in customers:
            requests = by_customer[customer.id]

            total = len(requests)
            completed = sum(1 for r in requests if r.service_status == "completed")
            pending = sum(1 for r in requests if r.service_status == "requested")
            cancelled = sum(1 for r in requests if r.service_status == "cancelled")

            items_html = "".join(
                f"<li>{r.service.name} (ID {r.id}) — {r.service_status} — "
                f"{r.date_of_request.strftime('%Y-%m-%d')}</li>"
                for r in requests
            ) or "<li>No service requests for this period.</li>"

            html = (
                f"<!DOCTYPE html><html><body>"
                f"<h2>Monthly Activity Report — {last_month_end.strftime('%B %Y')}</h2>"
                f"<p>Dear {customer.full_name},</p>"
                f"<p>Total: {total}, Completed: {completed}, "
                f"Pending: {pending}, Cancelled: {cancelled}</p>"
                f"<ul>{items_html}</ul>"
                f"<p>Best regards,<br>hearth Team</p>"
                f"</body></html>"
            )

            try:
                send_email(
                    customer.email,
                    f"Monthly Activity Report — {last_month_end.strftime('%B %Y')}",
                    html,
                )
            except Exception as exc:
                raise self.retry(exc=exc, countdown=60 * 2 ** self.request.retries) from None


@shared_task(name="test_redis")
def test_redis() -> str:
    return "Redis connection working!"


@shared_task(bind=True, ignore_result=True, max_retries=3, name="generate_activity_report")
def generate_activity_report(self) -> None:
    with session_scope() as session:
        customers = session.scalars(
            select(User).join(User.roles).where(Role.name == "user")
        ).all()

        customer_ids = [c.id for c in customers]
        all_requests = session.scalars(
            select(ServiceRequest)
            .options(selectinload(ServiceRequest.service))
            .where(ServiceRequest.customer_id.in_(customer_ids))
            .order_by(ServiceRequest.date_of_request.desc())
        ).all()

        by_customer: dict[int, list] = defaultdict(list)
        for r in all_requests:
            by_customer[r.customer_id].append(r)

        for customer in customers:
            requests = by_customer[customer.id]

            total = len(requests)
            completed = sum(1 for r in requests if r.service_status == "completed")
            pending = sum(1 for r in requests if r.service_status == "requested")
            in_progress = sum(1 for r in requests if r.service_status == "in_progress")
            cancelled = sum(1 for r in requests if r.service_status == "cancelled")

            items_html = "".join(
                f"<li>{r.service.name} — {r.service_status.upper()} — "
                f"{r.date_of_request.strftime('%Y-%m-%d')}</li>"
                for r in requests
            ) or "<li>No service requests found.</li>"

            html = (
                f"<!DOCTYPE html><html><body>"
                f"<h2>Service Activity Report</h2>"
                f"<p>Dear {customer.full_name},</p>"
                f"<p>Total: {total}, Completed: {completed}, In Progress: {in_progress}, "
                f"Pending: {pending}, Cancelled: {cancelled}</p>"
                f"<ul>{items_html}</ul>"
                f"<p>Best regards,<br>hearth Team</p>"
                f"</body></html>"
            )

            try:
                send_email(
                    customer.email,
                    f"Service Activity Report — {datetime.now().strftime('%B %d, %Y')}",
                    html,
                )
            except Exception as exc:
                raise self.retry(exc=exc, countdown=60 * 2 ** self.request.retries) from None
