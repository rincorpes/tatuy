# Tatuy repository guidance

## Project

Tatuy is a Python 2D game engine built around scenes, an Entity
Component System, and separate gameplay and rendering stages.
Pygame is the current backend.

Read README.md for an overview and pyproject.toml for supported
Python versions, dependencies, and tooling. Verify specific APIs
against the current implementation; documentation may lag behind code.

## Repository map

- src/tatuy: engine and game-building APIs.
- src/tatuy_cli: repository commands and example execution.
- src/tatuy_mcp: read-only access to configured development projects.
- src/tatuy_profiler: profiling tooling.
- examples: demonstrations, experiments, and game examples.
- tests: engine tests.
- docs: documentation and tutorials.

Example games may live inside this repository. Identify their location
before assuming they have a separate environment or repository.

## Architecture and reuse

Before proposing a feature, inspect the relevant engine implementation
and a nearby example.

Prefer existing components, systems, scene hooks, and services when
they support the intended behavior.

Keep game-specific rules in the game. Propose engine changes when
the capability has a clear reusable purpose.

Preserve the separation between control, simulation, and presentation.
Inspect the actual lifecycle and system ordering before deciding where
behavior belongs.

Keep Pygame-specific behavior in the backend layer where practical.
Use existing engine interfaces from gameplay code.

Avoid broad framework changes for a focused gameplay request.

## Python conventions

Follow pyproject.toml and nearby source files.

- Maintain compatibility with the declared Python version range.
- Use Black's configured 79-character line length.
- Follow the configured isort import groups.
- Prefer explicit types and small, composable functions.
- Verify import paths, signatures, and exports before suggesting code.

## Verification

Run or suggest commands from the Tatuy repository root.

Install dependencies:

    poetry install

Run a documented example:

    poetry run python manage.py run example scenes.on_present

For behavior changes, identify the relevant tests and suggest the
narrowest useful pytest command. Inspect example-specific instructions
before proposing launch commands.

Interactive games require a desktop environment. MP4 encoding requires
FFmpeg.

Distinguish tests actually run from checks merely suggested.

## Documentation and configuration

Update relevant documentation or examples when public APIs or workflows
change.

Keep local credentials in untracked configuration. Use placeholders in
.env.example. Do not request secret values through MCP tools.

Apply additional AGENTS.md guidance found in directories relevant to
the task. More specific guidance refines these repository-wide rules.