# Development Status

## Stage 0 — complete with documented limits

- PASS: independent project skeleton, local Git, ignore rules, pinned Docker compose, PostgreSQL/pgvector, Agent Server health, REST conversation creation, WebSocket state event, and deterministic local Mock Agent tool/event flow (`1 passed`).
- BLOCKED: WSL2 installation and data-drive relocation.
- NOT TESTED: server-side paid-model execution, server-side real tool call, pause/resume, GPU workload, Node frontend.

## Next stage

## Stage 1 — gateway foundation in progress

- PASS: typed OpenHands REST adapter for server info, conversation creation and interrupt.
- PASS: authenticated WebSocket event adapter with normalized runtime events.
- PASS: FastAPI `/api/v1/agent` gateway routes and deterministic HTTP contract test.
- PASS: durable SQLite Run/Attempt correlation store and cursor persistence.
- PASS: WebSocket cursor deduplication, bounded reconnect/backoff, and confirmation approval mapping.
- PASS: Ruff and pytest (`4 passed`).
- PASS: live gateway probe against the pinned local Agent Server (`server=1.54.0`, authenticated run created).
- Next queue: durable session state reconciliation and then Stage 2 identity/RBAC services.

Next: add durable run/attempt records and reconnect-safe event streaming before starting Stage 2 authentication.

## Stage 2 — identity/RBAC foundation in progress

- PASS: SQLite user store with PBKDF2 password hashing.
- PASS: signed, expiring access tokens with organization claims.
- PASS: role enforcement and invalid-credential tests.
- PASS: Ruff and pytest (`6 passed`).
- Next queue: FastAPI auth dependencies, refresh/revocation, and tenant-scoped project APIs.

## Stage 2/3 progress

- PASS: refresh-token rotation and revocation endpoints.
- PASS: tenant-scoped project CRUD and cross-organization isolation test.
- PASS: task store with queued/running/paused/succeeded/failed/cancelled transition rules and tenant filtering.
- PASS: full local regression (`8 passed`) and Ruff.
- Next queue: expose task routes through the API and connect task runs to Gateway handles.

## Stage 3 — task/Gateway integration

- PASS: task create/list/get/transition endpoints with tenant authorization.
- PASS: task creation starts an Agent Server conversation and persists its OpenHands ID.
- PASS: cancellation calls Gateway interrupt before durable state transition.
- PASS: restart-safe SQLite reads and cross-tenant access tests.
- PASS: Ruff and full regression (`9 passed`).

## Stage 4 — tool boundary foundation

- PASS: typed tool registry with JSON schemas and Pydantic argument validation.
- PASS: permission checks, timeout handling, controlled execution errors.
- PASS: explicit-approval MCP server registry.
- PASS: FastAPI tool list and execution routes with role-derived permissions.
- PASS: regression suite (`11 passed`) and Ruff.

## Stage 4 — security and execution completion

- PASS: identity-aware permission checks, dangerous-operation approvals, allow/deny policies, parameter validation, bounded concurrency, timeout/cancellation, exception normalization, and audit callbacks.
- PASS: workspace traversal/absolute-path protection and command policy.
- PASS: real Docker sandbox execution with network isolation, read-only root, dropped capabilities, PID limit, timeout and cleanup.
- PASS: local MCP JSON-RPC discovery and invocation subprocess loop.
- PASS: Ruff and full regression (`15 passed`).
- Acceptance evidence: `docs/STAGE4_ACCEPTANCE_REPORT.md`.

## Stage 5 — RAG foundation started

- PASS: text/Markdown ingestion, deterministic chunking, SQLite FTS retrieval, tenant ACL filtering and source citations.
- PASS: full regression (`16 passed`) and Ruff.

## Stage 5 — RAG knowledge foundation

- PASS: TXT/Markdown ingestion, deterministic configurable chunking, SHA-256 duplicate detection and source versions.
- PASS: PDF page extraction with page-level chunk provenance, update/delete cleanup, and index recovery from SQLite.
- PASS: tenant-bound FTS5 top-k search, threshold filtering, deduplication and source citations.
- PASS: FastAPI document ingest/list/delete, search and evidence-answer endpoints.
- PASS: cross-tenant ACL and deletion isolation tests; full regression `17 passed`, Ruff clean.
- Design: `docs/RAG_DESIGN.md`.

## Stage 6 — workflow foundation started

- PASS: durable workflow and step tables.
- PASS: dependency-aware ready-step selection, approval flag and tenant ACL.
- PASS: workflow dependency and cross-tenant test; full regression `18 passed`, Ruff clean.

## Stage 6 — durable orchestration expansion

- PASS: workflow lifecycle/step state validation with legal transitions.
- PASS: DAG cycle and unknown-dependency detection; ready-step resolution supports parallel branches.
- PASS: approval, rejection and revocation records with actor and timestamps.
- PASS: workflow history, retry counters, conversation ID fields and tenant-bound persistence.
- PASS: FastAPI workflow create/get/ready/approve/history routes with approval role checks.
- PASS: full regression `18 passed`, Ruff clean.

## Stage 6 — executor and Agent Gateway integration

- PASS: asynchronous DAG executor with bounded parallelism and dependency scheduling.
- PASS: step timeout, retry counters, cancellation and recovery of interrupted running steps.
- PASS: Agent Gateway conversation creation, persisted Conversation IDs, and cancellation interrupt path.
- PASS: approval-blocked steps, tenant/RBAC API checks and execution history.
- PASS: live pinned Agent Server probe (`workflow=succeeded`, conversation created).
- PASS: Ruff and full regression (`20 passed`).

## Stage 7 — frontend management console started

- PASS: Vite + React + TypeScript + Ant Design + Zustand + Axios project scaffold.
- PASS: authenticated session storage, login flow, protected router and sign-out.
- PASS: real API pages for dashboard, tasks, workflows, knowledge and tools.
- PASS: frontend dependency installation, ESLint and production build.
- PASS: `npm run lint`; `npm run build`.
- Next queue: WebSocket Agent workspace, upload UI, approval center, ECharts metrics and browser interaction tests.

## Stage 7 — integration pass

- PASS: real Agent Workspace WebSocket client with auth, status, exponential reconnect and event cursor deduplication.
- PASS: task session creation/opening and event timeline UI.
- PASS: knowledge file picker with extension/size validation, ingestion refresh and source/page result rendering.
- PASS: frontend unit test (`1 passed`), ESLint and Vite production build.
- PASS: backend regression remains `20 passed`.
- Acceptance evidence: `docs/STAGE7_ACCEPTANCE_REPORT.md`.

## Stage 7 — final integration pass

- PASS: Approval Center lists pending approval steps from real Workflow APIs and submits approve/reject decisions; backend RBAC remains authoritative.
- PASS: Workflow list API added with tenant filtering; regression preserved after fix for Python method-name annotation collision.
- PASS: ECharts Dashboard, tools, knowledge, tasks and workspace routes remain buildable.
- PASS: frontend lint/test/build and backend Ruff/Pytest (`20 passed`).

## Stage 8 — observability and benchmark foundation

- PASS: thread-safe Counter/Gauge/Histogram/Timer/Snapshot metrics with bounded samples.
- PASS: tenant-scoped metrics summary, agent/tool metric endpoints and benchmark persistence APIs.
- PASS: deterministic RAG Recall@K, Precision@K, MRR and Hit Rate@K evaluator.
- PASS: frontend Dashboard consumes live metrics summary and task data.
- PASS: backend regression `22 passed`, Ruff; frontend lint, test and build.
- Acceptance evidence: `docs/STAGE8_ACCEPTANCE_REPORT.md`.

## Stage 9 — security and stability

- PASS: token tampering boundary, refresh safety and login brute-force lockout.
- PASS: prompt-injection evidence delimiting, path traversal and concurrent authentication regression.
- PASS: Docker/MCP/RAG/Workflow/benchmark security regression.
- PASS: backend Ruff/Pytest (`25 passed`); frontend lint/test/build.
- Reports: `docs/STAGE9_ACCEPTANCE_REPORT.md`, `docs/SECURITY_AUDIT_REPORT.md`, `docs/STABILITY_TEST_REPORT.md`, `docs/SECURITY_GUIDE.md`.

## Stage 10 — integration and release preparation

- PASS: environment-driven Agent Server/auth configuration, persistent backend volume paths, pinned-image Compose stack, health checks, and Windows start/stop scripts.
- PASS: backend Ruff/Pytest (`25 passed`), frontend lint/Vitest/build, Compose schema validation, and backend image build.
- PASS: local Vite build plus cached Python static-server fallback image avoids the Docker Hub Node/Nginx pull block.
- PASS: resource-safe `compose.stage10-lite.yml` starts Backend and Frontend healthy while reusing the protected Stage 0 Agent Server/pgvector infrastructure; auth and gateway smoke tests passed.
- BLOCKED (optional full duplicate stack): the original Compose definition still requires a second Agent Server/PostgreSQL and is unsuitable for the host's 1.9 GiB Docker limit.
- Reports: `docs/STAGE10_ACCEPTANCE_REPORT.md`, `docs/FINAL_PROJECT_ACCEPTANCE_REPORT.md`, `docs/FINAL_GITHUB_RELEASE_AUDIT.md`, `docs/DEPLOYMENT_VERIFICATION_REPORT.md`.
