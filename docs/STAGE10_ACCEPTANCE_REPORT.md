# Stage 10 acceptance

Date: 2026-11-21. Scope: local integration and release preparation; no remote writes.

| Check | Result | Evidence |
|---|---|---|
| Backend Ruff | PASS | `uv run ruff check backend tests` |
| Backend tests | PASS | 25 passed |
| Frontend lint | PASS | `npm run lint` |
| Frontend tests | PASS | 1 passed |
| Frontend production build | PASS | Vite build completed |
| Compose schema | PASS | `docker compose ... config --quiet` |
| Root `.env` loading | PASS | `--env-file .env` now explicit in start/stop scripts; rotated local auth signing value without printing it |
| Pinned images | PASS | Agent Server 1.54.0 and pgvector digests in compose |
| Backend image build | PASS | Docker built `enterprise-agent-backend` successfully |
| Original frontend image build | BLOCKED | Docker Hub authorization/network timeout while resolving node/nginx base images |
| Frontend fallback image build | PASS | Local Vite build + cached `python:3.13-slim` static server |
| Real full-stack compose restart | BLOCKED | Images built and isolated containers recreated, but Docker Desktop `start` remained hung with containers in `Created`; existing Stage 0 data was not touched |
| Post-change backend regression | BLOCKED | 24 passed, 1 Docker sandbox timeout because Docker container lifecycle remained hung; Ruff still passed |
| Resource-safe lite deployment | PASS | Backend and frontend healthy; backend `ok`, frontend HTTP 200, Agent Server `ok`; Stage 0 containers unchanged |
| Auth smoke test | PASS | Local registration and login succeeded; token value not printed |
| Gateway smoke test | PASS | Backend reached Stage 0 Agent Server `/server-info` successfully |
| Runtime memory observation | PASS | Backend ~134 MiB, frontend ~19 MiB, Stage 0 Agent Server ~526 MiB, Stage 0 PostgreSQL ~39 MiB |
| Paid model/GPU | NOT TESTED | Explicitly out of scope; Mock mode retained |

The backend now reads Agent Server, auth, and persistent SQLite paths from environment variables, and the compose stack persists backend stores in a named volume.
