# Stage 7 Acceptance

- PASS: React/Vite/TypeScript console with protected routing and session authentication.
- PASS: real Tasks, Workflow, Knowledge and Tools API pages.
- PASS: Agent Workspace connects to OpenHands `/sockets/events/{conversation_id}`, sends auth, shows event/tool timeline, tracks connection state, reconnects with exponential backoff and deduplicates cursors.
- PASS: Knowledge page validates extension/10 MB client limit and submits file content to the existing ingestion API.
- PASS: frontend cursor test, ESLint and production build.
- PASS: backend regression `20 passed`.
- PASS: Approval Center consumes real workflow list/detail/approval endpoints; backend role checks remain authoritative.
- PASS: Tools page and Dashboard use live API responses with explicit empty/error states.
- PASS: full integration quality gates rerun after approval API additions.

The frontend does not store passwords or hard-code credentials. Backend authorization remains authoritative for all protected operations.
