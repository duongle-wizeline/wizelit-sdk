"""Public API tests for agent_wrapper."""

import wizelit_sdk.agent_wrapper as agent_wrapper


def test_agent_wrapper_public_api_is_minimal():
    """Ensure placeholder utilities are not exposed via the public API."""
    assert not hasattr(agent_wrapper, "greet")
    assert not hasattr(agent_wrapper, "greet_many")
    assert not hasattr(agent_wrapper, "greet_many3")


def test_agent_wrapper_exports_core_symbols():
    """Ensure core classes remain publicly available."""
    assert agent_wrapper.WizelitAgent is not None
    assert agent_wrapper.Job is not None
    assert agent_wrapper.LogStreamer is not None

