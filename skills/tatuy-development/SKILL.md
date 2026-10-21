---
name: tatuy-development
description: Collaborate on Tatuy engine and game development by inspecting projects, creating Tatuy experiments, games, and standalone projects, and proposing implementations in chat.
---

# Tatuy development

Use the Tatuy Development MCP tools to ground design discussions, project
creation, and code suggestions in the user's current Tatuy engine, games,
experiments, and standalone projects.

## Discover context

Call `list_projects` when project identities or locations are unknown.

Projects are dynamically discovered and may include:

- `engine` for the Tatuy engine repository.
- `experiment:<name>` for gameplay and technical experiments.
- `game:<name>` for Tatuy-owned reference games and clones.
- `project:<name>` for standalone games that use Tatuy.

Read the relevant repository README, pyproject.toml, tatuy.toml, and AGENTS.md
when present. Check for additional AGENTS.md files along the directory path
to the code being discussed.

Use `list_files` to discover structure, `search_code` to find implementations,
and `read_file` to inspect relevant definitions and callers. Follow pagination
and truncation indicators instead of assuming the first response is complete.

Verify documentation against source. If a documented file or API is missing,
state the discrepancy and inspect the available implementation.

## Create Tatuy targets

When the user asks to create a new Tatuy experiment, reference game, clone,
or standalone project, use `create_tatuy_target`.

Do not merely provide the scaffold in chat when the user explicitly asks
Tatuy Development to create the target and the creation tool is available.

Use these target kinds:

- `experiment` for prototypes, technical investigations, performance tests,
  rendering experiments, procedural-generation ideas, and other R&D work
  belonging inside `examples/experiments`.
- `game` for reference games, clones, and games intentionally belonging to
  the Tatuy repository under `examples/games`.
- `project` for standalone games or applications maintained separately from
  the Tatuy repository.

Experiments and games use the current Tatuy workspace automatically.

Standalone projects may use either the local Tatuy development repository
or a published PyPI Tatuy version.

When the user describes an idea, preserve the useful intent in the target
description and provide relevant tags when they are apparent from the request.

After creating a target, use the returned project key for subsequent inspection.
For example:

- `experiment:procedural_fire`
- `game:pong`
- `project:shatterphase`

Do not invent successful creation. Only state that a target was created when
`create_tatuy_target` succeeds.

## Collaborate on code

General source-code editing remains collaborative and read-only unless another
available MCP tool explicitly provides the requested write capability.

The user normally reviews and applies proposed code changes themselves.

Provide focused code snippets with their destination file and insertion or
replacement location. Supply full-file replacements only when asked.

For substantial design decisions, explain the relevant tradeoff before
presenting the implementation. Keep routine implementation choices brief.

Reuse existing engine capabilities. Verify signatures, imports, lifecycle
hooks, and system ordering before relying on them.

Separate confirmed behavior from proposed behavior and assumptions.
Re-read relevant files after the user reports local changes.

Suggest useful checks, but do not claim execution or successful tests without
a tool result or the user's report.

## Assets

Before proposing game assets, inspect how the game loads them and identify
the required format, dimensions, transparency, and animation conventions.

Do not claim to generate, save, import, convert, execute, capture, or otherwise
modify something unless an available tool explicitly supports that action.
