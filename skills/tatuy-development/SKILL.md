---
name: tatuy-development
description: Collaborate on Tatuy engine and game development by inspecting code through Tatuy Development and proposing implementations in chat.
---

# Tatuy development

Use the Tatuy Development MCP tools to ground design discussions and
code suggestions in the user's current engine and game projects.

## Discover context

Call list_projects when project identities or locations are unknown.

Read the relevant repository README, pyproject.toml, and AGENTS.md
when present. Check for additional AGENTS.md files along the directory
path to the code being discussed.

A configured game root may be inside the engine repository. In that
case, use the engine project to inspect ancestor instruction files.

Use list_files to discover structure, search_code to find implementations,
and read_file to inspect relevant definitions and callers. Follow
pagination and truncation indicators instead of assuming the first
response is complete.

Verify documentation against source. If a documented file or API is
missing, state the discrepancy and inspect the available implementation.

## Collaborate in chat

The user reviews and applies code themselves.

Provide focused code snippets with their destination file and insertion
or replacement location. Supply full-file replacements only when asked.

For substantial design decisions, explain the relevant tradeoff before
presenting the implementation. Keep routine implementation choices brief.

Reuse existing engine capabilities. Verify signatures, imports, lifecycle
hooks, and system ordering before relying on them.

Separate confirmed behavior from proposed behavior and assumptions.
Re-read relevant files after the user reports local changes.

Suggest useful checks, but do not claim execution or successful tests
without a tool result or the user's report.

## Assets

Before proposing game assets, inspect how the game loads them and identify
the required format, dimensions, transparency, and animation conventions.

The MCP server provides reading tools only. Do not claim to generate,
save, import, or convert assets unless an available tool actually performs
that action.