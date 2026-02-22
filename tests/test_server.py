"""Unit tests for the Bash MCP server tools."""

import pytest
from fastmcp import Client

from mcp_bash.server import mcp


@pytest.fixture
def mcp_server():
    """Return the MCP server instance."""
    return mcp


@pytest.mark.asyncio
async def test_bash_exec_echo(mcp_server):
    """Test basic echo command."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "echo 'hello world'"})

        data = result.data
        assert data.stdout.strip() == "hello world"
        assert data.stderr == ""
        assert data.exit_code == 0
        assert data.duration_ms >= 0


@pytest.mark.asyncio
async def test_bash_exec_exit_code(mcp_server):
    """Test non-zero exit code."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "exit 42"})

        data = result.data
        assert data.exit_code == 42


@pytest.mark.asyncio
async def test_bash_exec_stderr(mcp_server):
    """Test stderr capture."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "echo 'err' >&2"})

        data = result.data
        assert "err" in data.stderr
        assert data.exit_code == 0


@pytest.mark.asyncio
async def test_bash_exec_cwd(mcp_server):
    """Test custom working directory."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "pwd", "cwd": "/tmp"})

        data = result.data
        assert "tmp" in data.stdout.lower()
        assert data.exit_code == 0


@pytest.mark.asyncio
async def test_bash_exec_env(mcp_server):
    """Test custom environment variables."""
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "bash_exec", {"command": "echo $MY_VAR", "env": {"MY_VAR": "test_value"}}
        )

        data = result.data
        assert "test_value" in data.stdout
        assert data.exit_code == 0


@pytest.mark.asyncio
async def test_bash_exec_timeout(mcp_server):
    """Test command timeout."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "sleep 10", "timeout": 1})

        data = result.data
        assert data.exit_code == 124
        assert "timed out" in data.stderr


@pytest.mark.asyncio
async def test_bash_exec_invalid_cwd(mcp_server):
    """Test invalid working directory raises error."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("bash_exec", {"command": "pwd", "cwd": "/nonexistent"})
        assert (
            "does not exist" in str(exc_info.value).lower()
            or "nonexistent" in str(exc_info.value).lower()
        )


@pytest.mark.asyncio
async def test_bash_exec_timeout_clamped(mcp_server):
    """Test that excessive timeout is clamped to max."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "echo 'ok'", "timeout": 9999})

        data = result.data
        assert data.stdout.strip() == "ok"
        assert data.exit_code == 0


@pytest.mark.asyncio
async def test_bash_exec_command_not_found(mcp_server):
    """Test command not found returns exit code 127."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "nonexistentcommand123"})

        data = result.data
        assert data.exit_code == 127


@pytest.mark.asyncio
async def test_bash_exec_multiline(mcp_server):
    """Test multiline command output."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("bash_exec", {"command": "echo 'a'; echo 'b'"})

        data = result.data
        assert "a" in data.stdout
        assert "b" in data.stdout
        assert data.exit_code == 0


@pytest.mark.asyncio
async def test_bash_exec_tool_listed(mcp_server):
    """Test that exactly one tool named bash_exec is registered."""
    async with Client(mcp_server) as client:
        tools = await client.list_tools()

        assert len(tools) == 1
        assert tools[0].name == "bash_exec"
