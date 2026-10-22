# Tatuy Development MCP Server

A local MCP server that lets ChatGPT inspect the Tatuy engine and game projects.

It supports a collaborative workflow: ChatGPT reads the codebase, discusses designs, and provides code in chat. You review and apply changes yourself.

## Tools

| Tool | Purpose |
|---|---|
| `server_info` | Describe the server |
| `list_projects` | List configured projects and their availability |
| `list_files` | Browse a project directory |
| `read_file` | Read numbered lines and the current file SHA-256 |
| `search_code` | Search source and documentation for literal text |
| `create_tatuy_target` | Create an experiment, game, or standalone project |
| `create_file` | Create a new permitted UTF-8 project file |
| `edit_file` | Safely edit an existing file using optimistic concurrency |
| `format_python` | Run isort and Black on selected Python paths |
| `run_tests` | Run targeted pytest verification |

The server provides controlled development access to configured projects.

File creation and modification are restricted to permitted project-relative
paths and supported text file types. Existing-file edits require the
SHA-256 returned by `read_file`, preventing silent overwrites when a file
changes after inspection.

Command execution is intentionally constrained. The server does not expose
an arbitrary shell tool. Formatting and tests run through dedicated tools
with bounded output and execution time.

Test subprocesses receive a sanitized environment and do not inherit MCP,
tunnel, API, or unrelated server secrets.

## Requirements

- Python and the official MCP Python SDK v2
- Node.js for the optional MCP Inspector
- OpenAI `tunnel-client` for connecting to ChatGPT
- A configured OpenAI tunnel and runtime API key with Tunnels Read + Use permission

## Installation

From an activated Python environment:

```powershell
python -m pip install "mcp[cli]>=2,<3" python-dotenv
```

## Configuration

Copy the root configuration template:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your project paths and OpenAI tunnel runtime API key:

```dotenv
TATUY_ENGINE_PATH=C:/path/to/tatuy
TATUY_GAME_PATH=C:/path/to/game
CONTROL_PLANE_API_KEY=your-runtime-api-key
```

Use repository roots to make source files, tests, documentation, and project configuration accessible.

Commit `.env.example` with placeholders. Keep `.env` untracked.

The server reads `.env` from the repository root. Existing environment variables take precedence.

The tunnel launcher uses `CONTROL_PLANE_API_KEY` from its environment when available, otherwise loading it from `.env`. It restores the previous environment value when it exits.

Project access remains read-only and scoped to the configured directories. The MCP tools exclude `.env` files.

## Configure projects

Set project roots in `server.py`:

```python
PROJECTS: dict[str, Path] = {
    "engine": Path(r"C:\path\to\tatuy"),
    "game": Path(r"C:\path\to\game"),
}
```

Use repository roots when you want access to documentation, configuration, tests, and source files.

Tool requests use project names and project-relative paths. The server validates that resolved paths stay inside the selected project.

If configured, the shared access policy also excludes selected directories and sensitive filenames. These rules are filename filters, not secret detection.

## Run locally

```powershell
python server.py
```

The MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

Keep this process running while using the server.

The endpoint is not a webpage. Opening it in a browser may return a missing-session error because MCP clients initialize a protocol session first.

## Test with MCP Inspector

In another terminal:

```powershell
npx -y @modelcontextprotocol/inspector
```

Open the Inspector URL printed in the terminal. Select Streamable HTTP and connect to:

```text
http://127.0.0.1:8000/mcp
```

List the tools and call `list_projects`.

## Configure the tunnel once

Create a tunnel in:

https://platform.openai.com/settings/organization/tunnels

Download and extract the Windows tunnel client. Then initialize a profile, replacing the executable path and tunnel ID:

```powershell
& "C:\path\to\tunnel-client.exe" init `
  --sample sample_mcp_remote_no_auth `
  --profile tatuy `
  --tunnel-id tunnel_YOUR_ID `
  --mcp-server-url http://127.0.0.1:8000/mcp
```

The profile stores the tunnel configuration. The runtime API key is supplied separately when starting the client.

## Start the tunnel

With the Python server running, open another PowerShell terminal:

```powershell
.\start-tunnel.ps1 `
  -TunnelClientPath "C:\path\to\tunnel-client.exe"
```

Enter the runtime API key at the hidden prompt.

The script validates the profile and starts the tunnel in the foreground. Keep both terminals open. Press Ctrl+C in the tunnel terminal to stop it.

To use a different profile:

```powershell
.\start-tunnel.ps1 `
  -TunnelClientPath "C:\path\to\tunnel-client.exe" `
  -Profile "another-profile"
```

## Connect in ChatGPT

1. Open Plugins and choose Add custom MCP server.
2. Select Tunnel as the connection.
3. Select your configured tunnel.
4. Choose No authentication for this server, which does not implement OAuth.
5. Create the plugin and select it in a chat.
6. Ask ChatGPT to call `list_projects`.

The tunnel authenticates separately using the runtime API key.

## Development workflow

1. Ask ChatGPT to inspect repository guidance and the relevant subsystem.
2. ChatGPT reads the implementation, tests, documentation, and nearby
   examples as appropriate.
3. For review and design requests, proposed changes remain in chat.
4. When you explicitly authorize implementation, ChatGPT may apply the
   implementation and directly necessary supporting tests, documentation,
   examples, and formatting.
5. ChatGPT formats modified Python files.
6. ChatGPT runs the narrowest relevant tests.
7. Broader verification is run when the change affects shared
   infrastructure.
8. ChatGPT reports which checks actually ran and their results.

Repository instruction files are accessible through the tools. Behavioral
guidance is provided by AGENTS.md, docs/ai/, and the Tatuy Development
skill.

## Troubleshooting

- **Missing session ID in a browser:** use an MCP client such as Inspector.
- **Project unavailable:** check the configured directory.
- **Tunnel validation fails:** inspect the doctor output and verify permissions, profile configuration, and server availability.
- **Plugin calls fail:** confirm both the Python server and tunnel client are running.
- **Search results are truncated:** narrow the directory or search term.

Only tool-returned content is sent into the conversation; using the plugin does not automatically upload the entire repository.
