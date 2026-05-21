from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import hash_password
from backend.models import (
    Role,
    Service,
    ServiceProfessional,
    ServiceRequest,
    User,
)


@pytest.fixture
def world(session: Session):
    """Seed a basic world: admin + customer + professional, all bcrypt-hashed."""
    admin_role = Role(name="admin", description="Administrator")
    user_role = Role(name="user", description="User")
    pro_role = Role(name="professional", description="Professional")
    session.add_all([admin_role, user_role, pro_role])
    session.flush()

    service = Service(name="Plumbing", base_price=200.0, time_required=60)
    session.add(service)
    session.flush()

    admin = User(
        email="admin@x.com",
        password=hash_password("admin"),
        full_name="Admin",
        address="a",
        pincode="0",
        fs_uniquifier="admin_u",
    )
    admin.roles.append(admin_role)

    customer = User(
        email="cust@x.com",
        password=hash_password("pw"),
        full_name="Customer",
        address="a",
        pincode="0",
        fs_uniquifier="cust_u",
    )
    customer.roles.append(user_role)

    pro_user = User(
        email="pro@x.com",
        password=hash_password("pw"),
        full_name="Pro",
        address="a",
        pincode="0",
        fs_uniquifier="pro_u",
    )
    pro_user.roles.append(pro_role)

    session.add_all([admin, customer, pro_user])
    session.flush()

    pro_record = ServiceProfessional(
        user_id=pro_user.id,
        service_id=service.id,
        approval_status="approved",
        experience=5,
        description="experienced",
    )
    session.add(pro_record)
    session.flush()

    return {
        "admin": admin,
        "customer": customer,
        "pro_user": pro_user,
        "pro_record": pro_record,
        "service": service,
    }


def _login(client: TestClient, email: str, password: str = "pw") -> None:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text


def test_customer_creates_request(client: TestClient, world):
    _login(client, "cust@x.com")
    resp = client.post(
        "/api/requests",
        json={
            "service_id": world["service"].id,
            "scheduled_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            "address": "123 Test St",
            "pincode": "00000",
            "remarks": "Fix the sink",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["service_status"] == "requested"
    assert body["customer_id"] == world["customer"].id


def test_blocked_user_cannot_log_in(client: TestClient, world, session: Session):
    world["customer"].is_blocked = True
    session.flush()
    resp = client.post("/api/auth/login", json={"email": "cust@x.com", "password": "pw"})
    assert resp.status_code == 403


def test_customer_sees_only_own_requests(client: TestClient, world, session: Session):
    other_customer = User(
        email="cust2@x.com",
        password=hash_password("pw"),
        full_name="Other",
        address="a",
        pincode="0",
        fs_uniquifier="cust2_u",
    )
    other_customer.roles.append(world["customer"].roles[0])
    session.add(other_customer)
    session.flush()

    session.add_all(
        [
            ServiceRequest(
                service_id=world["service"].id,
                customer_id=world["customer"].id,
                scheduled_time=datetime.now(),
                address="a",
                pincode="0",
                date_of_request=datetime.now().date(),
                service_status="requested",
            ),
            ServiceRequest(
                service_id=world["service"].id,
                customer_id=other_customer.id,
                scheduled_time=datetime.now(),
                address="b",
                pincode="0",
                date_of_request=datetime.now().date(),
                service_status="requested",
            ),
        ]
    )
    session.flush()

    _login(client, "cust@x.com")
    body = client.get("/api/requests").json()
    assert len(body) == 1
    assert body[0]["customer_id"] == world["customer"].id


def test_professional_accepts_request(client: TestClient, world, session: Session):
    req = ServiceRequest(
        service_id=world["service"].id,
        customer_id=world["customer"].id,
        scheduled_time=datetime.now(),
        address="a",
        pincode="0",
        date_of_request=datetime.now().date(),
        service_status="requested",
    )
    session.add(req)
    session.flush()

    _login(client, "pro@x.com")
    resp = client.put(f"/api/requests/{req.id}", json={"service_status": "accepted"})
    assert resp.status_code == 200
    assert resp.json()["service_status"] == "accepted"


def test_customer_cannot_set_invalid_status(client: TestClient, world, session: Session):
    req = ServiceRequest(
        service_id=world["service"].id,
        customer_id=world["customer"].id,
        scheduled_time=datetime.now(),
        address="a",
        pincode="0",
        date_of_request=datetime.now().date(),
        service_status="requested",
    )
    session.add(req)
    session.flush()

    _login(client, "cust@x.com")
    resp = client.put(f"/api/requests/{req.id}", json={"service_status": "completed"})
    assert resp.status_code == 400


def test_admin_creates_service_then_deletes(client: TestClient, world):
    _login(client, "admin@x.com", "admin")
    resp = client.post(
        "/api/services",
        json={"name": "Painting", "base_price": 150.0, "time_required": 90, "description": "x"},
    )
    assert resp.status_code == 201
    service_id = resp.json()["id"]

    resp = client.delete(f"/api/services/{service_id}")
    assert resp.status_code == 204


def test_non_admin_cannot_create_service(client: TestClient, world):
    _login(client, "cust@x.com")
    resp = client.post(
        "/api/services",
        json={"name": "X", "base_price": 10.0, "time_required": 30, "description": "x"},
    )
    assert resp.status_code == 403


def test_admin_blocks_user(client: TestClient, world):
    _login(client, "admin@x.com", "admin")
    resp = client.put(f"/api/users/{world['customer'].id}", json={"is_blocked": True})
    assert resp.status_code == 200
    assert resp.json()["is_blocked"] is True


def test_admin_approves_professional(client: TestClient, world):
    _login(client, "admin@x.com", "admin")
    resp = client.put(
        f"/api/users/{world['pro_user'].id}", json={"approval_status": "approved"}
    )
    assert resp.status_code == 200
    assert resp.json()["approval_status"] == "approved"


def test_admin_approval_rejected_for_non_professional(client: TestClient, world):
    _login(client, "admin@x.com", "admin")
    resp = client.put(
        f"/api/users/{world['customer'].id}", json={"approval_status": "approved"}
    )
    assert resp.status_code == 400
