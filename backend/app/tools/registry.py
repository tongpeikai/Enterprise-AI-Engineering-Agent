import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError


class ToolDenied(PermissionError):
    pass


class ToolExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolSpec:
    name: str
    input_model: type[BaseModel]
    handler: Any
    required_permission: str
    timeout_seconds: float = 10.0
    dangerous: bool = False


class ToolRegistry:
    def __init__(
        self,
        max_concurrency: int = 4,
        audit: Callable[[dict[str, object]], Awaitable[None] | None] | None = None,
    ) -> None:
        self._tools: dict[str, ToolSpec] = {}
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._audit = audit

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def schemas(self) -> list[dict[str, object]]:
        return [
            {
                "name": s.name,
                "permission": s.required_permission,
                "input_schema": s.input_model.model_json_schema(),
            }
            for s in self._tools.values()
        ]

    async def execute(
        self,
        name: str,
        arguments: dict[str, object],
        permissions: set[str],
        *,
        approval: bool = False,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> object:
        spec = self._tools.get(name)
        if spec is None or spec.required_permission not in permissions:
            raise ToolDenied("tool permission denied")
        if spec.dangerous and not approval:
            raise ToolDenied("explicit approval required")
        try:
            validated = spec.input_model.model_validate(arguments)
        except ValidationError as exc:
            raise ToolExecutionError("invalid tool arguments") from exc
        record = {
            "tool": name,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "approved": approval,
        }
        try:
            async with self._semaphore:
                result = spec.handler(validated)
                if inspect.isawaitable(result):
                    result = await asyncio.wait_for(
                        result, timeout=spec.timeout_seconds
                    )
                record["status"] = "succeeded"
                return result
        except TimeoutError as exc:
            record["status"] = "timeout"
            raise ToolExecutionError("tool timed out") from exc
        except Exception as exc:
            record["status"] = "failed"
            raise ToolExecutionError("tool failed") from exc
        finally:
            if self._audit is not None:
                event = self._audit(record)
                if inspect.isawaitable(event):
                    await event
