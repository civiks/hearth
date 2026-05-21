# syntax=docker/dockerfile:1.6

# ---------------- Stage 1: build the Vue frontend ----------------
FROM node:24-alpine AS frontend

WORKDIR /build
RUN npm install -g pnpm@11

COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./

# Empty VITE_API_URL so the built bundle uses same-origin relative paths
# (the bundled image serves both API and frontend from one process).
RUN VITE_API_URL="" pnpm build


# ---------------- Stage 2: Python runtime ----------------
FROM python:3.13-slim AS runtime

# uv (single static binary; small, fast)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Resolve and install Python deps first so layer caches survive code changes
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY backend/ ./backend/
COPY alembic.ini ./

# Built frontend from stage 1
COPY --from=frontend /build/dist ./frontend/dist

# Volume for the SQLite DB + Celery CSV exports
RUN mkdir -p /data
VOLUME /data

# Defaults for the all-in-one image:
# - SQLite at /data/hearth.db
# - Celery in eager mode (tasks run in-process, no broker needed)
# - In-memory slowapi rate-limit storage (no Redis needed)
ENV DATABASE_URL=sqlite:////data/hearth.db \
    CELERY_EAGER=true \
    PORT=8000 \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8000

COPY <<'EOF' /app/docker-entrypoint.sh
#!/bin/sh
set -e
cd /app
uv run alembic upgrade head
if [ ! -f /data/.seeded ]; then
  echo "Seeding initial data..."
  uv run python -m backend.seed
  touch /data/.seeded
fi
exec uv run uvicorn backend.api.main:app --host 0.0.0.0 --port "${PORT}"
EOF
RUN chmod +x /app/docker-entrypoint.sh

CMD ["/app/docker-entrypoint.sh"]
