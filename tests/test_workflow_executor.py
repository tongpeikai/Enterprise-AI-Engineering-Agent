from uuid import UUID

import pytest

from backend.app.agent_gateway.models import RuntimeHandle
from backend.app.workflow.executor import WorkflowExecutor
from backend.app.workflow.store import WorkflowStore


class Gateway:
    def __init__(self) -> None:
        self.interrupted = []

    async def create_run(self, request):
        return RuntimeHandle(
            run_id=UUID("11111111-1111-1111-1111-111111111111"),
            openhands_id=UUID("22222222-2222-2222-2222-222222222222"),
            status="idle",
        )

    async def interrupt(self, conversation_id):
        self.interrupted.append(conversation_id)


@pytest.mark.asyncio
async def test_executor_runs_dag_and_persists_conversation(tmp_path) -> None:
    store = WorkflowStore(tmp_path / "workflow.sqlite")
    workflow_id = store.create(
        "org-a", "build", [{"name": "one"}, {"name": "two", "depends_on": ["one"]}]
    )
    await WorkflowExecutor(store, Gateway()).run("org-a", workflow_id)
    state = store.get("org-a", workflow_id)
    assert state["status"] == "succeeded"
    assert all(step["status"] == "succeeded" for step in state["steps"])
    assert all(step["conversation_id"] for step in state["steps"])


def test_recover_running_steps(tmp_path) -> None:
    store = WorkflowStore(tmp_path / "workflow.sqlite")
    workflow_id = store.create("org-a", "recover", [{"name": "one"}])
    store.transition("org-a", workflow_id, "running", "worker")
    step_id = store.get("org-a", workflow_id)["steps"][0]["id"]
    store.transition("org-a", workflow_id, "running", "worker", step_id)
    assert store.recover_running("org-a", workflow_id) == 1
    assert store.get("org-a", workflow_id)["steps"][0]["status"] == "queued"
