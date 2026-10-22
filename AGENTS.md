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
2. inspect relevant source/tooling tests when the change affects `src/`
3. inspect relevant canonical documentation
4. for changes under `src/tatuy`, inspect the nearest relevant fundamental
   and search affected experiments and games
5. understand the architectural boundary being changed

When behavior changes:

- add or update focused source/tooling tests when the behavior can
  reasonably be tested
- prefer regression tests for bug fixes
- update relevant documentation when public APIs, configuration,
  architecture, workflows, or documented behavior change
- add, update, or remove affected examples after Tatuy engine changes
- do not create redundant tests or documentation merely because a file
  was edited

After modifying Python:

- format all modified Python files, including tests
- run the narrowest relevant pytest tests for Tatuy-owned source/tooling
- run broader tests when the change affects shared engine infrastructure
  or multiple subsystems
- run mypy and pylint only against relevant non-test Python code
- distinguish checks actually executed from checks merely recommended

If verification cannot be executed, explain what remains unverified.

An explicit request to implement, apply, refactor, fix, or update a
feature also authorizes directly necessary supporting changes such as
tests, documentation, examples, package structure, formatting, and
removal of content made obsolete by that implementation unless the user
limits the requested scope.

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

## Python package structure

New importable Python package directories under `src/` must include an
`__init__.py`.

When creating a file inside a new source package:

1. create the package directory
2. create its `__init__.py`
3. create the implementation files
4. update package exports when the new API is intended to be exported

Do not require `__init__.py` merely because a corresponding directory
exists under `tests/`. Test directories may mirror the source hierarchy
without becoming Python packages unless existing local conventions require
otherwise.

Examples, experiments, and games follow their existing runnable-target
layout rather than the source-package rule.

## Examples and engine changes

Examples are executable documentation and integration pressure for Tatuy.

Every addition, behavior change, or removal under `src/tatuy` requires an
example review.

Inspect:

1. the nearest relevant fundamental example
2. relevant experiments that exercise the affected capability
3. relevant games when they depend on the affected behavior

After inspection, add, update, or remove examples as needed.

A new public engine capability should normally have a focused fundamental
example unless an existing example already demonstrates it clearly.

Internal changes may require no example edits, but that conclusion should
be made only after reviewing affected examples.

Do not create pytest tests for examples, experiments, or games. They are
validated through their executable behavior and their use of the current
Tatuy API.

## Source and test structure

The pytest suite under `tests/` validates Tatuy-owned source and tooling
under `src/`.

Do not add pytest coverage for fundamentals, experiments, or games.
Those are executable validation targets with different purposes.

Test directories may mirror the source hierarchy without becoming Python
packages unless their local structure explicitly requires package
semantics.

Tests should cover applicable input/output behavior, meaningful edge
cases, and observable side effects. See docs/ai/verification.md.

Test files are formatted but are not checked with mypy or pylint.

## Scoped guidance

Apply additional AGENTS.md guidance found in directories relevant to
the task. More specific guidance refines these repository-wide rules.
