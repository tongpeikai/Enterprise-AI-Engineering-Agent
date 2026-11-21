from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    command: str = Field(min_length=1)
    args: list[str] = Field(default_factory=list)
    allowed: bool = False


class MCPRegistry:
    def __init__(self) -> None:
        self._servers: dict[str, MCPServerConfig] = {}

    def add(self, name: str, config: MCPServerConfig) -> None:
        if not config.allowed:
            raise PermissionError("MCP server requires explicit approval")
        self._servers[name] = config

    def list(self) -> dict[str, MCPServerConfig]:
        return self._servers.copy()
