import pytest
from pydantic import BaseModel

from backend.app.tools.mcp import MCPRegistry, MCPServerConfig
from backend.app.tools.registry import (
    ToolDenied,
    ToolExecutionError,
    ToolRegistry,
    ToolSpec,
)


class EchoInput(BaseModel):
    text: str


@pytest.mark.asyncio
async def test_registry_validates_permissions_and_timeout() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("echo", EchoInput, lambda value: value.text, "tool.echo")
    )
    assert await registry.execute("echo", {"text": "ok"}, {"tool.echo"}) == "ok"
    with pytest.raises(ToolDenied):
        await registry.execute("echo", {"text": "ok"}, set())
    with pytest.raises(ToolExecutionError):
        await registry.execute("echo", {"wrong": "x"}, {"tool.echo"})


def test_mcp_requires_explicit_approval() -> None:
    registry = MCPRegistry()
    with pytest.raises(PermissionError):
        registry.add("unsafe", MCPServerConfig(command="server"))
    registry.add("safe", MCPServerConfig(command="server", allowed=True))
    assert "safe" in registry.list()
