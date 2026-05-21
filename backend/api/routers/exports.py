from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from backend.celery.tasks import (
    create_csv,
    generate_activity_report,
    generate_monthly_report,
    send_daily_reminders,
    test_redis,
)
from backend.core.security import AdminUser, CurrentUser

router = APIRouter(prefix="/api", tags=["exports"])


@router.post("/export-service-requests", status_code=status.HTTP_202_ACCEPTED)
def export_requests(_admin: AdminUser):
    task = create_csv.delay()
    return {"task_id": task.id}


@router.get("/export-status/{task_id}")
def export_status(task_id: str, _admin: AdminUser):
    task = AsyncResult(task_id)
    payload = {"status": task.state, "current": 0 if task.state == "PENDING" else 1, "total": 1}
    if task.state == "FAILURE":
        payload["error"] = str(task.info)
    elif task.state not in ("PENDING", "FAILURE") and task.info:
        payload["filename"] = task.info
    return payload


@router.get("/download-export/{filename}")
def download_export(filename: str, _admin: AdminUser):
    from backend.celery.tasks import EXPORTS_DIR

    path = EXPORTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="file not found")
    return FileResponse(path, filename=filename, media_type="text/csv")


@router.get("/test-redis", status_code=status.HTTP_202_ACCEPTED)
def test_redis_route(_user: CurrentUser):
    task = test_redis.delay()
    return {"task_id": task.id}


@router.post("/trigger-daily-reminders")
def trigger_daily_reminders(_admin: AdminUser):
    send_daily_reminders.delay()
    return {"message": "daily reminders triggered"}


@router.post("/trigger-monthly-reports")
def trigger_monthly_reports(_admin: AdminUser):
    generate_monthly_report.delay()
    return {"message": "monthly reports triggered"}


@router.post("/trigger-activity-reports")
def trigger_activity_reports(_admin: AdminUser):
    generate_activity_report.delay()
    return {"message": "activity reports triggered"}
