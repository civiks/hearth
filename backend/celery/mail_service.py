import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.core.config import get_settings


def send_email(to: str, subject: str, content: str) -> bool:
    settings = get_settings()

    message = MIMEMultipart()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject

    stripped = content.strip()
    is_html = stripped.startswith("<!DOCTYPE html>") or stripped.startswith("<html>")
    message.attach(MIMEText(content, "html" if is_html else "plain"))

    with smtplib.SMTP(host=settings.smtp_host, port=settings.smtp_port) as server:
        server.send_message(message)
    return True
