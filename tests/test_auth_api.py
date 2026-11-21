from fastapi.testclient import TestClient

from backend.app.auth.service import AuthService
from backend.app.main import create_app


def test_refresh_rotation_and_project_tenant_isolation(tmp_path) -> None:
    auth = AuthService(tmp_path / "auth.sqlite", "test-signing-key")
    app = create_app(auth=auth)
    client = TestClient(app)
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "a@example.test",
            "password": "strong-password-123",
            "organization_id": "a",
        },
    )
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "b@example.test",
            "password": "strong-password-123",
            "organization_id": "b",
        },
    )
    first = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.test", "password": "strong-password-123"},
    ).json()
    rotated = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]}
    )
    assert rotated.status_code == 200
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]}
        ).status_code
        == 401
    )
    project = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {rotated.json()['access_token']}"},
        json={"name": "A", "repository": "synthetic"},
    )
    assert project.status_code == 200
    second = client.post(
        "/api/v1/auth/login",
        json={"email": "b@example.test", "password": "strong-password-123"},
    ).json()
    projects = client.get(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {second['access_token']}"},
    )
    assert projects.json() == []
