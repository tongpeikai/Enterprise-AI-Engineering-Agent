# Security Audit Report

The application enforces backend bearer-token validation, refresh rotation/revocation, tenant-bound queries, role checks, workspace path containment, command policy, explicit dangerous-tool approval, Docker no-network/read-only/capability-drop defaults, and delimited untrusted RAG evidence. Security regression tests live under `tests/security/`. Logs and metrics do not use credentials as labels. Remaining external boundary work includes production reverse-proxy hardening and a full multi-process load campaign.
