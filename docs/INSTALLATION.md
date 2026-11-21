# Installation

Use Docker Desktop on Windows with Linux containers. Copy `.env.example` to `.env`, set local random values, then run `scripts/stage10-start.ps1`. The script builds the backend/frontend images and starts PostgreSQL, Agent Server, backend, and frontend with health checks. `scripts/stage10-stop.ps1` stops the stack without deleting volumes.

For local development, run `uv sync`, `uv run uvicorn backend.app.main:app --reload`, and `npm ci && npm run dev` in `frontend/`.
