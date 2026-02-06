"""Agent Wrapper - Internal utility package."""

# Apply Accept header patch when this module is imported
# This ensures the patch is applied regardless of import path
try:
    from .agent_wrapper import _apply_fastmcp_accept_header_patch
    _apply_fastmcp_accept_header_patch()
except Exception:
    # Silently fail - patch will be applied when agent_wrapper module loads
    pass

# Import main functions
from .agent_wrapper import WizelitAgent
from .job import Job
from .streaming import LogStreamer

# Backward-compatible alias used by sample MCP servers
WizelitAgentWrapper = WizelitAgent

__all__ = ["WizelitAgent", "WizelitAgentWrapper", "Job", "LogStreamer"]
