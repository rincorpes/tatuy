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
- nearest fundamental example when applicable

## Tests

Identify the narrowest relevant tests before changing behavior.

For behavior changes, add or update focused tests when practical.

For bug fixes, prefer a regression test that fails for the original bug
and passes after the fix.

If the affected behavior has no tests, determine whether the absence is
intentional or a coverage gap.

When implementation changes are authorized, creating directly relevant
tests is part of completing the change unless the user limits the scope.

Run targeted tests first.

Run broader tests when the change affects shared infrastructure,
cross-cutting behavior, or multiple features.

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

Find the nearest fundamental example.

Use experiments for architecture pressure, not as unquestioned API
guidance.

Update examples when public usage or recommended workflows change.

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