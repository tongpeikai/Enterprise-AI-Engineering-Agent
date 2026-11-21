import pytest

from backend.app.auth.service import AuthError, AuthService, require_role


def test_register_login_and_tenant_claim(tmp_path) -> None:
    service = AuthService(tmp_path / "auth.sqlite", "test-signing-key")
    user_id = service.register("person@example.test", "strong-password-123", "org-a")
    claims = service.verify(service.login("person@example.test", "strong-password-123"))
    assert claims["sub"] == user_id
    assert claims["org"] == "org-a"
    assert claims["role"] == "member"


def test_invalid_password_and_role_are_rejected(tmp_path) -> None:
    service = AuthService(tmp_path / "auth.sqlite", "test-signing-key")
    service.register("person@example.test", "strong-password-123", "org-a")
    with pytest.raises(AuthError):
        service.login("person@example.test", "wrong-password")
    with pytest.raises(AuthError):
        require_role({"role": "member"}, "admin")
