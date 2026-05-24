"""Tests for the agent layer.

Two surfaces are tested separately:
  * `backend.agent.tools` — pure DB-side tool implementations. Exercised with
    the `session` fixture directly; no LLM, no FastAPI app.
  * `backend.api.routers.agent` (later) — the SSE endpoint with Gemini mocked
    at the `backend.agent.gemini` boundary.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.agent.tools import (
    SEARCH_SERVICES,
    TOOLS,
    Tool,
    get_tool,
    tools_for_role,
)
from backend.core.config import get_settings
from backend.core.security import hash_password
from backend.models import Role, Service, User


@pytest.fixture
def customer(session: Session) -> User:
    role = Role(name="user", description="User")
    session.add(role)
    session.flush()
    u = User(
        email="cust@agent.x.com",
        password=hash_password("pw"),
        full_name="Agent Customer",
        address="a",
        pincode="0",
        fs_uniquifier="cust_agent",
    )
    u.roles.append(role)
    session.add(u)
    session.flush()
    return u


@pytest.fixture
def catalogue(session: Session) -> list[Service]:
    services = [
        Service(
            name="Kitchen Plumbing",
            base_price=499.0,
            time_required=60,
            description="Leaks, taps, drains",
            category="Plumbing",
        ),
        Service(
            name="Electrical Repair",
            base_price=399.0,
            time_required=45,
            description="Switchboards and wiring",
            category="Electrical",
        ),
        Service(
            name="Deep House Cleaning",
            base_price=999.0,
            time_required=180,
            description="Full home sanitization",
            category="Cleaning",
        ),
        # Inactive service should be filtered out by search.
        Service(
            name="Retired Carpet Cleaning",
            base_price=299.0,
            time_required=90,
            description="Discontinued service",
            category="Cleaning",
            is_active=False,
        ),
    ]
    session.add_all(services)
    session.flush()
    return services


def test_search_services_matches_name_and_category(
    session: Session, customer: User, catalogue: list[Service]
) -> None:
    result = SEARCH_SERVICES.run(session, customer, {"query": "plumb"})
    assert isinstance(result, list)
    assert len(result) == 1
    row = result[0]
    # Shape mirrors frontend/src/lib/genai.ts ServiceShape.
    expected_keys = {
        "id",
        "name",
        "category",
        "description",
        "base_price",
        "time_required",
        "is_active",
        "image_url",
        "rating",
        "review_count",
    }
    assert expected_keys <= set(row.keys())
    assert row["name"] == "Kitchen Plumbing"
    assert row["category"] == "Plumbing"


def test_search_services_excludes_inactive(
    session: Session, customer: User, catalogue: list[Service]
) -> None:
    result = SEARCH_SERVICES.run(session, customer, {"query": "cleaning"})
    names = [r["name"] for r in result]
    assert "Deep House Cleaning" in names
    assert "Retired Carpet Cleaning" not in names


def test_search_services_empty_query_returns_browse(
    session: Session, customer: User, catalogue: list[Service]
) -> None:
    result = SEARCH_SERVICES.run(session, customer, {"query": ""})
    # 3 active services seeded; all returned (cap is 6).
    assert len(result) == 3


def test_get_tool_respects_role_gate() -> None:
    # `search_services` is customer-only.
    assert get_tool("search_services", "user") is SEARCH_SERVICES
    assert get_tool("search_services", "professional") is None
    assert get_tool("search_services", "admin") is None
    assert get_tool("nope", "user") is None
    assert get_tool("search_services", None) is None


def test_tools_for_role_filters() -> None:
    customer_tools = tools_for_role("user")
    assert SEARCH_SERVICES in customer_tools
    assert all(isinstance(t, Tool) for t in customer_tools)
    assert tools_for_role(None) == []


def test_tool_registry_contains_search_services() -> None:
    assert "search_services" in TOOLS


# ───────────────────────────────────────────────────── SSE endpoint


def _login(client: TestClient, email: str) -> None:
    resp = client.post("/api/auth/login", json={"email": email, "password": "pw"})
    assert resp.status_code == 200, resp.text


def _parse_sse(body: str) -> list[tuple[str, str]]:
    """Split an SSE body into (event, data) frames."""
    frames: list[tuple[str, str]] = []
    for chunk in body.split("\n\n"):
        if not chunk.strip():
            continue
        event = ""
        data = ""
        for line in chunk.splitlines():
            if line.startswith("event: "):
                event = line[len("event: ") :]
            elif line.startswith("data: "):
                data = line[len("data: ") :]
        frames.append((event, data))
    return frames


def _script_gemini(turns: list[list]):
    """Build a fake `stream_turn` async iterator that replays `turns`.

    Each entry in `turns` is a list of events (text strings or
    `GeminiFunctionCall` instances) that one Gemini turn would yield, in
    order. The runner calls `stream_turn` once per loop iteration, so
    `len(turns)` should equal the expected number of model turns.
    """
    from backend.agent.gemini import GeminiFunctionCall, GeminiTextChunk

    calls = {"i": 0}

    async def fake(**_kwargs):
        idx = calls["i"]
        calls["i"] += 1
        for item in turns[idx]:
            if isinstance(item, str):
                yield GeminiTextChunk(delta=item)
            elif isinstance(item, GeminiFunctionCall):
                yield item
            else:
                raise TypeError(f"unsupported scripted event: {item!r}")

    return fake


def test_chat_endpoint_streams_gemini_text(
    client: TestClient, session: Session, customer: User, monkeypatch
) -> None:
    # Pretend a Gemini key is configured so the route doesn't 503.
    monkeypatch.setattr(get_settings(), "gemini_api_key", "test-key", raising=False)
    # Replace the real Gemini call with a scripted async iterator.
    from backend.agent import gemini

    monkeypatch.setattr(gemini, "stream_turn", _script_gemini([["Hello ", "world"]]))

    _login(client, "cust@agent.x.com")
    resp = client.post(
        "/api/agent/chat",
        json={"model_id": "gemini-2.5-pro", "messages": [], "message": "hi"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    frames = _parse_sse(resp.text)
    types = [t for t, _ in frames]
    # Runner emits: Thinking → Writing → text → text → done.
    assert types == ["state", "state", "text", "text", "done"]
    import json as _json
    assert _json.loads(frames[0][1])["status"] == "Thinking"
    assert _json.loads(frames[1][1])["status"] == "Writing"
    assert _json.loads(frames[2][1])["delta"] == "Hello "
    assert _json.loads(frames[3][1])["delta"] == "world"


def test_chat_endpoint_runs_function_call_loop(
    client: TestClient, session: Session, customer: User, catalogue, monkeypatch
) -> None:
    """Two-turn agent loop: model asks for search_services, runner executes
    it against the real DB, model writes a follow-up. Verify both turns
    surface in the SSE stream with proper tool_call/tool_result framing."""
    monkeypatch.setattr(get_settings(), "gemini_api_key", "test-key", raising=False)
    from backend.agent import gemini

    monkeypatch.setattr(
        gemini,
        "stream_turn",
        _script_gemini(
            [
                # Turn 1: a small narration + a tool request.
                [
                    "Looking that up… ",
                    gemini.GeminiFunctionCall(name="search_services", args={"query": "plumb"}),
                ],
                # Turn 2: model wraps up after seeing the tool result.
                ["Found **Kitchen Plumbing** for ₹499."],
            ]
        ),
    )

    _login(client, "cust@agent.x.com")
    resp = client.post(
        "/api/agent/chat",
        json={"model_id": "gemini-2.5-pro", "messages": [], "message": "find me a plumber"},
    )
    assert resp.status_code == 200

    frames = _parse_sse(resp.text)
    types = [t for t, _ in frames]
    # Expected ordering:
    #   state(Thinking) → state(Writing) → text("Looking that up… ")
    #   → state(Searching) → tool_call → tool_result
    #   → state(Writing) → text("Found Kitchen Plumbing…")
    #   → done
    assert types.count("tool_call") == 1
    assert types.count("tool_result") == 1
    assert types[-1] == "done"

    import json as _json

    tool_call_idx = types.index("tool_call")
    tool_result_idx = types.index("tool_result")
    assert tool_call_idx < tool_result_idx
    call = _json.loads(frames[tool_call_idx][1])
    result = _json.loads(frames[tool_result_idx][1])
    assert call["name"] == "search_services"
    assert call["args"] == {"query": "plumb"}
    assert call["id"] == result["id"]  # the ids match
    assert result["ok"] is True
    # The real search ran — result is a list of dicts.
    assert isinstance(result["data"], list)
    assert any(row["name"] == "Kitchen Plumbing" for row in result["data"])


def test_chat_endpoint_forbids_wrong_role_tool(
    client: TestClient, session: Session, customer: User, monkeypatch
) -> None:
    """Customer session, model tries to call an admin-only tool. Runner
    must refuse and emit `ok: false, data: "forbidden"`."""
    monkeypatch.setattr(get_settings(), "gemini_api_key", "test-key", raising=False)
    from backend.agent import gemini

    monkeypatch.setattr(
        gemini,
        "stream_turn",
        _script_gemini(
            [
                [gemini.GeminiFunctionCall(name="approve_professional", args={"id": 1})],
                ["Sorry, I can't do that."],
            ]
        ),
    )
    _login(client, "cust@agent.x.com")
    resp = client.post(
        "/api/agent/chat",
        json={"model_id": "gemini-2.5-pro", "messages": [], "message": "approve user 1"},
    )
    assert resp.status_code == 200

    frames = _parse_sse(resp.text)
    import json as _json

    tool_result = next((f for f in frames if f[0] == "tool_result"), None)
    assert tool_result is not None
    payload = _json.loads(tool_result[1])
    assert payload["ok"] is False
    assert payload["data"] == "forbidden"


def test_chat_endpoint_503s_without_key(client: TestClient, customer: User, monkeypatch) -> None:
    # No server fallback + no user-stored encrypted key on `customer` → 503.
    monkeypatch.setattr(get_settings(), "gemini_api_key", "", raising=False)
    _login(client, "cust@agent.x.com")
    resp = client.post(
        "/api/agent/chat",
        json={"model_id": "", "messages": [], "message": "hello"},
    )
    assert resp.status_code == 503
    assert "gemini api key" in resp.json()["detail"].lower()


# ───────────────────────────────────────────────────── BYOK endpoints


def _set_encryption_key(monkeypatch) -> None:
    """Generate a fresh Fernet key for the test process."""
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode()
    monkeypatch.setattr(get_settings(), "gemini_key_encryption_key", key, raising=False)


def test_gemini_key_set_then_status_then_delete(
    client: TestClient, customer: User, monkeypatch
) -> None:
    _set_encryption_key(monkeypatch)
    _login(client, "cust@agent.x.com")

    # Initially: not configured.
    r = client.get("/api/users/me/gemini-key")
    assert r.status_code == 200
    assert r.json() == {"configured": False}

    # Set.
    r = client.put(
        "/api/users/me/gemini-key",
        json={"api_key": "AIzaSyFAKEKEYFAKEKEYFAKEKEYFAKEKEYFAKE"},
    )
    assert r.status_code == 200, r.text
    assert r.json() == {"configured": True}

    # Status now true.
    r = client.get("/api/users/me/gemini-key")
    assert r.json() == {"configured": True}

    # Delete.
    r = client.delete("/api/users/me/gemini-key")
    assert r.status_code == 204
    r = client.get("/api/users/me/gemini-key")
    assert r.json() == {"configured": False}


def test_chat_uses_user_encrypted_key_over_server_fallback(
    client: TestClient, customer: User, monkeypatch
) -> None:
    """When the user has a stored key, the runner is invoked with it (not the
    server fallback). We assert by capturing the api_key passed into runner.run."""
    _set_encryption_key(monkeypatch)
    # Set a server fallback that should be ignored.
    monkeypatch.setattr(get_settings(), "gemini_api_key", "server-fallback-key", raising=False)

    _login(client, "cust@agent.x.com")
    client.put(
        "/api/users/me/gemini-key",
        json={"api_key": "AIzaSyUSERSPECIFICKEYUSERSPECIFICKEY"},
    )

    captured: dict[str, str | None] = {}

    async def fake_run(**kwargs):
        captured["api_key"] = kwargs.get("gemini_api_key")
        yield {"type": "done"}

    from backend.api.routers import agent as agent_router

    monkeypatch.setattr(agent_router.runner, "run", fake_run)

    resp = client.post(
        "/api/agent/chat",
        json={"model_id": "", "messages": [], "message": "hello"},
    )
    assert resp.status_code == 200
    assert captured["api_key"] == "AIzaSyUSERSPECIFICKEYUSERSPECIFICKEY"
