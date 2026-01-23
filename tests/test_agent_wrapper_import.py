def test_imports():
    # Simple import smoke test to ensure public symbols are available
    from wizelit_sdk.agent_wrapper import WizelitAgent, Job  # type: ignore

    assert WizelitAgent is not None
    assert Job is not None
