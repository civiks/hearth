<img src="frontend/public/brand-mark.svg" alt="hearth" width="64">

# hearth

[![ci](https://img.shields.io/github/actions/workflow/status/civiks/hearth/ci.yml?branch=main&label=ci&style=flat-square)](https://github.com/civiks/hearth/actions/workflows/ci.yml)
[![docker](https://img.shields.io/github/actions/workflow/status/civiks/hearth/docker.yml?label=docker&style=flat-square)](https://github.com/civiks/hearth/actions/workflows/docker.yml)
[![license](https://img.shields.io/github/license/civiks/hearth?style=flat-square)](LICENSE)

[demo](https://civiks.github.io/hearth/) · [docker](#docker) · [setup](#setup) · [todo](TODO.md)

> GenAI-backed marketplace for home services.

## Highlights

- **Chat to do anything in the app** — You type what you want; the chatbot picks the right action and runs it. [How it works ↓](#the-chatbot)
- **Multi-role** — customers book, professionals fulfill, admins moderate.
- **Booking lifecycle** — `requested → accepted → in_progress → completed` (or `cancelled`), with status transitions gated by role.
- **Background jobs** — daily reminder emails to pros with pending requests, monthly activity reports to customers, async CSV exports admins can kick off and poll.
- **Dashboards per role** — system-wide metrics for admins, personal earnings and status mix for pros.

## Gallery

![Browse requests](docs/01-browse.png)

![Admin overview](docs/02-admin.png)

![Service requests](docs/03-professional.png)

![Login](docs/04-auth.png)

## The chatbot

Actions are invoked through natural language. The model selects an action, the backend runs it against the database, and the result is returned in the same response stream.

### Available actions by role

| Role | Actions |
| --- | --- |
| Customer | Search services, list own requests, check request status, create a booking |
| Professional | View pending requests in their area, accept a request, view weekly summary |
| Admin | View platform metrics, list pending applicants, approve a professional |

**Bring your own key.** Each user adds their own Gemini key in Settings → AI; the server encrypts it and stores it tied to their account. The browser never sees the stored key. If you'd rather run a shared key for everyone, set `GEMINI_API_KEY` in `.env` and skip the per-user step.

## Stack

| | |
| --- | --- |
| **Backend** | Python 3.13, FastAPI, SQLAlchemy 2.0 (typed), Alembic, Pydantic v2, Celery, Redis, PostgreSQL |
| **Frontend** | Vue 3, TypeScript, Vite, Pinia, Tailwind CSS | 
| **Infra** | Docker |
| **Tooling** | pytest, Ruff, vue-tsc, ESLint |

## Docker

```bash
docker run -p 8000:8000 -v hearth-data:/data ghcr.io/civiks/hearth:latest
```

Open <http://localhost:8000>. `make docker-build` / `make docker-run` for a local build.

## Setup

Requires Python 3.13, Node 24, pnpm, and Postgres + Redis (native or `docker compose up -d`).

```bash
make install            # uv sync + pnpm install
cp .env.example .env
make migrate seed       # Alembic upgrade + seed data
```

Run the stack, one process per terminal:

```bash
make backend            # FastAPI on :8000
make worker             # Celery worker
make beat               # Celery beat
make frontend           # Vite on :5173
make demo               # VITE_DEMO=1 — frontend only, in-browser mocks
```

`make help` lists every target.

### Seeded credentials

| Role         | Email                | Password  |
| ------------ | -------------------- | --------- |
| Admin        | `admin@email.com`    | `admin`   |
| Customer     | `user01@email.com`   | `user01`  |
| Professional | `plumber@email.com`  | `pass123` |

Demo build accepts any password with `admin@demo.local`, `customer@demo.local`, or `pro@demo.local`.

## Tests

```bash
make test               # pytest, 22 tests
make lint               # ruff check
make typecheck          # vue-tsc
```

## Layout

```
backend/
  api/routers/      endpoints
  celery/           background tasks
  core/             config, db, security
  schemas/          Pydantic models
  services/         business logic
frontend/src/
  views/            per-route SFCs
  components/       shared UI + shadcn-vue primitives
  layouts/          dashboard / auth / public
  lib/demo/         static demo mock layer
```

## License

[MIT](LICENSE)
