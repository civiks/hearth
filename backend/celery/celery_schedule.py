from celery.schedules import crontab

from backend.celery.celery_factory import celery_app


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from backend.celery.tasks import generate_monthly_report, send_daily_reminders

    sender.add_periodic_task(
        crontab(hour=18, minute=0),
        send_daily_reminders.s(),
        name="send-daily-reminders",
    )
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=9, minute=0),
        generate_monthly_report.s(),
        name="generate-monthly-report",
    )
