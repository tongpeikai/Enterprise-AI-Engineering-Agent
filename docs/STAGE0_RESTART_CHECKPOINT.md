# Stage 0 Restart Checkpoint

Recorded: 2026-11-20  
Status: system restart required before Stage 0 can continue

## Completed before restart

- Initialized a local Git repository on branch `main`.
- No Git remote is configured.
- No commit or push was performed.
- Added public-repository `.gitignore`, `.env.example`, LICENSE, and NOTICE.
- Added the Stage 0 Docker Compose definition and pgvector initialization SQL.
- Installed uv 0.13.9.
- Created an independent Python 3.13 virtual environment and lock file.
- Installed only the Stage 0 Python dependencies.
- Installed Docker Desktop 4.99.0.
- Installed the Ubuntu 24.04 LTS application package.
- Enabled Windows Subsystem for Linux and Virtual Machine Platform.
- Stored randomly generated Stage 0 database and Agent Server secrets in the
  current Windows user's environment. Secret values were not written to the
  repository or printed in reports.
- Verified official upstream tags through the GitHub API:
  - Software Agent SDK v1.54.0: `1d471742ea7be017d013eaaa3080f5d28d5490cb`
  - Agent Canvas v1.27.1: `f07aebdf5cdd71f4a05ebcf30f8bef5e4e3b70b9`

## Reason for restart

Windows reported that enabling WSL and Virtual Machine Platform requires a
restart. Docker's WSL2 backend and the Ubuntu distribution cannot be validated
until the new Windows feature state is loaded by the operating system.

## Resume checks

After restart:

1. Confirm WSL2 kernel and Ubuntu registration.
2. Complete Ubuntu first-run initialization without storing private identity in
   project files.
3. Confirm Docker Desktop uses the WSL2 backend.
4. Move or configure WSL/Docker data on the data drive before pulling images.
5. Pull and pin the Agent Server and pgvector images by digest.
6. Start services and execute database, REST, WebSocket, tool, pause, and resume
   verification.

This checkpoint is not a Stage 0 acceptance report and makes no claim that
Docker, PostgreSQL, or Agent Server is already operational.
