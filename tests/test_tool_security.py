import asyncio

import pytest
from pydantic import BaseModel

from backend.app.tools.registry import (
    ToolDenied,
    ToolExecutionError,
    ToolRegistry,
    ToolSpec,
)
from backend.app.tools.sandbox import DockerSandbox
from backend.app.tools.security import UnsafePath, command_allowed, safe_workspace_path


class Input(BaseModel):
    value: str


@pytest.mark.asyncio
async def test_dangerous_approval_audit_and_timeout() -> None:
    events = []
    registry = ToolRegistry(audit=events.append)
    registry.register(
        ToolSpec("danger", Input, lambda value: "ok", "tool.execute", dangerous=True)
    )
    with pytest.raises(ToolDenied):
        await registry.execute("danger", {"value": "x"}, {"tool.execute"})
    assert (
        await registry.execute(
            "danger",
            {"value": "x"},
            {"tool.execute"},
            approval=True,
            tenant_id="org",
            user_id="u",
        )
        == "ok"
    )
    assert events[-1]["status"] == "succeeded"

    async def slow(_: Input) -> str:
        await asyncio.sleep(1)
        return "late"

    registry.register(
        ToolSpec("slow", Input, slow, "tool.execute", timeout_seconds=0.01)
    )
    with pytest.raises(ToolExecutionError):
        await registry.execute("slow", {"value": "x"}, {"tool.execute"})


def test_path_and_command_policies(tmp_path) -> None:
    assert (
        safe_workspace_path(tmp_path, "nested/file.txt").parent == tmp_path / "nested"
    )
    with pytest.raises(UnsafePath):
        safe_workspace_path(tmp_path, "../secret")
    assert command_allowed("pytest tests", {"pytest"}, {"rm", "curl"})
    assert not command_allowed("rm -rf /", {"rm"}, {"rm"})


@pytest.mark.asyncio
async def test_docker_sandbox_real_container() -> None:
    result = await DockerSandbox().run("python -c 'print(\"sandbox-ok\")'")
    assert result.exit_code == 0
    assert "sandbox-ok" in result.stdout
