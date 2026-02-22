"""Pydantic models for Bash MCP Server responses."""

from pydantic import BaseModel, Field


class BashExecResponse(BaseModel):
    """Response model for bash_exec tool."""

    stdout: str = Field(..., description="Command standard output")
    stderr: str = Field(..., description="Command standard error")
    exit_code: int = Field(..., description="Exit code (124 = timeout)")
    duration_ms: int = Field(..., description="Execution time in milliseconds")
