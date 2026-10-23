# Tatuy Development MCP Server

A local MCP server that gives ChatGPT controlled development access to the
Tatuy engine, examples, and configured standalone projects.

The server supports chat-first collaboration as well as explicitly
authorized project modifications. Repository behavior and write
authorization are governed by `AGENTS.md`, `docs/ai/`, and the Tatuy
Development skill.

## Tools

| Tool | Purpose |
|---|---|
| `server_info` | Describe the server |
| `list_projects` | List configured projects and their availability |
| `list_files` | Browse a project directory |
| `read_file` | Read numbered lines and the current file SHA-256 |
| `search_code` | Search source and documentation for literal text |
| `create_tatuy_target` | Create an experiment, game, or standalone project |
| `create_directory` | Create one project-relative directory |
| `create_file` | Create a new permitted UTF-8 project file |
| `edit_file` | Safely edit an existing file using optimistic concurrency |
| `delete_path` | Delete a guarded file or empty directory |
| `format_python` | Run isort and Black on selected Python paths |
| `run_tests` | Run targeted pytest verification |
| `run_mypy` | Run diagnostic mypy analysis against non-test Python code |
| `run_pylint` | Run diagnostic pylint analysis against non-test Python code |
| `git_review` | Render an interactive changed-files panel in MCP Apps-compatible hosts |
| `git_status` | Return the current branch and changed files |
| `git_snapshot` | Summarize changed files and line counts |
| `git_diff` | Review tracked and untracked changes |
| `git_stage` | Stage selected project-relative paths |
| `git_commit` | Commit staged changes with a short Conventional Commit subject |
| `git_log` | Return recent commit hashes and subjects |

The server provides controlled development access to configured projects.

File creation, modification, and deletion are restricted to permitted
project-relative paths and supported file types.

Existing-file edits and file deletion require the SHA-256 returned by
`read_file`, preventing silent modification or deletion when a file changes
after inspection.

Directory creation is explicit. Directory deletion is allowed only for
empty directories; recursive bulk deletion is intentionally unsupported.

Command execution is intentionally constrained. The server does not expose
an arbitrary shell tool.

Formatting, tests, mypy, and pylint run through dedicated tools with
bounded output and execution time.

Test subprocesses receive a sanitized environment and do not inherit MCP,
tunnel, API, or unrelated server secrets.

Tatuy pytest targets are restricted to `tests/`. Fundamentals, experiments,
and games are executable validation targets rather than pytest suites.

Test files may be formatted but are not analyzed by mypy or pylint.

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

Edit `.env` with the Tatuy engine path, standalone-project root, and OpenAI
tunnel runtime API key:

```dotenv
TATUY_ENGINE_PATH=C:/path/to/tatuy
TATUY_PROJECTS_PATH=C:/path/to/projects
CONTROL_PLANE_API_KEY=your-runtime-api-key
```

Use repository roots to make source files, tests, documentation, and project configuration accessible.

Commit `.env.example` with placeholders. Keep `.env` untracked.

The server reads `.env` from the repository root. Existing environment variables take precedence.

The tunnel launcher uses `CONTROL_PLANE_API_KEY` from its environment when available, otherwise loading it from `.env`. It restores the previous environment value when it exits.

The MCP tools exclude `.env` files.

## Configure projects

The engine repository is configured with `TATUY_ENGINE_PATH`.

Standalone Tatuy projects are discovered dynamically inside
`TATUY_PROJECTS_PATH` when they contain a `tatuy.toml` manifest.

Experiments and games are discovered dynamically from the Tatuy engine
repository under:

```text
examples/experiments/
examples/games/
```

Tool requests use project keys and project-relative paths. The server
validates that resolved paths remain inside the selected project.

The shared access policy excludes sensitive files and selected directories.
These rules are filename/path filters rather than secret-content detection.

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
2. ChatGPT inspects the implementation, Tatuy-owned tests, canonical
   documentation, and affected examples.
3. Review and design requests remain read-only.
4. When implementation is explicitly authorized, ChatGPT may apply the
   implementation and directly necessary supporting work.
5. New importable source packages are created with `__init__.py`.
6. Tatuy engine changes audit affected fundamentals, experiments, and games.
7. Modified Python files, including tests, are formatted.
8. Tatuy-owned source/tooling behavior is verified with targeted pytest
   tests.
9. Mypy and pylint are run only against relevant non-test code.
10. Non-trivial static-analysis fixes are proposed for developer approval
    before being applied.
11. Broader verification is run when shared infrastructure is affected.
12. ChatGPT reports exactly which checks ran and their results.

Repository behavior is governed by `AGENTS.md`, `docs/ai/`, and the Tatuy
Development skill.

## Troubleshooting

- **Missing session ID in a browser:** use an MCP client such as Inspector.
- **Project unavailable:** check the configured directory.
- **Tunnel validation fails:** inspect the doctor output and verify permissions, profile configuration, and server availability.
- **Plugin calls fail:** confirm both the Python server and tunnel client are running.
- **Search results are truncated:** narrow the directory or search term.

Only tool-returned content is sent into the conversation; using the plugin does not automatically upload the entire repository.
