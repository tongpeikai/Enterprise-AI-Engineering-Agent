from uuid import UUID

from fastapi.testclient import TestClient

from backend.app.agent_gateway.models import RuntimeHandle
from backend.app.auth.service import AuthService
from backend.app.main import create_app
from backend.app.tasks.store import TaskStore


class FakeGateway:
    async def create_run(self, request):
        return RuntimeHandle(
            run_id=UUID("11111111-1111-1111-1111-111111111111"),
            openhands_id=UUID("22222222-2222-2222-2222-222222222222"),
            status="idle",
        )

    async def interrupt(self, conversation_id):
        assert str(conversation_id) == "22222222-2222-2222-2222-222222222222"


def test_task_api_connects_gateway_and_isolates_tenants(tmp_path) -> None:
    auth = AuthService(tmp_path / "auth.sqlite", "test-key")
    auth.register("a@example.test", "strong-password-123", "org-a")
    auth.register("b@example.test", "strong-password-123", "org-b")
    app = create_app(FakeGateway(), auth, TaskStore(tmp_path / "tasks.sqlite"))
    client = TestClient(app)
    token_a = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.test", "password": "strong-password-123"},
    ).json()["access_token"]
    token_b = client.post(
        "/api/v1/auth/login",
        json={"email": "b@example.test", "password": "strong-password-123"},
    ).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    created = client.post(
        "/api/v1/tasks", headers=headers_a, json={"title": "run tests"}
    )
    assert created.status_code == 200
    task_id = created.json()["id"]
    assert client.get("/api/v1/tasks", headers=headers_b).json() == []
    assert (
        client.post(
            f"/api/v1/tasks/{task_id}/transition",
            headers=headers_b,
            json={"status": "cancelled"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/v1/tasks/{task_id}/transition",
            headers=headers_a,
            json={"status": "cancelled"},
        ).status_code
        == 200
    )
