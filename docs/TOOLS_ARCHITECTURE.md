# Tool and MCP Architecture

Requests enter through authenticated FastAPI routes or the OpenHands Gateway. The registry resolves a named `ToolSpec`, checks role-derived permissions and dangerous-action approval, validates Pydantic arguments, applies a bounded semaphore and timeout, then emits an audit record. Filesystem and command tools must additionally use workspace path and allowlist policies. MCP servers are registered only after explicit approval; the local client uses a bounded JSON-RPC subprocess boundary.
