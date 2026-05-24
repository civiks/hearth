"""Thin async wrapper around the `google-genai` SDK.

The runner owns the conversation state and the agent loop. This module just
turns SDK chunks into a small typed event union and exposes helpers for
building the `Content`/`Part` objects that go back into the next turn.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from google import genai
from google.genai import types as gtypes

from backend.agent.tools import Tool
from backend.core.config import get_settings

# ─────────────────────────────────────────────── internal event shape


@dataclass
class GeminiTextChunk:
    """A streamed text delta from the model."""

    delta: str


@dataclass
class GeminiFunctionCall:
    """The model wants to call a tool. Args are already JSON-decoded."""

    name: str
    args: dict[str, Any]


GeminiEvent = GeminiTextChunk | GeminiFunctionCall


# ─────────────────────────────────────────────── client


# Cache of Clients keyed by API key — supports BYOK where different
# requests may bring different keys. Each Client is cheap to construct
# (it just stashes the key + creates an httpx session), so the cache is
# more about avoiding redundant work than performance-critical.
_clients: dict[str, genai.Client] = {}


def _get_client(api_key: str | None = None) -> genai.Client:
    """Return a Client for `api_key`, falling back to `settings.gemini_api_key`."""
    key = (api_key or "").strip() or get_settings().gemini_api_key
    if not key:
        raise RuntimeError("gemini_api_key is not set")
    if key not in _clients:
        _clients[key] = genai.Client(api_key=key)
    return _clients[key]


# ─────────────────────────────────────────────── Content builders
#
# The runner uses these to thread the conversation across turns. Keeping
# the SDK type imports contained in this module lets the runner stay
# free of Gemini-specific types.


def user_text(text: str) -> gtypes.Content:
    return gtypes.Content(role="user", parts=[gtypes.Part(text=text)])


def model_turn(
    text: str | None = None,
    function_calls: list[GeminiFunctionCall] | None = None,
) -> gtypes.Content:
    """Reconstruct the model's last turn so Gemini sees its own prior output.

    A model turn may contain both prose and a function-call request; we
    preserve both so the next turn's context is faithful.
    """
    parts: list[gtypes.Part] = []
    if text:
        parts.append(gtypes.Part(text=text))
    for fc in function_calls or []:
        parts.append(
            gtypes.Part(function_call=gtypes.FunctionCall(name=fc.name, args=fc.args))
        )
    return gtypes.Content(role="model", parts=parts)


def function_response(name: str, response: dict[str, Any]) -> gtypes.Content:
    """A `user`-role turn carrying a function execution result.

    Gemini uses the `user` role for function responses (no separate
    `function` role). The `response` dict shape is whatever the model
    declared in the FunctionDeclaration's return schema — Gemini treats
    it as opaque JSON.
    """
    return gtypes.Content(
        role="user",
        parts=[gtypes.Part(function_response=gtypes.FunctionResponse(name=name, response=response))],
    )


def history_to_contents(history: list[dict[str, str]]) -> list[gtypes.Content]:
    """Map our `{role, text}` chat history to Gemini Contents.

    Skips empty turns so we don't 400.
    """
    contents: list[gtypes.Content] = []
    for m in history:
        text = (m.get("text") or "").strip()
        if not text:
            continue
        role = "model" if m["role"] == "assistant" else "user"
        contents.append(gtypes.Content(role=role, parts=[gtypes.Part(text=text)]))
    return contents


def _build_tool_decl(tool: Tool) -> gtypes.FunctionDeclaration:
    return gtypes.FunctionDeclaration(
        name=tool.name,
        description=tool.description,
        parameters=tool.params_schema,
    )


# ─────────────────────────────────────────────── streaming entry point


async def stream_turn(
    *,
    model_id: str,
    contents: list[gtypes.Content],
    tools: list[Tool],
    system_prompt: str,
    api_key: str | None = None,
) -> AsyncIterator[GeminiEvent]:
    """Stream a single Gemini turn over a pre-built conversation.

    Yields `GeminiTextChunk` for each text delta and `GeminiFunctionCall`
    when the model requests a tool. The runner is responsible for executing
    the tool and constructing the next turn's `contents`.

    `api_key` overrides `settings.gemini_api_key` — used by the BYOK route.
    """
    client = _get_client(api_key)

    config_kwargs: dict[str, Any] = {"system_instruction": system_prompt}
    if tools:
        config_kwargs["tools"] = [
            gtypes.Tool(function_declarations=[_build_tool_decl(t) for t in tools])
        ]
        # Disable the SDK's automatic function-calling — we run tools
        # ourselves so we can emit `tool_call`/`tool_result` events to the
        # UI as they happen.
        config_kwargs["automatic_function_calling"] = gtypes.AutomaticFunctionCallingConfig(
            disable=True
        )

    stream = await client.aio.models.generate_content_stream(
        model=model_id,
        contents=contents,
        config=gtypes.GenerateContentConfig(**config_kwargs),
    )

    async for chunk in stream:
        text = getattr(chunk, "text", None)
        if text:
            yield GeminiTextChunk(delta=text)

        candidates = getattr(chunk, "candidates", None) or []
        for cand in candidates:
            content = getattr(cand, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                fc = getattr(part, "function_call", None)
                if fc and fc.name:
                    yield GeminiFunctionCall(name=fc.name, args=dict(fc.args or {}))
