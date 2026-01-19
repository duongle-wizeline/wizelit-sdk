def test_imports():
    # Simple import smoke test to ensure public symbols are available
    from wizelit_sdk.agent_wrapper import WizelitAgentWrapper, Job  # type: ignore

    assert WizelitAgentWrapper is not None
    assert Job is not None
