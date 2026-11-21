import asyncio
import os

from backend.app.agent_gateway.client import AgentServerClient
from backend.app.agent_gateway.models import CreateAgentRun


async def main() -> None:
    client = AgentServerClient(
        "http://127.0.0.1:8010", os.environ["AGENT_SERVER_SESSION_API_KEY"]
    )
    info = await client.server_info()
    handle = await client.create_run(CreateAgentRun(workspace="workspace/stage1"))
    print(f"server={info['version']} run={handle.openhands_id} status={handle.status}")


if __name__ == "__main__":
    asyncio.run(main())
