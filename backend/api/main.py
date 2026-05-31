from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.api.middleware import RequestLoggingMiddleware
from backend.api.routers import agent, analytics, auth, exports, requests, services, users
from backend.core.config import get_settings
from backend.core.db import get_session
from backend.core.logging import configure_logging

settings = get_settings()

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.slowapi_storage_uri)


def create_app() -> FastAPI:
    configure_logging(settings.debug)

    app = FastAPI(
        title="hearth API",
        version="0.2.0",
        debug=settings.debug,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, lambda req, exc: exc.response())  # type: ignore
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/healthz", tags=["meta"])
    def healthz(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
        try:
            session.execute(text("SELECT 1"))
            db_status = "ok"
        except Exception:
            db_status = "error"
        overall = "ok" if db_status == "ok" else "degraded"
        return {"status": overall, "db": db_status}

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(services.router)
    app.include_router(requests.router)
    app.include_router(exports.router)
    app.include_router(analytics.router)
    app.include_router(agent.router)

    # Mount the built frontend if present (bundled Docker image path).
    # Skipped during dev since the Vite dev server serves the frontend separately.
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.is_dir():
        assets_dir = frontend_dist / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def spa_fallback(full_path: str):
            if full_path.startswith(("api/", "healthz", "docs", "redoc", "openapi.json")):
                raise HTTPException(status_code=404)
            candidate = frontend_dist / full_path
            if candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(frontend_dist / "index.html")

    return app


app = create_app()
