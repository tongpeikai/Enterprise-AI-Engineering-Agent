# API Surface

Current application routes include:

- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/revoke`
- `GET/POST /api/v1/projects`
- `GET/POST /api/v1/tasks`, `GET /api/v1/tasks/{task_id}`, `POST /api/v1/tasks/{task_id}/transition`
- `GET /api/v1/tools`, `POST /api/v1/tools/{name}/execute`
- `GET /api/v1/agent/server-info`, `POST /api/v1/agent/runs`

Protected routes require `Authorization: Bearer <access-token>`.
