# Bash MCP Server

[![mpak](https://img.shields.io/badge/mpak-registry-blue)](https://mpak.dev/packages/@nimblebraininc/bash?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)
[![NimbleBrain](https://img.shields.io/badge/NimbleBrain-nimblebrain.ai-purple)](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)
[![Discord](https://img.shields.io/badge/Discord-community-5865F2)](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that executes bash commands. Returns stdout, stderr, exit code, and execution duration for each command.

**[View on mpak registry](https://mpak.dev/packages/@nimblebraininc/bash?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)** | **Built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)**

## Install

Install with [mpak](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash):

```bash
mpak install @nimblebraininc/bash
```

### Claude Code

```bash
claude mcp add bash -- mpak run @nimblebraininc/bash
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bash": {
      "command": "mpak",
      "args": ["run", "@nimblebraininc/bash"]
    }
  }
}
```

See the [mpak registry page](https://mpak.dev/packages/@nimblebraininc/bash?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash) for full install options.

## Tools

### bash_exec

Execute a bash command and return stdout, stderr, exit code, and duration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | `string` | Yes | The bash command to execute |
| `cwd` | `string` | No | Working directory (defaults to server's cwd) |
| `timeout` | `integer` | No | Timeout in seconds (default: `30`, max: `600`) |
| `env` | `object` | No | Additional environment variables to set |

**Example call:**

```json
{
  "name": "bash_exec",
  "arguments": {
    "command": "ls -la /tmp",
    "timeout": 10
  }
}
```

**Example response:**

```json
{
  "stdout": "total 0\ndrwxrwxrwt  12 root  wheel  384 Jan 15 12:00 .\ndrwxr-xr-x   6 root  wheel  192 Jan  1 00:00 ..\n",
  "stderr": "",
  "exit_code": 0,
  "duration_ms": 12
}
```

## Security Model

This server executes arbitrary bash commands. Security is **secure-by-deployment**: the server itself has no allowlist or sandbox. Instead, security is enforced by the deployment environment:

- **mpak**: User approves MTF permissions (`subprocess: "full"`) at install time
- **Containers**: Linux namespaces, cgroups, and network policies restrict what commands can do
- **Claude Desktop**: Runs under the user's own OS permissions

The MTF permission declaration (`subprocess: "full"`, `filesystem: "full"`, `network: "full"`) accurately reflects that bash commands can read/write files and make network calls.

## Quick Start

### Local Development

```bash
git clone https://github.com/NimbleBrainInc/mcp-bash.git
cd mcp-bash

# Install dependencies
uv sync

# Run the server (stdio mode)
uv run python -m mcp_bash.server

# Or run via FastMCP
uv run fastmcp run src/mcp_bash/server.py
```

The server supports HTTP transport with:
- Health check: `GET /health`
- MCP endpoint: `POST /mcp`

## Development

```bash
# Install with dev dependencies
uv sync --group dev

# Run unit tests
make test

# Run with coverage
make test-cov

# Run all checks (format, lint, typecheck, unit tests)
make check

# Format
uv run ruff format .

# Lint
uv run ruff check .
```

### E2E Tests

End-to-end tests validate the full MCPB bundle lifecycle: building the bundle, deploying it into a Docker container, and calling tools over HTTP.

**Prerequisites:** Docker running, `mcpb` CLI installed (`npm install -g @anthropic-ai/mcpb`)

```bash
make test-e2e
```

The tests:
1. Vendor dependencies for the Docker container's Linux architecture
2. Build a `.mcpb` bundle with `mcpb pack`
3. Serve the bundle over HTTP
4. Start a `nimbletools/mcpb-python` container that downloads and runs the bundle
5. Verify the `/health` endpoint, MCP tool listing, and tool invocation via streamable HTTP

## About

Bash MCP Server is published on the [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash) and built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash). mpak is an open registry for [Model Context Protocol](https://modelcontextprotocol.io) servers.

- [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)
- [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)
- [MCP specification](https://modelcontextprotocol.io)
- [Discord community](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-bash)

## License

MIT
