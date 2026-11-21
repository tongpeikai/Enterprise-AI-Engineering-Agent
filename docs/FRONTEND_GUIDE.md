# Frontend Guide

From `frontend/`, run `npm install`, then `npm run dev`. Set `VITE_API_BASE_URL` when the backend is not at `http://127.0.0.1:8000/api/v1`. The console uses session-scoped access/refresh tokens, calls the protected FastAPI routes, and renders explicit empty states when the backend has no records. `npm run lint` and `npm run build` are the local quality gates.
