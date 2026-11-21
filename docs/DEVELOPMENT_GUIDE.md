# Development guide

Keep upstream OpenHands source untouched. Add platform code under `backend/`, `frontend/`, `agent/`, and `tests/`. Run Ruff and Pytest for backend changes and lint/test/build for frontend changes. Do not commit `.env`, runtime databases, logs, uploads, model weights, or credentials.
