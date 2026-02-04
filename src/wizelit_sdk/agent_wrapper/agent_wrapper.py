# wizelit_sdk/core.py
import asyncio
import inspect
import logging
import os
from typing import Callable, Any, Optional, Literal, Dict, TYPE_CHECKING, Union, cast
from contextvars import ContextVar
from fastmcp import FastMCP, Context
from fastmcp.dependencies import CurrentContext
from wizelit_sdk.agent_wrapper.job import Job
from wizelit_sdk.agent_wrapper.signature_validation import (
    SignatureValidationError,
    bind_and_validate_arguments,
    ensure_type_hints,
)
from wizelit_sdk.exceptions import (
    StreamingError,
)

# Local Transport literal to avoid import issues when fastmcp.types is unavailable
Transport = Literal["stdio", "http", "sse", "streamable-http"]

if TYPE_CHECKING:
    from wizelit_sdk.database import DatabaseManager

# Reusable framework constants
LLM_FRAMEWORK_CREWAI = "crewai"
LLM_FRAMEWORK_LANGCHAIN = "langchain"
LLM_FRAMEWORK_LANGGRAPH = "langraph"

LlmFrameworkType = Literal["crewai", "langchain", "langraph", None]

# Context variable for current Job instance
_current_job: ContextVar[Optional[Job]] = ContextVar("_current_job", default=None)


class CurrentJob:
    """
    Dependency injection class for Job instances.
    Similar to CurrentContext(), returns the current Job instance from context.
    """

    def __call__(self) -> Optional[Job]:
        """Return the current Job instance from context."""
        return _current_job.get()


class WizelitAgent:
    """
    Main wrapper class that converts Python functions into MCP server tools.
    Built on top of fast-mcp with enhanced streaming and agent framework support.
    """

    def __init__(
        self,
        name: str,
        transport: str = "streamable-http",
        host: str = "0.0.0.0",
        port: int = 8080,
        version: str = "1.0.0",
        db_manager: Optional["DatabaseManager"] = None,
        enable_streaming: bool = True,
    ):
        """
        Initialize the Wizelit Agent.

        Args:
            name: Name of the MCP server
            transport: Transport protocol (sse, streamable-http, stdio)
            host: Host address
            port: Port number
            version: Version string for the server
            db_manager: Optional DatabaseManager for job persistence
            enable_streaming: Enable real-time log streaming via Redis
        """
        self._mcp = FastMCP(name=name)
        self._name = name
        self._version = version
        self._tools = {}
        self._jobs: Dict[str, Job] = {}  # Store jobs by job_id
        self._host = host
        self._transport: Transport = cast(Transport, transport)
        self._port = port
        self._db_manager = db_manager
        self._log_streamer = None

        # Initialize log streamer if enabled
        if enable_streaming:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            try:
                from .streaming import LogStreamer

                self._log_streamer = LogStreamer(redis_url)
                print(f"Log streaming enabled via Redis: {redis_url}")
            except ImportError:
                print("Warning: redis package not installed. Log streaming disabled.")
            except Exception as e:
                raise StreamingError(
                    "Failed to initialize log streaming",
                    f"Could not connect to Redis at {redis_url}: {str(e)}"
                )

        print(
            f"WizelitAgent initialized with name: {name}, transport: {transport}, host: {host}, port: {port}"
        )

    def ingest(
        self,
        is_long_running: bool = False,
        description: Optional[str] = None,
        response_handling: Optional[Dict[str, Any]] = None,
    ):
        """
        Decorator to convert a function into an MCP tool.

        Args:
            is_long_running: If True, enables progress reporting
            description: Human-readable description of the tool
            response_handling: Optional dict configuring how tool responses are handled:
                {
                    "mode": "direct" | "formatted" | "default",  # Default: "default"
                    "extract_path": "content[0].text",  # Optional: path to extract value. Default: "content[0].text" (MCP format)
                    "template": "Message: {value}",  # Optional: template for formatted mode. Default: "{value}"
                    "content_type": "text" | "json" | "auto"  # Default: "text"
                }

                Mode options:
                - "direct": Return response directly to user (bypass LLM processing)
                - "formatted": Format response using template before returning to user
                - "default": Normal LLM processing (let LLM interpret and respond)

                Content type options:
                - "text": Always convert content to plain string using str(). Use for human-readable text responses.
                  Example: "Hello world" -> "Hello world", {"key": "value"} -> "{'key': 'value'}"

                - "json": Format content as pretty-printed JSON. If content is a string, tries to parse it as JSON first.
                  Use when you want structured data displayed as formatted JSON.
                  Example: {"key": "value"} -> '{\n  "key": "value"\n}', "Hello" -> "Hello" (if not valid JSON)

                - "auto": Smart formatting - strings returned as-is, dicts/lists converted to JSON, other types to string.
                  Use when content type is unknown or mixed.
                  Example: "Hello" -> "Hello", {"key": "value"} -> '{\n  "key": "value"\n}', 123 -> "123"

        Usage:
            @agent.ingest(
                is_long_running=True,
                description="Start a job",
                response_handling={
                    "mode": "formatted",
                    "extract_path": "content[0].text",
                    "template": "Job started. ID: {value}",
                    "content_type": "text"
                }
            )
            def start_job(code: str, job: Job) -> str:
                return job.id
        """

        def decorator(func: Callable) -> Callable:
            # Store original function metadata
            tool_name = func.__name__
            tool_description = description or func.__doc__ or f"Execute {tool_name}"

            # Detect if function is async
            is_async = inspect.iscoroutinefunction(func)

            # Get function signature
            sig = inspect.signature(func)

            # Build new signature with ctx: Context = CurrentContext() as LAST parameter
            # This follows fast-mcp v2.14+ convention for dependency injection
            params_list = list(sig.parameters.values())

            # Check if function has 'job' parameter (for backward compatibility)
            has_job_param = sig.parameters.get("job") is not None

            if is_long_running and not has_job_param:
                raise ValueError(
                    "is_long_running is True but 'job' parameter is not provided"
                )

            # Remove original 'job' parameter if it exists
            if has_job_param:
                params_list = [p for p in params_list if p.name != "job"]

            # Add ctx as the last parameter with CurrentContext() as default
            ctx_param = inspect.Parameter(
                "ctx",
                inspect.Parameter.KEYWORD_ONLY,
                default=CurrentContext(),
                annotation=Context,
            )
            params_list.append(ctx_param)

            # Add job parameter if function signature includes it
            # Use None as default - we'll resolve CurrentJob() in the wrapper at call time
            if has_job_param:
                job_param = inspect.Parameter(
                    "job",
                    inspect.Parameter.KEYWORD_ONLY,
                    default=None,
                    annotation=Any,  # Use Any to avoid Pydantic issues
                )
                params_list.append(job_param)

            new_sig = sig.replace(parameters=params_list)

            # Exclude dependency-injected params from validation/schema
            exclude_args = ["ctx"]
            if has_job_param:
                exclude_args.append("job")

            # Validate that the user function has explicit type hints
            ensure_type_hints(func, exclude_params=exclude_args)

            # Validate response_handling schema early to catch drift
            if response_handling is not None:
                allowed_keys = {"mode", "extract_path", "template", "content_type"}
                unknown_keys = set(response_handling.keys()) - allowed_keys
                if unknown_keys:
                    raise ValueError(
                        f"response_handling for {tool_name} has unsupported keys: {sorted(unknown_keys)}"
                    )

                mode = response_handling.get("mode", "default")
                if mode not in {"direct", "formatted", "default"}:
                    raise ValueError(
                        f"response_handling.mode for {tool_name} must be one of 'direct', 'formatted', 'default'"
                    )

                content_type = response_handling.get("content_type", "text")
                if content_type not in {"text", "json", "auto"}:
                    raise ValueError(
                        f"response_handling.content_type for {tool_name} must be one of 'text', 'json', 'auto'"
                    )

            # Create the wrapper function
            async def tool_wrapper(*args, **kwargs):
                """MCP-compliant wrapper with streaming."""
                # Extract ctx from kwargs (injected by fast-mcp via CurrentContext())
                ctx = kwargs.pop("ctx", None)
                if ctx is None:
                    raise ValueError("Context not injected by fast-mcp")

                # Extract job from kwargs if present
                # Handle case where fast-mcp might pass CurrentJob instance instead of Job
                job = None
                if has_job_param:
                    job = kwargs.pop("job", None)
                    # If job is a CurrentJob instance, call it to get the actual Job
                    if isinstance(job, CurrentJob):
                        job = job()
                    # If job is still None, _execute_tool will create it

                try:
                    func_kwargs = bind_and_validate_arguments(
                        func, args, kwargs, exclude_params=exclude_args
                    )
                except SignatureValidationError as exc:
                    raise ValueError(
                        f"Argument validation failed for {tool_name}: {exc}"
                    ) from exc

                return await self._execute_tool(
                    func, ctx, is_async, is_long_running, tool_name, job, **func_kwargs
                )

            # Set the signature with ctx as last parameter with CurrentContext() default
            cast(Any, tool_wrapper).__signature__ = new_sig
            cast(Any, tool_wrapper).__name__ = tool_name
            cast(Any, tool_wrapper).__doc__ = tool_description

            # Copy annotations and add Context
            # Note: We don't add job annotation here since we use Any and exclude it from schema
            new_annotations = {}
            if hasattr(func, "__annotations__"):
                new_annotations.update(func.__annotations__)
            new_annotations["ctx"] = Context
            if has_job_param:
                new_annotations["job"] = (
                    Any  # Use Any instead of Job to avoid Pydantic schema issues
                )
            cast(Any, tool_wrapper).__annotations__ = new_annotations

            # Register with fast-mcp
            # Exclude ctx and job from schema generation since they're dependency-injected
            # Prepare tool kwargs
            tool_kwargs = {
                "description": tool_description,
                "exclude_args": exclude_args,
            }

            # Add response_handling metadata to tool's meta field (exposed via MCP protocol)
            if response_handling:
                tool_kwargs["meta"] = {"wizelit_response_handling": response_handling}

            registered_tool = self._mcp.tool(**tool_kwargs)(tool_wrapper)

            # Store tool metadata
            self._tools[tool_name] = {
                "function": func,
                "wrapper": registered_tool,
                "is_long_running": is_long_running,
            }

            # Return original function so it can still be called directly
            return func

        return decorator

    async def _execute_tool(
        self,
        func: Callable,
        ctx: Context,
        is_async: bool,
        is_long_running: bool,
        tool_name: str,
        job: Optional[Job] = None,
        **kwargs,
    ) -> Any:
        """Central execution method for all tools."""

        token = None
        # Create Job instance if not provided
        if job is None and is_long_running:
            job = Job(ctx, db_manager=self._db_manager, log_streamer=self._log_streamer)

            # Persist job to database BEFORE any logs are emitted
            if self._db_manager:
                await job.persist_to_db()

            # Store job in jobs dictionary for later retrieval
            self._jobs[job.id] = job

            # Set CurrentJob context so CurrentJob() can retrieve it
            token = _current_job.set(job)

        try:
            try:
                # Add job to kwargs if function signature includes it
                func_sig = inspect.signature(func)
                if "job" in func_sig.parameters:
                    # For non-long-running tools, create a minimal job if needed
                    if job is None and not is_long_running:
                        # Create a lightweight job for non-long-running tools that require it
                        job = Job(
                            ctx,
                            db_manager=self._db_manager,
                            log_streamer=self._log_streamer,
                        )
                        # Don't persist to DB for fast tools, just create in memory
                    if job is not None:
                        kwargs["job"] = job

                # Execute function (async or sync)
                logging.info(f"kwargs: {kwargs}")
                if is_async:
                    result = await func(**kwargs)
                else:
                    result = await asyncio.to_thread(func, **kwargs)

                # Ensure result is never None for functions that should return strings
                func_sig = inspect.signature(func)
                if result is None:
                    return_annotation = func_sig.return_annotation
                    # Check if return type is str (handle both direct str and Optional[str])
                    is_str_return = (
                        return_annotation is str
                        or (
                            hasattr(return_annotation, "__origin__")
                            and return_annotation.__origin__ is str
                        )
                        or (
                            hasattr(return_annotation, "__args__")
                            and str in getattr(return_annotation, "__args__", [])
                        )
                    )
                    if is_str_return:
                        logging.warning(
                            f"Function {tool_name} returned None but should return str. Returning empty string."
                        )
                        result = ""

                return result

            except Exception as e:
                # Mark job as failed when a job instance exists
                active_job = job or _current_job.get()
                if active_job is not None:
                    active_job.status = "failed"

                # Stream error information
                await ctx.report_progress(
                    progress=0, message=f"Error in {tool_name}: {str(e)}"
                )
                raise
        finally:
            # Reset CurrentJob context only if we set it
            if token is not None:
                _current_job.reset(token)

    def _create_accept_header_middleware(self):
        """Create middleware to make Accept header validation more lenient for streamable-http."""
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.requests import Request

        class LenientAcceptHeaderMiddleware(BaseHTTPMiddleware):
            """Middleware to make Accept header validation more lenient for streamable-http."""

            async def dispatch(self, request: Request, call_next):
                # Only modify Accept header for MCP endpoints
                if "/mcp" in str(request.url.path):
                    accept_header = request.headers.get("accept", "").lower()

                    # Check if Accept header needs fixing
                    needs_fix = (
                        not accept_header
                        or accept_header == "application/json"
                        or accept_header == "*/*"
                        or (
                            "application/json" in accept_header
                            and "text/event-stream" not in accept_header
                        )
                    )

                    if needs_fix:
                        # Modify headers in request.scope (Starlette/FastAPI internal)
                        headers_list = list(request.scope.get("headers", []))

                        # Remove existing accept header if present
                        headers_list = [
                            (name, value)
                            for name, value in headers_list
                            if name.lower() != b"accept"
                        ]

                        # Add new Accept header with both content types
                        headers_list.append(
                            (b"accept", b"application/json, text/event-stream")
                        )

                        # Update the scope
                        request.scope["headers"] = headers_list

                response = await call_next(request)
                return response

        return LenientAcceptHeaderMiddleware

    def _get_fastapi_app(self):
        """Try to get the FastAPI app from FastMCP."""
        if hasattr(self._mcp, "app"):
            return self._mcp.app
        elif hasattr(self._mcp, "_app"):
            return self._mcp._app
        elif hasattr(self._mcp, "fastapi_app"):
            return self._mcp.fastapi_app
        return None

    def _is_middleware_added(self, app, middleware_class):
        """Check if middleware is already added to the app."""
        user_middleware = getattr(app, "user_middleware", []) or []
        return any(
            isinstance(m.cls if hasattr(m, "cls") else m, type)
            and (m.cls if hasattr(m, "cls") else m) == middleware_class
            for m in user_middleware
        )

    def _add_accept_header_middleware(self, app, middleware_class):
        """Add Accept header middleware to the FastAPI app if not already added."""
        if not self._is_middleware_added(app, middleware_class):
            app.add_middleware(middleware_class)
            print(
                "✅ Added lenient Accept header middleware for streamable-http compatibility"
            )
            return True
        return False

    def _patch_fastmcp_run_with_middleware(self, middleware_class):
        """Patch FastMCP's run method to add middleware before server starts."""
        original_run = self._mcp.run

        def patched_run(*args, **run_kwargs):
            # Try to get app before calling original_run
            app = self._get_fastapi_app()
            if app:
                self._add_accept_header_middleware(app, middleware_class)

            # Call original run (this will start the server)
            result = original_run(*args, **run_kwargs)

            # After run() starts, try again in case app was initialized during run()
            if not app:
                import time

                time.sleep(0.1)  # Give FastMCP time to initialize

                app = self._get_fastapi_app()
                if app:
                    self._add_accept_header_middleware(app, middleware_class)

            return result

        # Replace the run method
        self._mcp.run = patched_run

    def _setup_accept_header_middleware(self):
        """Setup middleware to make Accept header validation more lenient.

        This allows clients that only send "application/json" to work.
        FastMCP requires "application/json, text/event-stream" but Chainlit doesn't set it.
        """
        try:
            middleware_class = self._create_accept_header_middleware()

            # Try to add middleware before run() is called
            app = self._get_fastapi_app()
            if app:
                self._add_accept_header_middleware(app, middleware_class)
            else:
                # If app not available, patch run() to add middleware during initialization
                self._patch_fastmcp_run_with_middleware(middleware_class)
                print(
                    "ℹ️  Will add Accept header middleware during FastMCP initialization"
                )

        except Exception as e:
            print(f"⚠️  Could not add Accept header middleware: {e}")
            import traceback

            traceback.print_exc()

    def run(
        self,
        transport: Optional[Transport] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs,
    ):
        """
        Start the MCP server.

        Args:
            transport: MCP transport type ('stdio', 'http', 'streamable-http')
            host: Host to bind to (for HTTP transports)
            port: Port to bind to (for HTTP transports)
            **kwargs: Additional arguments passed to fast-mcp
        """
        transport = cast(Transport, transport or self._transport)
        host = host or self._host
        port = port or self._port
        print(f"🚀 Starting {self._name} MCP Server")

        if transport in ["http", "streamable-http"]:
            print(f"🌐 Listening on {host}:{port}")
            self._setup_accept_header_middleware()

        print(f"🔧 Registered {len(self._tools)} tool(s):")
        for tool_name, tool_info in self._tools.items():
            lr_status = "⏱️  long-running" if tool_info["is_long_running"] else "⚡ fast"
            print(f"   • {tool_name} [{lr_status}]")

        # Start the server
        self._mcp.run(transport=transport, host=host, port=port, **kwargs)

    def list_tools(self) -> dict:
        """Return metadata about all registered tools."""
        return {
            name: {
                "is_long_running": info["is_long_running"],
                "llm_framework": info["llm_framework"],
            }
            for name, info in self._tools.items()
        }

    def get_job_logs(self, job_id: str) -> Optional[list]:
        """
        Get logs for a specific job by job_id.

        Args:
            job_id: The job identifier

        Returns:
            List of log messages (timestamped strings) if job exists, None otherwise
        """
        job = self._jobs.get(job_id)
        if job is None:
            return None
        return job.logs

    def get_job_status(self, job_id: str) -> Optional[str]:
        """
        Get status for a specific job by job_id.

        Args:
            job_id: The job identifier

        Returns:
            Job status ("running", "completed", "failed") if job exists, None otherwise
        """
        job = self._jobs.get(job_id)
        if job is None:
            return None
        return job.status

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get a Job instance by job_id.
        First checks in-memory cache, then falls back to database.

        Args:
            job_id: The job identifier

        Returns:
            Job instance if exists, None otherwise
        """
        # Check in-memory first
        job = self._jobs.get(job_id)
        if job:
            return job

        # If not in memory and DB is available, try to load from DB
        # Note: This returns None for now as we'd need async context
        # Use get_job_from_db_async for async retrieval
        return None

    async def get_job_from_db(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve job data from database asynchronously.

        Args:
            job_id: The job identifier

        Returns:
            Dict with job data or None if not found
        """
        if not self._db_manager:
            return None

        try:
            from wizelit_sdk.models.job import JobModel
            from sqlalchemy import select

            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    select(JobModel).where(JobModel.id == job_id)
                )
                job_model = result.scalar_one_or_none()

                if not job_model:
                    return None

                return {
                    "id": job_model.id,
                    "status": job_model.status,
                    "result": job_model.result,
                    "error": job_model.error,
                    "created_at": (
                        job_model.created_at.isoformat()
                        if job_model.created_at is not None
                        else None
                    ),
                    "updated_at": (
                        job_model.updated_at.isoformat()
                        if job_model.updated_at is not None
                        else None
                    ),
                }
        except Exception as e:
            logging.error(f"Error retrieving job from database: {e}")
            return None

    async def get_job_logs_from_db(
        self, job_id: str, limit: int = 100
    ) -> Optional[list]:
        """
        Retrieve job logs from database asynchronously.

        Args:
            job_id: The job identifier
            limit: Maximum number of logs to retrieve

        Returns:
            List of log messages or None if job not found
        """
        if not self._db_manager:
            return None

        try:
            from wizelit_sdk.models.job import JobLogModel
            from sqlalchemy import select

            async with self._db_manager.get_session() as session:
                result = await session.execute(
                    select(JobLogModel)
                    .where(JobLogModel.job_id == job_id)
                    .order_by(JobLogModel.timestamp.asc())
                    .limit(limit)
                )
                log_models = result.scalars().all()

                return [
                    f"[{log.level}] [{log.timestamp.strftime('%H:%M:%S')}] {log.message}"
                    for log in log_models
                ]
        except Exception as e:
            logging.error(f"Error retrieving logs from database: {e}")
            return None

    def get_jobs(self) -> list[Job]:
        """
        Get all Job instances.

        Returns:
            List of Job instances
        """
        return list(self._jobs.values())

    def set_job_status(self, job_id: str, status: str) -> bool:
        """
        Set the status of a job by job_id.

        Args:
            job_id: The job identifier
            status: New status ("running", "completed", "failed")

        Returns:
            True if job exists and status was updated, False otherwise
        """
        job = self._jobs.get(job_id)
        if job is None:
            return False
        job.status = status
        return True

    def set_job_result(
        self, job_id: str, result: Optional[Union[str, dict[str, Any]]]
    ) -> bool:
        """
        Set the result of a job by job_id.

        Args:
            job_id: The job identifier
            result: The job result

        Returns:
            True if job exists and result was updated, False otherwise
        """
        job = self._jobs.get(job_id)
        if job is None:
            return False
        job.result = result
        return True

    def set_job_error(self, job_id: str, error: Optional[str]) -> bool:
        """
        Set the error message of a job by job_id.

        Args:
            job_id: The job identifier
            error: The error message

        Returns:
            True if job exists and error was updated, False otherwise
        """
        job = self._jobs.get(job_id)
        if job is None:
            return False
        job.error = error
        return True
