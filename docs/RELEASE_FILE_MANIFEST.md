# Release file manifest

The release copy contains 131 files across:

- `backend/`: Gateway, auth/RBAC, tasks, tools/MCP, RAG, workflows, metrics and API routes.
- `frontend/`: React/TypeScript source, package manifests, Vite configuration and SPA static server.
- `agent/`: project Agent integration.
- `deploy/`: pinned full Compose and resource-safe Lite Compose plus database init scripts.
- `scripts/`: Windows start/stop and verification utilities.
- `tests/`: public automated tests.
- `docs/`: architecture, installation, security, deployment, benchmark and acceptance documentation.

Excluded by policy: `.env`, databases, Docker volumes, logs, uploads, caches, `node_modules`, `dist`, `.venv`, bytecode and private runtime artifacts.
