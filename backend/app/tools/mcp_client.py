import asyncio
import json


class MCPClientError(RuntimeError):
    pass


class LocalMCPClient:
    def __init__(self, command: list[str], timeout: float = 5) -> None:
        self.command = command
        self.timeout = timeout

    async def call(self, method: str, params: dict[str, object]) -> dict[str, object]:
        process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        request = json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        )
        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate((request + "\n").encode()), self.timeout
            )
        except TimeoutError:
            process.kill()
            await process.wait()
            raise MCPClientError("MCP call timed out") from None
        if process.returncode != 0:
            raise MCPClientError("MCP server exited with an error")
        try:
            response = json.loads(stdout.decode().splitlines()[0])
        except (IndexError, json.JSONDecodeError) as exc:
            raise MCPClientError("invalid MCP response") from exc
        if "error" in response:
            raise MCPClientError(str(response["error"]))
        return response["result"]
