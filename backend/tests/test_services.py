from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import Service


def test_list_services_empty(client: TestClient):
    response = client.get("/api/services")
    assert response.status_code == 200
    assert response.json() == []


def test_list_services_returns_active_only(client: TestClient, session: Session):
    session.add_all(
        [
            Service(name="Plumbing", base_price=180.0, time_required=90, is_active=True),
            Service(name="Carpet Cleaning", base_price=300.0, time_required=120, is_active=False),
        ]
    )
    session.flush()

    response = client.get("/api/services")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Plumbing"
    assert body[0]["base_price"] == 180.0


def test_healthz(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
