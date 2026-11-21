# Troubleshooting

If startup waits, run `docker compose -f deploy/compose.stage10.yml ps` and inspect service logs. Ensure Docker Desktop is using Linux containers and that ports 5173 and 8000 are free. If Agent Server is unavailable, verify the pinned image can be pulled and that `AGENT_SERVER_SESSION_API_KEY` matches the local value. Stop/restart preserves named volumes.
