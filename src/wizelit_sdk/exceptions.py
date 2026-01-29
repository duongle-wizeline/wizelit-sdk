"""
Custom exceptions for Wizelit SDK with helpful error messages and suggestions.
"""


class WizelitSDKException(Exception):
    """Base exception class for all Wizelit SDK errors."""

    def __init__(self, message: str, suggestion: str = ""):
        self.message = message
        self.suggestion = suggestion
        full_message = message
        if suggestion:
            full_message = f"{message}\n💡 Suggestion: {suggestion}"
        super().__init__(full_message)


class AgentInitializationError(WizelitSDKException):
    """Raised when WizelitAgent cannot be initialized."""

    def __init__(self, reason: str = "", original_error: str = ""):
        message = "Failed to initialize WizelitAgent"
        if reason:
            message += f": {reason}"
        if original_error:
            message += f" ({original_error})"
        suggestion = (
            "1. Verify all required dependencies are installed\n"
            "2. Check that the name parameter is provided\n"
            "3. Verify the transport mode is valid (sse, http, streamable-http, stdio)\n"
            "4. Check that host and port are available and not in use\n"
            "5. Review the initialization code for configuration errors"
        )
        super().__init__(message, suggestion)


class SignatureValidationError(WizelitSDKException):
    """Raised when a function signature doesn't meet requirements."""

    def __init__(self, function_name: str, reason: str = ""):
        message = f"Signature validation failed for function '{function_name}'"
        if reason:
            message += f": {reason}"
        suggestion = (
            f"1. Ensure all parameters of '{function_name}' have type hints\n"
            f"2. Verify parameter names match between definition and usage\n"
            f"3. Check that the function signature is compatible with the ingest decorator\n"
            f"4. Ensure complex types are properly imported and defined\n"
            f"5. Review the decorator parameters for compatibility"
        )
        super().__init__(message, suggestion)


class JobExecutionError(WizelitSDKException):
    """Raised when a job fails during execution."""

    def __init__(self, job_id: str, reason: str = "", original_error: str = ""):
        message = f"Job execution failed for job_id '{job_id}'"
        if reason:
            message += f": {reason}"
        if original_error:
            message += f" ({original_error})"
        suggestion = (
            "1. Check the job logs for detailed error information\n"
            "2. Verify job inputs are valid and complete\n"
            "3. Check if the underlying tool/function has dependencies\n"
            "4. Try running the job again with the same inputs\n"
            "5. Check application logs and database logs for more context"
        )
        super().__init__(message, suggestion)


class JobNotFoundError(WizelitSDKException):
    """Raised when a job cannot be found."""

    def __init__(self, job_id: str):
        message = f"Job not found: {job_id}"
        suggestion = (
            "1. Verify the job_id is correct and complete\n"
            "2. Check if the job has expired or been deleted\n"
            "3. Verify the job was created in the current session\n"
            "4. Check the database for job records\n"
            "5. Review job retention policies"
        )
        super().__init__(message, suggestion)


class ToolRegistrationError(WizelitSDKException):
    """Raised when a tool cannot be registered with the MCP server."""

    def __init__(self, tool_name: str, reason: str = ""):
        message = f"Failed to register tool '{tool_name}' with MCP server"
        if reason:
            message += f": {reason}"
        suggestion = (
            f"1. Verify '{tool_name}' function is properly decorated with @ingest\n"
            f"2. Check that function name is unique across all registered tools\n"
            f"3. Verify function signature is valid with type hints\n"
            f"4. Check for duplicate tool registrations\n"
            f"5. Ensure the FastMCP server is properly initialized"
        )
        super().__init__(message, suggestion)


class DatabaseManagerError(WizelitSDKException):
    """Raised when database operations fail."""

    def __init__(self, operation: str, reason: str = ""):
        message = f"Database operation failed: {operation}"
        if reason:
            message += f" ({reason})"
        suggestion = (
            "1. Verify the database is running and accessible\n"
            "2. Check database connection parameters (host, port, credentials)\n"
            "3. Verify the database has sufficient disk space\n"
            "4. Check if the database tables are properly initialized\n"
            "5. Review database logs for detailed error information"
        )
        super().__init__(message, suggestion)


class StreamingError(WizelitSDKException):
    """Raised when log streaming fails."""

    def __init__(self, reason: str = "", original_error: str = ""):
        message = "Error in log streaming"
        if reason:
            message += f": {reason}"
        if original_error:
            message += f" ({original_error})"
        suggestion = (
            "1. Verify Redis is running and accessible\n"
            "2. Check REDIS_URL environment variable is set correctly\n"
            "3. Verify network connectivity to Redis\n"
            "4. Check Redis logs for connection errors\n"
            "5. Log streaming is optional - the SDK will continue without it"
        )
        super().__init__(message, suggestion)


class ContextVariableError(WizelitSDKException):
    """Raised when context variable operations fail."""

    def __init__(self, variable_name: str, reason: str = ""):
        message = f"Error accessing context variable '{variable_name}'"
        if reason:
            message += f": {reason}"
        suggestion = (
            f"1. Ensure '{variable_name}' is set before accessing\n"
            f"2. Verify the context is active in the current async task\n"
            f"3. Check if using the decorator or dependency injection correctly\n"
            f"4. Ensure context propagation across async calls\n"
            f"5. Review context variable usage documentation"
        )
        super().__init__(message, suggestion)


class InvalidConfigError(WizelitSDKException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, config_key: str, expected_type: str = "", reason: str = ""):
        message = f"Invalid configuration for '{config_key}'"
        if expected_type:
            message += f" (expected: {expected_type})"
        if reason:
            message += f": {reason}"
        suggestion = (
            f"1. Verify {config_key} is set in environment variables\n"
            f"2. Check the value format and type\n"
            f"3. Review configuration documentation for valid values\n"
            f"4. Check .env file or deployment configuration\n"
            f"5. Restart the application after fixing configuration"
        )
        super().__init__(message, suggestion)


class TransportError(WizelitSDKException):
    """Raised when transport/communication errors occur."""

    def __init__(self, transport_type: str, reason: str = ""):
        message = f"Transport error with '{transport_type}'"
        if reason:
            message += f": {reason}"
        suggestion = (
            f"1. Verify the {transport_type} transport is properly configured\n"
            f"2. Check network connectivity and firewall rules\n"
            f"3. Verify server ports are open and accessible\n"
            f"4. Check if there are proxy or routing issues\n"
            f"5. Review transport-specific logs for detailed information"
        )
        super().__init__(message, suggestion)


class TimeoutError(WizelitSDKException):
    """Raised when an operation exceeds the timeout limit."""

    def __init__(self, operation: str, timeout_seconds: float):
        message = f"Operation '{operation}' exceeded timeout of {timeout_seconds} seconds"
        suggestion = (
            f"1. The {operation} took too long to complete\n"
            f"2. Check if there are resource constraints (CPU, memory)\n"
            f"3. Simplify the job inputs or query\n"
            f"4. Check application and system logs for bottlenecks\n"
            f"5. Consider increasing timeout if the operation is expected to be slow"
        )
        super().__init__(message, suggestion)
