# Documentation Publication Policy

Tatuy's repository contains both public documentation and operational material that should remain repository-only.

## Public documentation

The GitHub Pages site publishes:

- getting started
- learn material
- task-oriented guides
- architecture documentation
- examples and web compatibility status
- selected internals that help contributors understand the engine

These documents should be written as stable project documentation and may link to public source, live examples, and release/build metadata.

## Repository-only documentation

The public MkDocs build intentionally excludes:

- `docs/ai/` — AI-specific operating instructions and navigation aids
- `docs/internals/mcp/` — local MCP server operation and development notes
- `.tatuy/` — implementation roadmaps, local reports, staging state, and planning artifacts
- local profiles, credentials, recordings, replays, screenshots, and workspace state

Repository-only material may still be version-controlled when useful to contributors, but it must not enter `build/web/` implicitly.

## Publication invariant

The Pages build is allow-list based: MkDocs emits selected public documentation, browser targets emit normalized bundles beneath `play/`, and the showcase builder emits only its catalog, shell, assets, provenance, and generated play pages.

`WebOutputStructureValidator` rejects known local/private paths and key material if they appear in the final publication tree. Target staging also filters those paths before Pygbag packaging.

When adding a new documentation area, decide whether it is public before adding it to MkDocs navigation. Do not rely on accidental directory traversal to determine publication visibility.
