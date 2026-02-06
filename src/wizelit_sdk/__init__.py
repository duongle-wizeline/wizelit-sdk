"""Wizelit SDK package."""

# Apply Accept header patch at package level to ensure it runs regardless of import path
try:
    from wizelit_sdk.agent_wrapper.agent_wrapper import _apply_fastmcp_accept_header_patch
    _apply_fastmcp_accept_header_patch()
except Exception:
    # Silently fail - patch will be retried when agent_wrapper is imported
    pass

from wizelit_sdk.agent_wrapper import WizelitAgent
from wizelit_sdk.database import DatabaseManager
from wizelit_sdk.agent_wrapper.job import Job
from wizelit_sdk.agent_wrapper.streaming import LogStreamer
from wizelit_sdk.models.base import BaseModel
from wizelit_sdk.models.job import JobModel, JobLogModel, JobStatus
from wizelit_sdk.exceptions import (
    WizelitSDKException,
    AgentInitializationError,
    SignatureValidationError,
    JobExecutionError,
    JobNotFoundError,
    ToolRegistrationError,
    DatabaseManagerError,
    StreamingError,
    ContextVariableError,
    InvalidConfigError,
    TransportError,
    TimeoutError,
)

__all__ = [
    "WizelitAgent",
    "DatabaseManager",
    "Job",
    "LogStreamer",
    "BaseModel",
    "JobModel",
    "JobLogModel",
    "JobStatus",
    # Exceptions
    "WizelitSDKException",
    "AgentInitializationError",
    "SignatureValidationError",
    "JobExecutionError",
    "JobNotFoundError",
    "ToolRegistrationError",
    "DatabaseManagerError",
    "StreamingError",
    "ContextVariableError",
    "InvalidConfigError",
    "TransportError",
    "TimeoutError",
]

