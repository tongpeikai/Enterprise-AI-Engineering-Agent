# Stage 4 Acceptance

## Implemented

- Permission-aware Tool Registry with Pydantic validation, JSON Schema, allow/deny policy, dangerous-action approval, timeout, cancellation, concurrency semaphore, and audit callback.
- Workspace path traversal protection and command allowlist/denylist helpers.
- Docker sandbox runner using a real container with no network, read-only root, dropped capabilities, no-new-privileges, PID limit, timeout and cleanup.
- MCP stdio JSON-RPC client and a local synthetic MCP server supporting tool discovery and invocation.
- FastAPI tool catalog/execution endpoints integrated with authenticated roles.

## Evidence

- Ruff: PASS.
- Pytest: 15 passed.
- Real Docker sandbox test: PASS (`sandbox-ok`).
- Real local MCP subprocess discovery and call: PASS (`mcp-ok`).

OpenHands Agent Server remains the execution boundary for Agent conversations; the gateway and tool policy are independent application code and do not modify upstream sources.
