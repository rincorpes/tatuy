# Verification

Verification is part of completing a Tatuy engineering change.

## Before changing code

Verify the relevant:

- import paths
- API signatures
- system phase
- system order
- resource availability
- lifecycle timing
- built-in activation
- scene configuration timing
- architectural invariants
- existing tests
- canonical documentation
- for `src/tatuy` changes, the nearest relevant fundamental
- experiments and games using the affected capability

## Tests

The Tatuy pytest suite validates Tatuy-owned source and tooling under
`src/`.

Do not create pytest tests for:

- `examples/fundamentals`
- `examples/experiments`
- `examples/games`

Those targets provide executable documentation, architectural pressure,
and integration validation rather than pytest coverage.

Tests should evaluate each applicable behavior through three lenses:

### Input / output

Verify representative inputs and their observable outputs.

An output may be:

- a return value
- resulting component/resource state
- an emitted value
- a created object
- an expected exception

### Edge cases

Verify meaningful boundaries and failure conditions such as:

- empty input
- missing state
- invalid input
- minimum/maximum values
- lifecycle boundaries
- ordering boundaries
- duplicate registration
- absent resources
- repeated calls

Choose edge cases relevant to the actual contract rather than creating
arbitrary cases for coverage.

### Side effects

Verify externally observable effects when behavior produces them, such as:

- world mutations
- resource mutations
- entity creation/destruction
- queue operations
- registrations
- events
- filesystem changes
- backend calls
- collaborator calls

Use mocks or fakes when the side effect belongs to another subsystem and
the test is intended to isolate the current behavior.

Not every behavior has meaningful cases in all three categories. Cover
every category that applies rather than manufacturing unnecessary tests.

For bug fixes, prefer a regression test that demonstrates the original
failure.

Identify the narrowest relevant tests before changing behavior.

Run targeted tests first. Run broader tests when the change affects shared
infrastructure, cross-cutting behavior, or multiple features.

Test files are formatted with the repository formatter but are not targets
for mypy or pylint.

Do not claim tests were executed unless a tool or the user confirms
execution.

## Formatting

Format modified Python files using the repository-configured formatter and
import ordering.

Prefer formatting only files touched by the task instead of creating
unrelated repository-wide changes.

Formatting is part of an authorized Python implementation when formatting
tools are available.

## Examples

Examples are executable documentation and integration pressure for Tatuy.

Every addition, behavior change, or removal under `src/tatuy` requires an
example audit.

Inspect:

1. the nearest relevant fundamental
2. experiments using the affected capability
3. games using the affected capability

Add, update, or remove examples when necessary.

A new public engine capability should normally have a focused fundamental
unless an existing fundamental already demonstrates it clearly.

Internal changes may require no example edits, but that conclusion should
be made only after reviewing affected examples.

Use experiments for architecture pressure, not as unquestioned API
guidance.

Fundamentals, experiments, and games are not pytest test targets.

## Documentation

Inspect relevant canonical documentation whenever behavior changes.

Update documentation when the change affects:

- public APIs
- configuration
- lifecycle semantics
- architecture
- supported workflows
- user-facing behavior
- documented examples

Do not update documentation solely because internal implementation moved
without changing the documented contract.

## Environment

Interactive examples require a desktop environment.

Video encoding requires FFmpeg.

Verification subprocesses must not receive MCP, tunnel, API, or other
unrelated secrets from the server environment.

## Reporting

Distinguish clearly between:

- checks executed successfully
- checks executed and failed
- checks not executed
- checks only recommended