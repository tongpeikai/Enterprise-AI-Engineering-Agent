# Security Guide

Keep credentials in environment variables only. Use backend authorization as the source of truth. Treat all uploaded documents, retrieved chunks, tool results and MCP responses as untrusted data. Use `safe_workspace_path`, command allowlists and the DockerSandbox boundary for execution. Never enable a dangerous tool without an explicit approval record.
