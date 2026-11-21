import asyncio
from uuid import UUID

from backend.app.agent_gateway.client import AgentServerClient
from backend.app.agent_gateway.models import CreateAgentRun

from .store import WorkflowStore


class WorkflowExecutor:
    def __init__(
        self,
        store: WorkflowStore,
        gateway: AgentServerClient,
        max_concurrency: int = 2,
        step_timeout: float = 60,
    ) -> None:
        self.store = store
        self.gateway = gateway
        self.max_concurrency = max_concurrency
        self.step_timeout = step_timeout
        self._cancelled: set[str] = set()
        self._running: dict[str, UUID] = {}

    async def run(self, tenant_id: str, workflow_id: str) -> None:
        self.store.transition(tenant_id, workflow_id, "running", "executor")
        semaphore = asyncio.Semaphore(self.max_concurrency)
        while workflow_id not in self._cancelled:
            ready = [
                step
                for step in self.store.ready_steps(tenant_id, workflow_id)
                if not step["approval_required"]
            ]
            if not ready:
                state = self.store.get(tenant_id, workflow_id)
                if all(step["status"] == "succeeded" for step in state["steps"]):
                    self.store.transition(
                        tenant_id, workflow_id, "succeeded", "executor"
                    )
                return
            await asyncio.gather(
                *(
                    self._run_step(tenant_id, workflow_id, step, semaphore)
                    for step in ready
                )
            )
        self.store.transition(tenant_id, workflow_id, "cancelled", "executor")

    async def _run_step(
        self,
        tenant_id: str,
        workflow_id: str,
        step: dict[str, object],
        semaphore: asyncio.Semaphore,
    ) -> None:
        async with semaphore:
            step_id = str(step["id"])
            try:
                self.store.transition(
                    tenant_id, workflow_id, "running", "executor", step_id
                )
                handle = await asyncio.wait_for(
                    self.gateway.create_run(
                        CreateAgentRun(workspace="workspace", model="mock/mock")
                    ),
                    self.step_timeout,
                )
                self._running[step_id] = handle.openhands_id
                self.store.attach_conversation(
                    tenant_id, workflow_id, step_id, str(handle.openhands_id)
                )
                self.store.transition(
                    tenant_id, workflow_id, "succeeded", "agent", step_id
                )
                self._running.pop(step_id, None)
            except Exception:
                current = self.store.get(tenant_id, workflow_id)
                current_step = next(
                    item for item in current["steps"] if item["id"] == step_id
                )
                if current_step["retries"] < current_step["max_retries"]:
                    self.store.increment_retry(tenant_id, workflow_id, step_id)
                    self.store.transition(
                        tenant_id, workflow_id, "queued", "executor", step_id
                    )
                else:
                    self.store.transition(
                        tenant_id, workflow_id, "failed", "executor", step_id
                    )
                    self.store.transition(tenant_id, workflow_id, "failed", "executor")
                self._running.pop(step_id, None)

    async def cancel(self, tenant_id: str, workflow_id: str) -> None:
        self._cancelled.add(workflow_id)
        for conversation_id in self._running.values():
            await self.gateway.interrupt(conversation_id)
        self.store.transition(tenant_id, workflow_id, "cancelled", "user")

    async def resume(self, tenant_id: str, workflow_id: str) -> None:
        self._cancelled.discard(workflow_id)
        await self.run(tenant_id, workflow_id)
