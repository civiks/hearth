"""Agentic GenAI surface — Gemini function calling against the live DB.

Layout:
- `tools.py`   — Tool dataclass, registry, and tool implementations.
- `gemini.py`  — Thin wrapper around the google-genai SDK (streaming + tools).
- `runner.py`  — The agent loop: stream from Gemini, execute tools, emit
                 `AgentEvent`s back to the SSE response.

The SSE route lives at `backend/api/routers/agent.py`; everything in this
package is HTTP-agnostic so it can be reused (e.g. from a Celery task or a
CLI tool) and unit-tested without spinning up the FastAPI app.
"""
