from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.api.routers import analytics, auth, exports, requests, services, users
from backend.core.config import get_settings

settings = get_settings()

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.slowapi_storage_uri)


def create_app() -> FastAPI:
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

    @app.get("/healthz", tags=["meta"])
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(services.router)
    app.include_router(requests.router)
    app.include_router(exports.router)
    app.include_router(analytics.router)

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
