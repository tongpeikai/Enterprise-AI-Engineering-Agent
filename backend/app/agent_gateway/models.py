from uuid import UUID

from pydantic import BaseModel, Field


class CreateAgentRun(BaseModel):
    workspace: str = Field(min_length=1)
    model: str = "mock/mock"
    initial_message: str | None = None


class RuntimeHandle(BaseModel):
    run_id: UUID
    openhands_id: UUID
    status: str


class RuntimeEvent(BaseModel):
    event_id: str
    event_type: str
    payload: dict[str, object]


class AgentServerError(RuntimeError):
    """An upstream request failed without exposing credentials."""
