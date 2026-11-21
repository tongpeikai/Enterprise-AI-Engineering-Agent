# Deployment verification

`docker compose -f deploy/compose.stage10.yml config --quiet` passed with placeholder environment values. The stack defines health checks and restart policies for PostgreSQL, Agent Server, backend, and frontend, plus named volumes for database, server state, workspace, and backend SQLite stores.

The original Node/Nginx image resolution was blocked by a Docker Hub anonymous-token network timeout. Node 24.21.0 and npm 11.19.0 are available locally, so the frontend was built with the existing local toolchain and the compose file uses the trusted, already-cached `python:3.13-slim` image to serve the generated static files. This changes only the frontend serving layer (Python static HTTP instead of Nginx); application assets and API behavior are unchanged. The existing Stage 0 Agent Server and pgvector services were previously verified live.

The fallback backend and frontend images built successfully. A Stage 10 `up -d` created isolated containers and volumes, but Docker Desktop then hung while starting/inspecting the new containers; the existing Stage 0 stack remained untouched. This is an environment/daemon blocker, not an application build failure.

Root cause of the earlier missing `AUTH_SIGNING_KEY` was Compose's implicit `.env` lookup relative to `deploy/`; the scripts now pass `--env-file <project>/.env`. The local signing value was rotated without exposing it.

After the isolated Stage 10 containers were removed where Docker responded, a real sandbox retry still hung at Docker container lifecycle. Stage 0 containers remained healthy throughout. A Docker Desktop Engine restart is required before the final health and end-to-end run can be truthfully marked PASS.

After Docker Desktop recovery, the resource-safe `compose.stage10-lite.yml` deployment was built and started successfully. It runs Backend and Frontend in an isolated network, reuses the already healthy Stage 0 Agent Server at `host.docker.internal:8010` and Stage 0 pgvector/PostgreSQL infrastructure, and preserves the separate Stage 10 backend volume. Backend health, frontend HTTP 200, Agent Server reachability, registration/login, and gateway server-info all passed.
