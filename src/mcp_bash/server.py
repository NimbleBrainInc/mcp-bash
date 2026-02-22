"""Bash MCP Server - FastMCP Implementation."""

import logging
import os
import signal
import subprocess
import sys
import time

from fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .api_models import BashExecResponse

# Debug logging for container diagnostics
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_bash")


# Signal handler for debugging
def _signal_handler(signum: int, frame: object) -> None:
    logger.warning("Received signal %s (%s)", signum, signal.Signals(signum).name)


# Register signal handlers to see what signals we receive
for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    try:
        signal.signal(sig, _signal_handler)
        logger.debug("Registered handler for %s", sig.name)
    except (ValueError, OSError) as e:
        logger.debug("Could not register handler for %s: %s", sig.name, e)

logger.info("Bash server module loading...")

# Create MCP server
logger.debug("Creating FastMCP instance...")
mcp = FastMCP("Bash")
logger.debug("FastMCP instance created")

# Maximum output size: 10 MB
_MAX_OUTPUT_BYTES = 10 * 1024 * 1024

# Maximum allowed timeout in seconds
_MAX_TIMEOUT = 600


def _truncate(text: str, limit: int = _MAX_OUTPUT_BYTES) -> str:
    """Truncate text to byte limit, preserving valid UTF-8."""
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= limit:
        return text
    truncated = encoded[:limit].decode("utf-8", errors="ignore")
    return truncated + "\n\n[truncated — output exceeded 10 MB]"


# Health endpoint for HTTP transport
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-bash"})


# MCP Tools
@mcp.tool()
async def bash_exec(
    command: str,
    cwd: str | None = None,
    timeout: int = 30,
    env: dict[str, str] | None = None,
    ctx: Context | None = None,
) -> BashExecResponse:
    """Execute a bash command and return stdout, stderr, exit code, and duration.

    Args:
        command: The bash command to execute
        cwd: Working directory (defaults to server's cwd)
        timeout: Timeout in seconds (default 30, max 600)
        env: Additional environment variables to set
        ctx: MCP context

    Returns:
        Command output with stdout, stderr, exit code, and duration
    """
    # Validate cwd
    if cwd is not None:
        real_cwd = os.path.realpath(cwd)
        if not os.path.isdir(real_cwd):
            raise ValueError(f"Working directory does not exist: {cwd}")
        cwd = real_cwd

    # Clamp timeout
    timeout = min(max(1, timeout), _MAX_TIMEOUT)

    # Build environment
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    if ctx:
        await ctx.info(f"Executing: {command[:100]}...")

    start = time.monotonic()

    try:
        result = subprocess.run(
            command,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=run_env,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)

        return BashExecResponse(
            stdout=_truncate(result.stdout),
            stderr=_truncate(result.stderr),
            exit_code=result.returncode,
            duration_ms=elapsed_ms,
        )

    except subprocess.TimeoutExpired as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")

        return BashExecResponse(
            stdout=_truncate(stdout),
            stderr=_truncate(stderr + f"\n[timed out after {timeout}s]"),
            exit_code=124,
            duration_ms=elapsed_ms,
        )


# Create ASGI application for HTTP deployment
logger.debug("Creating http_app()...")
app = mcp.http_app()
logger.info("ASGI app created successfully, ready for uvicorn")

# Stdio entrypoint for Claude Desktop / mpak
if __name__ == "__main__":
    logger.info("Running in stdio mode")
    mcp.run()
