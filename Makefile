.PHONY: help install migrate seed backend worker beat frontend demo test lint typecheck build clean docker-build docker-run

help:
	@echo "make install      install backend + frontend deps"
	@echo "make migrate      alembic upgrade head"
	@echo "make seed         seed demo data (18 services, 30 pros, etc)"
	@echo "make backend      run fastapi on :8000"
	@echo "make worker       run celery worker"
	@echo "make beat         run celery beat (periodic tasks)"
	@echo "make frontend     run vite on :5173"
	@echo "make demo         run vite in static demo mode (no backend)"
	@echo "make test         pytest"
	@echo "make lint         ruff check"
	@echo "make typecheck    vue-tsc"
	@echo "make build        production frontend build"
	@echo "make docker-build build the all-in-one Docker image locally"
	@echo "make docker-run   run the local image on :8000"
	@echo "make clean        remove dist/, __pycache__, .pytest_cache"

install:
	uv sync
	cd frontend && pnpm install

migrate:
	uv run alembic upgrade head

seed:
	uv run python -m backend.seed

backend:
	uv run uvicorn backend.api.main:app --reload --port 8000

worker:
	uv run celery -A backend.celery.celery_factory worker --loglevel=info

beat:
	uv run celery -A backend.celery.celery_factory beat --loglevel=info

frontend:
	cd frontend && pnpm dev

demo:
	cd frontend && VITE_DEMO=1 pnpm dev

test:
	uv run pytest backend/tests/ -v

lint:
	uv run ruff check backend/

typecheck:
	cd frontend && pnpm typecheck

build:
	cd frontend && pnpm build

docker-build:
	docker build -t hearth:local .

docker-run:
	docker run --rm -p 8000:8000 -v hearth-data:/data hearth:local

clean:
	rm -rf frontend/dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
