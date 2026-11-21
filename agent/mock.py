from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MockResponse:
    text: str
    tool_name: str | None = None
    tool_args: dict[str, str] = field(default_factory=dict)


class DeterministicMockAgent:
    """Small, provider-free harness for validating gateway orchestration."""

    def __init__(self, tool: Callable[[dict[str, str]], str]) -> None:
        self._tool = tool
        self.events: list[dict[str, object]] = []

    def run(self, prompt: str) -> str:
        self.events.append({"type": "user_message", "text": prompt})
        response = MockResponse(
            text="mock tool request",
            tool_name="echo",
            tool_args={"text": prompt},
        )
        self.events.append(
            {
                "type": "tool_call",
                "name": response.tool_name,
                "args": response.tool_args,
            }
        )
        result = self._tool(response.tool_args)
        self.events.append(
            {"type": "tool_result", "name": response.tool_name, "result": result}
        )
        final = f"mock result: {result}"
        self.events.append({"type": "agent_final", "text": final})
        return final
