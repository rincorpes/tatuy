# Tatuy repository guidance

## Project

Tatuy is a Python 2D game engine built around scenes, an Entity
Component System, and separate gameplay and rendering stages.
Pygame is the current backend.

Read README.md for an overview and pyproject.toml for supported
Python versions, dependencies, and tooling. Verify specific APIs
against the current implementation; documentation may lag behind code.

For AI-assisted development, begin with docs/ai/index.md and follow
the relevant architecture, task-routing, invariant, public-API, and
verification guidance from docs/ai/.

## Repository map

- src/tatuy: engine and game-building APIs.
- src/tatuy_cli: repository commands and example execution.
- src/tatuy_mcp: controlled development access to configured projects.
- src/tatuy_profiler: profiling tooling.
- examples: demonstrations, experiments, and game examples.
- tests: engine and tooling tests.
- docs: documentation and tutorials.
- skills: ChatGPT collaboration and development workflow guidance.

Example games may live inside this repository. Identify their location
before assuming they have a separate environment or repository.

## Architecture and reuse

Before proposing a feature, inspect the relevant engine implementation,
relevant canonical documentation, existing tests, and a nearby example.

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

## Engineering workflow

Treat an authorized implementation as an engineering change, not only
a source-file edit.

Before changing behavior:

1. inspect the current implementation
2. inspect relevant tests
3. inspect relevant canonical documentation
4. inspect the nearest useful example when applicable
5. understand the architectural boundary being changed

When behavior changes:

- add or update focused tests when the behavior can reasonably be tested
- prefer regression tests for bug fixes
- update relevant documentation when public APIs, configuration,
  architecture, workflows, or documented behavior change
- update examples when they are part of the public usage pattern
- do not create redundant tests or documentation merely because a file
  was edited

After modifying Python:

- format the modified Python files
- run the narrowest relevant tests
- run broader tests when the change affects shared engine infrastructure
  or multiple subsystems
- distinguish checks actually executed from checks merely recommended

If verification cannot be executed, explain what remains unverified.

An explicit request to implement, apply, refactor, fix, or update a
feature also authorizes directly necessary supporting changes such as
tests, documentation, examples, and formatting unless the user limits
the requested scope.

## Verification

Use docs/ai/verification.md as the canonical verification checklist.

Run commands from the appropriate project environment.

Install engine dependencies:

    poetry install

Run a documented example:

    poetry run python manage.py run example scenes.on_present

Prefer targeted verification before the full test suite.

Interactive games require a desktop environment. MP4 encoding requires
FFmpeg.

Never claim a test, formatter, example, lint check, or other command
was executed unless a tool or the user confirms execution.

## Documentation and configuration

Keep documentation synchronized with the behavior it describes.

Public API, configuration, lifecycle, architectural, or workflow changes
should trigger inspection of relevant canonical documentation and
examples.

Internal refactors that preserve documented behavior do not require
documentation changes solely because implementation moved.

Keep local credentials in untracked configuration. Use placeholders in
.env.example. Do not request or expose secret values through MCP tools.

## Static analysis

Tatuy uses mypy and pylint in addition to formatting and tests.

When Python code changes, inspect relevant mypy and pylint findings when
the corresponding tools are available.

Treat static-analysis findings as engineering feedback, not instructions
to modify architecture blindly.

Safe mechanical corrections may be applied as part of an already
authorized implementation when they are local and preserve behavior.

Do not make broader design, typing, API, inheritance, configuration, or
suppression changes solely to satisfy mypy or pylint without presenting
the issue and proposed solution for developer approval first.

In particular, require approval before:

- adding or broadening `# type: ignore`
- adding or broadening pylint disables
- changing public types or signatures
- changing inheritance or protocols
- introducing casts that hide uncertain types
- weakening mypy or pylint configuration
- restructuring architecture solely for static analysis
- changing runtime behavior to satisfy a checker

Prefer fixing the underlying issue over suppressing it.

When reporting a finding, distinguish:

1. the diagnostic
2. why it occurs
3. whether it exposes a real defect or only a tooling limitation
4. the recommended fix
5. alternatives and tradeoffs when relevant

## Scoped guidance

Apply additional AGENTS.md guidance found in directories relevant to
the task. More specific guidance refines these repository-wide rules.
