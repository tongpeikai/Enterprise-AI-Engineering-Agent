# Final deployment guide

1. Copy `.env.example` to `.env` and set local-only random values.
2. Run `./scripts/stage10-start.ps1` from PowerShell.
3. Open `http://127.0.0.1:5173`; backend is at `http://127.0.0.1:8000`.
4. Check `docker compose --env-file .env -f deploy/compose.stage10-lite.yml ps`.
5. Stop with `./scripts/stage10-stop.ps1`.

The Lite profile runs Backend and Frontend in isolated resources and connects to the already-running Stage 0 Agent Server at host port 8010 and pgvector/PostgreSQL at 5433. This is intentional for the current 1.9 GiB Docker limit and preserves Stage 0 data. The original `compose.stage10.yml` starts duplicate infrastructure and is intended for a higher-memory machine.
