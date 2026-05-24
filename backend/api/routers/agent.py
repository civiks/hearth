"""POST /api/agent/chat — Server-Sent Events stream of `AgentEvent`s.

The route is the thinnest possible adapter: validate the body, look up the
caller's role, hand everything to `backend.agent.runner.run()`, and SSE-encode
each event it yields. All AI logic lives in the runner so it can be unit-
tested without spinning up FastAPI.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Annotated, Literal

from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.agent import runner
from backend.core import crypto
from backend.core.config import get_settings
from backend.core.db import get_session
from backend.core.security import CurrentUser
from backend.models import User

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _resolve_gemini_key(user: User, server_fallback: str) -> str:
    """Return the API key to use for this request.

    Per-user encrypted key takes precedence; we fall back to the server-wide
    `gemini_api_key` setting (useful for local dev / single-user setups).
    Returns "" if neither is available — caller turns that into a 503.
    """
    enc = user.gemini_api_key_encrypted
    if enc:
        try:
            decrypted = crypto.decrypt(enc).strip()
            if decrypted:
                return decrypted
        except (InvalidToken, crypto.EncryptionUnavailable):
            # Stored token can't be decrypted — either the encryption key
            # rotated or it was never set. Fall through to the server key
            # rather than 500; user can re-paste via Settings.
            pass
    return server_fallback.strip()


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class ChatRequest(BaseModel):
    # Frontend lets the user pick between Gemini variants — we forward it.
    # Defaults to the configured fallback if unknown.
    model_id: str = Field(default="")
    # Prior conversation turns. The latest user `message` is sent separately
    # so it's obvious where the new input is.
    messages: list[ChatTurn] = Field(default_factory=list)
    message: str = Field(min_length=1, max_length=4000)


def _sse_format(event: dict) -> bytes:
    """Encode a single dict as one SSE frame.

    Frame shape:
      event: <type>\n
      data: <json>\n
      \n
    The trailing blank line is the SSE record separator.
    """
    event_type = event.get("type", "message")
    # Strip `type` from data — it's already in the event line — to keep frames
    # compact. The client uses the event-line for dispatch anyway.
    payload = {k: v for k, v in event.items() if k != "type"}
    data = json.dumps(payload, separators=(",", ":"))
    return f"event: {event_type}\ndata: {data}\n\n".encode()


def _user_role(user) -> str | None:
    return user.roles[0].name if user.roles else None


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
) -> StreamingResponse:
    """SSE stream of AgentEvents.

    The key resolution order is: user's encrypted key on the User row
    (BYOK, set via `PUT /api/users/me/gemini-key`), then `settings.gemini_api_key`
    as a server-wide fallback. Without either, we 503 with a clear message.
    """
    settings = get_settings()
    effective_key = _resolve_gemini_key(user, settings.gemini_api_key)
    if not effective_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Add your Gemini API key to start chatting.",
        )

    role = _user_role(user)
    model_id = payload.model_id or settings.gemini_default_model

    async def event_stream() -> AsyncIterator[bytes]:
        async for event in runner.run(
            session=session,
            user=user,
            role=role,
            history=[m.model_dump() for m in payload.messages],
            message=payload.message,
            model_id=model_id,
            gemini_api_key=effective_key,
        ):
            yield _sse_format(event)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            # Disable proxy buffering so chunks reach the client in real time.
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
