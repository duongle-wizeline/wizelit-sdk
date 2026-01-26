"""Agent Wrapper - Internal utility package."""

# Import main functions
from .agent_wrapper import WizelitAgent

# Backward-compatible alias used by sample MCP servers
WizelitAgentWrapper = WizelitAgent
from .job import Job
from .streaming import LogStreamer

__all__ = ["WizelitAgent", "WizelitAgentWrapper", "Job", "LogStreamer"]
