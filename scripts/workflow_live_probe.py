import asyncio
import os
from pathlib import Path

from backend.app.agent_gateway.client import AgentServerClient
from backend.app.workflow.executor import WorkflowExecutor
from backend.app.workflow.store import WorkflowStore


async def main() -> None:
    path = Path(".tmp/workflow-live.sqlite")
    path.parent.mkdir(exist_ok=True)
    store = WorkflowStore(path)
    workflow_id = store.create("stage6", "live", [{"name": "agent"}])
    client = AgentServerClient(
        "http://127.0.0.1:8010", os.environ["AGENT_SERVER_SESSION_API_KEY"]
    )
    await WorkflowExecutor(store, client).run("stage6", workflow_id)
    state = store.get("stage6", workflow_id)
    print(f"workflow={state['status']} conversation={state['steps'][0]['conversation_id']}")


if __name__ == "__main__":
    asyncio.run(main())
