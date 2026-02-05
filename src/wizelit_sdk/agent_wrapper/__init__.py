"""Agent Wrapper - Internal utility package."""

# Import main functions
from .agent_wrapper import WizelitAgent
from .job import Job
from .streaming import LogStreamer

# Backward-compatible alias used by sample MCP servers
WizelitAgentWrapper = WizelitAgent

__all__ = ["WizelitAgent", "WizelitAgentWrapper", "Job", "LogStreamer"]
