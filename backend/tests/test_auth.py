from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.security import hash_password
from backend.models import Role, Service, User


def _make_user(session: Session, *, email: str, password: str, role_name: str) -> User:
    role = Role(name=role_name, description=role_name)
    session.add(role)
    session.flush()
    user = User(
        email=email,
        password=hash_password(password),
        full_name="Test User",
        address="addr",
        pincode="00000",
        fs_uniquifier=email,
    )
    user.roles.append(role)
    session.add(user)
    session.flush()
    return user


def test_login_success_sets_cookie(client: TestClient, session: Session):
    _make_user(session, email="alice@example.com", password="secret123", role_name="user")
    resp = client.post(
        "/api/auth/login", json={"email": "alice@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "user"
    assert "auth_token" in resp.cookies


def test_login_wrong_password_401(client: TestClient, session: Session):
    _make_user(session, email="bob@example.com", password="secret123", role_name="user")
    resp = client.post(
        "/api/auth/login", json={"email": "bob@example.com", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_me_requires_auth(client: TestClient):
    assert client.get("/api/auth/me").status_code == 401


def test_login_then_me(client: TestClient, session: Session):
    _make_user(session, email="carol@example.com", password="hunter22", role_name="user")
    client.post(
        "/api/auth/login", json={"email": "carol@example.com", "password": "hunter22"}
    )
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "carol@example.com"


def test_register_customer(client: TestClient, session: Session):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "newcust@example.com",
            "password": "pw1234",
            "role": "user",
            "full_name": "New Customer",
            "address": "1 Main St",
            "pincode": "560001",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "user"


def test_register_professional_requires_service(client: TestClient, session: Session):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "newpro@example.com",
            "password": "pw1234",
            "role": "professional",
            "full_name": "New Pro",
            "address": "1 Main St",
            "pincode": "560001",
        },
    )
    assert resp.status_code == 400


def test_register_professional_success(client: TestClient, session: Session):
    session.add(Service(name="Plumbing", base_price=180.0, time_required=90))
    session.flush()
    service_id = session.query(Service).first().id

    resp = client.post(
        "/api/auth/register",
        json={
            "email": "pro2@example.com",
            "password": "pw1234",
            "role": "professional",
            "full_name": "Pro Two",
            "address": "1 Main St",
            "pincode": "560001",
            "service_id": service_id,
            "experience": 3,
            "description": "Skilled plumber",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "professional"
    assert body["service_id"] == service_id
    assert body["approval_status"] == "pending"


def test_register_duplicate_email_409(client: TestClient, session: Session):
    _make_user(session, email="dup@example.com", password="x", role_name="user")
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "dup@example.com",
            "password": "pw1234",
            "role": "user",
            "full_name": "Dup",
            "address": "x",
            "pincode": "00000",
        },
    )
    assert resp.status_code == 409


def test_logout_clears_cookie(client: TestClient, session: Session):
    _make_user(session, email="eve@example.com", password="pw", role_name="user")
    client.post("/api/auth/login", json={"email": "eve@example.com", "password": "pw"})
    resp = client.post("/api/auth/logout")
    assert resp.status_code == 204
    assert client.get("/api/auth/me").status_code == 401
