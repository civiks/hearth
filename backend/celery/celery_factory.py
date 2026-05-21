from celery import Celery

from backend.core.config import get_settings


def make_celery() -> Celery:
    settings = get_settings()
    celery_app = Celery(
        "hearth",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["backend.celery.tasks"],
    )
    celery_app.conf.update(
        timezone="Asia/Kolkata",
        broker_connection_retry_on_startup=True,
        task_always_eager=settings.celery_eager,
        task_eager_propagates=True,
    )
    return celery_app


celery_app = make_celery()

# Wire periodic tasks (previously dead code — never imported anywhere)
from backend.celery import celery_schedule  # noqa: F401, E402
