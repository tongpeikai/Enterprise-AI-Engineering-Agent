import asyncio
import json
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import httpx
import websockets
from pydantic import BaseModel

from .events import EventCursor
from .models import AgentServerError, CreateAgentRun, RuntimeEvent, RuntimeHandle


class AgentServerClient:
    def __init__(
        self,
        base_url: str,
        session_api_key: str,
        http: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session_api_key = session_api_key
        self._http = http

    async def _request(
        self, method: str, path: str, body: BaseModel | dict[str, object] | None = None
    ) -> dict[str, object]:
        client = self._http or httpx.AsyncClient(base_url=self.base_url, timeout=30)
        owns_client = self._http is None
        try:
            response = await client.request(
                method,
                path,
                headers={"X-Session-API-Key": self.session_api_key},
                json=(
                    body.model_dump(exclude_none=True)
                    if isinstance(body, BaseModel)
                    else body
                ),
            )
            if response.is_error:
                raise AgentServerError(
                    f"Agent Server returned HTTP {response.status_code}"
                )
            return response.json()
        finally:
            if owns_client:
                await client.aclose()

    async def server_info(self) -> dict[str, object]:
        return await self._request("GET", "/server_info")

    async def create_run(self, request: CreateAgentRun) -> RuntimeHandle:
        payload: dict[str, object] = {
            "workspace": {"working_dir": request.workspace},
            "agent_settings": {"llm": {"model": request.model}},
            "autotitle": False,
        }
        if request.initial_message is not None:
            payload["initial_message"] = {
                "role": "user",
                "content": [{"type": "text", "text": request.initial_message}],
            }
        data = await self._request("POST", "/api/conversations", payload)
        return RuntimeHandle(
            run_id=uuid4(),
            openhands_id=UUID(str(data["id"])),
            status=str(data["execution_status"]),
        )

    async def interrupt(self, openhands_id: UUID) -> None:
        await self._request("POST", f"/api/conversations/{openhands_id}/interrupt")

    async def approve(self, openhands_id: UUID, event_id: str, approve: bool) -> None:
        await self._request(
            "POST",
            f"/api/conversations/{openhands_id}/events/respond_to_confirmation",
            {"event_id": event_id, "confirm": approve},
        )

    async def stream_events(
        self,
        openhands_id: UUID,
        cursor: str | None = None,
        retries: int = 3,
    ) -> AsyncIterator[RuntimeEvent]:
        url = self.base_url.replace("https://", "wss://").replace("http://", "ws://")
        event_cursor = EventCursor(cursor)
        for attempt in range(retries + 1):
            try:
                async with websockets.connect(
                    f"{url}/sockets/events/{openhands_id}"
                ) as socket:
                    await socket.send(
                        json.dumps(
                            {"type": "auth", "session_api_key": self.session_api_key}
                        )
                    )
                    async for raw in socket:
                        data = json.loads(raw)
                        event = RuntimeEvent(
                            event_id=str(data.get("id", "")),
                            event_type=str(
                                data.get("key", data.get("type", "unknown"))
                            ),
                            payload=data if isinstance(data, dict) else {"value": data},
                        )
                        if event_cursor.accept(event):
                            yield event
                return
            except (OSError, websockets.WebSocketException):
                if attempt >= retries:
                    raise AgentServerError(
                        "Agent Server WebSocket disconnected after retries"
                    ) from None
                await asyncio.sleep(min(2**attempt, 8))
