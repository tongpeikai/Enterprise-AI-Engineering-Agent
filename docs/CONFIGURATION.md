# Configuration

Runtime secrets belong only in an ignored `.env`. Required compose values are `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `AGENT_SERVER_SESSION_API_KEY`, and `AUTH_SIGNING_KEY`. `AGENT_SERVER_URL` and SQLite paths are injected by compose. Never place credentials in source, reports, screenshots, or Git history.
