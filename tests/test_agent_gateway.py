from uuid import uuid4

import httpx
import pytest

from backend.app.agent_gateway.client import AgentServerClient
from backend.app.agent_gateway.events import EventCursor
from backend.app.agent_gateway.models import CreateAgentRun, RuntimeEvent, RuntimeHandle
from backend.app.agent_gateway.store import RunStore


@pytest.mark.asyncio
async def test_create_run_maps_request_and_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/conversations"
        assert request.headers["X-Session-API-Key"] == "test-key"
        body = await request.aread()
        assert b"mock/mock" in body
        return httpx.Response(
            200,
            json={
                "id": "11111111-1111-1111-1111-111111111111",
                "execution_status": "idle",
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="http://test"
    ) as http:
        result = await AgentServerClient("http://test", "test-key", http).create_run(
            CreateAgentRun(workspace="workspace")
        )
    assert str(result.openhands_id) == "11111111-1111-1111-1111-111111111111"
    assert result.status == "idle"


def test_store_persists_run_and_cursor(tmp_path) -> None:
    store = RunStore(tmp_path / "runs.sqlite")
    handle = RuntimeHandle(
        run_id=uuid4(),
        openhands_id=uuid4(),
        status="idle",
    )
    store.save(handle, attempt=2)
    store.update_cursor(handle.run_id, "event-2")

    record = store.get(handle.run_id)
    assert record is not None
    assert record["attempt"] == 2
    assert record["cursor"] == "event-2"


def test_event_cursor_deduplicates_ids() -> None:
    cursor = EventCursor()
    event = RuntimeEvent(event_id="event-1", event_type="state", payload={})
    assert cursor.accept(event)
    assert not cursor.accept(event)
