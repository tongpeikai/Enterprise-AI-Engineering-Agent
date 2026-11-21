# Enterprise AI Engineering Agent

Enterprise AI Engineering Agent is an independently designed platform for building, operating, and evaluating tool-using AI agents. It combines an application-owned gateway, security model, knowledge layer, workflow engine, observability, and React console with the OpenHands Agent Server as the execution integration boundary.

The ownership boundary is explicit: the modules below are project engineering work; Agent execution primitives are integrated through OpenHands Agent Server; FastAPI, React, SQLite, PostgreSQL/pgvector, Docker, and other libraries remain third-party open-source components.

## Engineering Contributions

### Agent Gateway

Provides an application-owned boundary for conversations, runs, events, interruption, reconnects, cursor de-duplication, timeouts, and errors. It uses Python, FastAPI, HTTPX, WebSockets, SQLite, and the OpenHands Agent Server API, giving tasks, workflows, and the frontend a stable integration seam. Agent reasoning itself remains provided by the integrated OpenHands service.

### Authentication & RBAC

Protects agent tools and business APIs with registration, password hashing, signed access tokens, refresh rotation/revocation, login lockout, role checks, and server-side authorization. It uses FastAPI, Pydantic, PBKDF2, HMAC signing, and SQLite to create an enforceable security boundary rather than frontend-only controls.

### Multi-tenant Architecture

Prevents organizations from reading or mutating one another's projects, tasks, documents, workflows, approvals, and metrics. Tenant context flows through authenticated requests and is enforced in stores and routes with cross-tenant tests. This makes isolation an application invariant.

### Tool Registry & MCP

Makes tools discoverable and controlled through registry metadata, JSON Schema/Pydantic validation, tenant and role permissions, concurrency and timeout limits, dangerous-operation approvals, audit callbacks, path/command safety rules, and a local MCP client/server loop. Python, asyncio, Pydantic, and Docker isolation provide an extensible execution boundary without modifying OpenHands internals.

### RAG Knowledge Management

Adds tenant-scoped TXT/Markdown/PDF ingestion, duplicate/version detection, configurable chunking, metadata and page provenance, SQLite FTS5 retrieval, top-k/threshold filtering, ACL enforcement, deletion cleanup, and evidence-delimited prompt context. The result is a reproducible knowledge workflow with source citations and separation between evidence and generation.

### Workflow Orchestration

Turns Agent runs into durable business processes through persisted workflow/step models, DAG validation, cycle detection, ready-step scheduling, bounded parallelism, retries, approvals, Agent conversation/run correlation, cancellation, and restart recovery. Python asyncio, SQLite transactions, FastAPI, and the Gateway integration supply this application-owned orchestration layer.

### Metrics & Benchmark

Provides thread-safe counters, gauges, histograms, timers, snapshots, tenant-scoped APIs, persisted benchmark runs, and deterministic Recall@K, Precision@K, MRR, and Hit Rate@K evaluation. These metrics support repeatable engineering comparisons; reported scores describe the supplied evaluation set only, not production performance.

### React Frontend

Delivers protected routes, session state, an Agent workspace with WebSocket reconnect and cursor de-duplication, task/workflow/approval/knowledge/tool pages, and live dashboards. React, TypeScript, Vite, Ant Design, Zustand, Axios, React Router, ECharts, and WebSockets provide a real API client rather than a static mock interface.

### Docker Deployment

Provides pinned Agent Server and pgvector digests, health checks, persistent volumes, environment-driven secrets, PowerShell start/stop scripts, and a resource-safe Stage 10 Lite profile. The Lite profile reuses verified Stage 0 infrastructure for the current 1.9 GiB Docker engine; the higher-memory duplicate stack is not presented as validated here.

### Security Engineering

Treats prompts, documents, tools, credentials, and tenant boundaries as security surfaces through evidence delimiting, refresh controls, brute-force lockout, path traversal defenses, command restrictions, approval gates, secret-file exclusion, regression tests, and release-tree scans. These controls are project work layered around third-party components and the OpenHands integration.

## Architecture and ownership

Project-owned code lives in `backend/`, `frontend/`, `agent/`, `deploy/`, `scripts/`, and `tests/`. OpenHands Agent Server is the execution integration and is not claimed as original implementation. FastAPI, React, Ant Design, Zustand, ECharts, SQLite, PostgreSQL/pgvector, Docker, and Python packages remain third-party components under their respective licenses.

## Quick start

```powershell
Copy-Item .env.example .env
# Replace placeholders with local-only values. Never commit .env.
./scripts/stage10-start.ps1
```

Open `http://127.0.0.1:5173`; stop with `./scripts/stage10-stop.ps1`. See [docs/FINAL_DEPLOYMENT_GUIDE.md](docs/FINAL_DEPLOYMENT_GUIDE.md).

## Development and verification

```powershell
uv sync
uv run ruff check backend tests
uv run pytest -q
cd frontend; npm ci; npm run lint; npm run test -- --run; npm run build
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/API_GUIDE.md](docs/API_GUIDE.md), [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md), [docs/THIRD_PARTY_LICENSES.md](docs/THIRD_PARTY_LICENSES.md), and [docs/FINAL_PRODUCT_ACCEPTANCE_REPORT.md](docs/FINAL_PRODUCT_ACCEPTANCE_REPORT.md).

## License and attribution

Project-owned code is released under the MIT License. OpenHands attribution and license notices are retained in [LICENSE](LICENSE) and [NOTICE](NOTICE). Third-party dependencies remain under their own licenses; see [docs/THIRD_PARTY_LICENSES.md](docs/THIRD_PARTY_LICENSES.md). No OpenHands upstream implementation is presented as original project code.
