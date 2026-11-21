import sys

import pytest

from backend.app.tools.mcp_client import LocalMCPClient


@pytest.mark.asyncio
async def test_local_mcp_list_and_call() -> None:
    client = LocalMCPClient([sys.executable, "scripts/local_mcp_server.py"])
    tools = await client.call("tools/list", {})
    assert tools["tools"][0]["name"] == "echo"
    result = await client.call(
        "tools/call", {"name": "echo", "arguments": {"text": "mcp-ok"}}
    )
    assert result["content"][0]["text"] == "mcp-ok"
