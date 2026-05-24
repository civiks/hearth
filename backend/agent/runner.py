from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.orm import Session

from backend.agent import gemini
from backend.agent.tools import ToolError, get_tool, tools_for_role
from backend.core.config import get_settings
from backend.models import User

AgentEvent = dict[str, Any]


SYSTEM_PROMPT = """You are hearth AI, an in-app assistant for a local-services marketplace.

You can call tools to read or change the user's data. Prefer using tools
over asking the user for information you can look up yourself. Use multiple
tools in sequence when a task needs it. After tools return, summarize the
result concisely.

Style:
  * Keep responses short — usually 1–4 short paragraphs.
  * Use **bold** for key names, IDs, and numbers.
  * Format lists as bullets when you have more than two items.
  * Don't invent IDs or fields — only refer to data returned by tools.
""".strip()


def _state_for_tool(name: str) -> str:
    if name.startswith(("search_", "list_")):
        return "Searching"
    if name.startswith(("check_", "get_")) or name == "weekly_summary":
        return "Analyzing"
    if name.startswith(("accept_", "approve_", "book_")):
        return "Updating"
    return "Working"


def _user_role(user: User) -> str | None:
    return user.roles[0].name if user.roles else None


async def _execute_tool(
    *,
    session: Session,
    user: User,
    role: str | None,
    name: str,
    args: dict[str, Any],
) -> tuple[bool, Any]:
    """Run the named tool with role-gating. Returns (ok, payload)."""
    tool = get_tool(name, role)
    if tool is None:
        return False, "forbidden"
    try:
        # Sync tool runs in a worker thread so the event loop keeps streaming
        # other connections.
        data = await asyncio.to_thread(tool.run, session, user, args)
        return True, data
    except ToolError as e:
        return False, str(e)
    except Exception as e:  # surface unexpected failures rather than dying silently
        return False, f"tool error: {e}"


async def run(
    *,
    session: Session,
    user: User,
    role: str | None,
    history: list[dict[str, str]],
    message: str,
    model_id: str,
    gemini_api_key: str | None = None,
) -> AsyncIterator[AgentEvent]:
    """Emit a stream of AgentEvents in response to `message`."""
    settings = get_settings()
    available_tools = tools_for_role(role or _user_role(user))

    # Build the initial conversation. Subsequent loop iterations extend it.
    contents = gemini.history_to_contents(history)
    contents.append(gemini.user_text(message))

    # The UI shows "Thinking" until the first text or tool event lands.
    yield {"type": "state", "status": "Thinking"}
    seen_text_this_turn = False

    try:
        for _iteration in range(settings.gemini_max_tool_iterations):
            # Accumulators for what the model emits in this turn — used to
            # reconstruct its turn for the next call and to drive tool exec.
            text_buf: list[str] = []
            pending_calls: list[gemini.GeminiFunctionCall] = []

            async for ev in gemini.stream_turn(
                model_id=model_id,
                contents=contents,
                tools=available_tools,
                system_prompt=SYSTEM_PROMPT,
                api_key=gemini_api_key,
            ):
                if isinstance(ev, gemini.GeminiTextChunk):
                    if not seen_text_this_turn:
                        yield {"type": "state", "status": "Writing"}
                        seen_text_this_turn = True
                    text_buf.append(ev.delta)
                    yield {"type": "text", "delta": ev.delta}
                elif isinstance(ev, gemini.GeminiFunctionCall):
                    pending_calls.append(ev)

            # No tool requests → the model is done with this run.
            if not pending_calls:
                break

            # Append the model's turn (text + function calls) so Gemini sees
            # its own prior output on the next call.
            contents.append(
                gemini.model_turn(text="".join(text_buf) or None, function_calls=pending_calls)
            )

            # Execute every requested tool, emit events, attach responses.
            for fc in pending_calls:
                call_id = f"tc_{uuid.uuid4().hex[:8]}_{int(time.time() * 1000)}"
                yield {"type": "state", "status": _state_for_tool(fc.name)}
                yield {
                    "type": "tool_call",
                    "id": call_id,
                    "name": fc.name,
                    "args": fc.args,
                }
                ok, data = await _execute_tool(
                    session=session, user=user, role=role, name=fc.name, args=fc.args
                )
                yield {"type": "tool_result", "id": call_id, "ok": ok, "data": data}
                # Feed the result back to Gemini for the next turn. We always
                # use a single key (`result` or `error`) to keep the schema
                # the model sees consistent.
                payload = {"result": data} if ok else {"error": data}
                contents.append(gemini.function_response(name=fc.name, response=payload))

            # Reset the "Writing" gate for the next iteration — the model
            # may resume narrating after seeing the tool result.
            seen_text_this_turn = False
        else:
            # Loop hit the iteration cap without the model finishing — tell
            # the user rather than silently truncating.
            yield {
                "type": "text",
                "delta": "\n\n_Stopped: the assistant ran more tool calls than allowed._",
            }
    except Exception as exc:
        yield {
            "type": "text",
            "delta": f"\n\n_Something went wrong: {exc}_",
        }

    yield {"type": "done"}
