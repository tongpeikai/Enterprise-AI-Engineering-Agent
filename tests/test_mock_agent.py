from agent.mock import DeterministicMockAgent


def test_mock_agent_runs_tool_and_records_ordered_events() -> None:
    agent = DeterministicMockAgent(lambda args: args["text"].upper())

    assert agent.run("stage0") == "mock result: STAGE0"
    assert [event["type"] for event in agent.events] == [
        "user_message",
        "tool_call",
        "tool_result",
        "agent_final",
    ]
