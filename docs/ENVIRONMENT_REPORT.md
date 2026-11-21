# Environment Report

Date: 2026-11-20 (Asia/Shanghai)

| Component | Result | Evidence |
|---|---|---|
| Windows 11 + Hyper-V | PASS | Hyper-V backend available; Docker Linux engine running |
| WSL2 | BLOCKED | Windows optional features enabled, but WSL app package is absent; Store/standalone installation was not completed |
| Docker Desktop | PASS | Docker 29.9.3, Linux engine, `desktop-linux` context |
| Python | PASS | Python 3.13, project `.venv`, uv 0.13.9, frozen `uv.lock` |
| Node/npm | NOT TESTED | Not required by Stage 0 backend baseline |
| RTX 5080 | NOT TESTED | No model download or GPU workload was performed |
| Docker data location | PARTIAL | Docker VHDX remains on C:; D: has more free space, relocation deferred to avoid risky system migration |

Resource evidence: Docker images occupy approximately 5.24 GB; C: retained approximately 32.6 GB free and D: approximately 134 GB free at inspection time.
