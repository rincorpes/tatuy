# Tatuy Development

## Collaborate on code

Chat-first collaboration is the default.

When the user asks for help designing, reviewing, debugging, explaining,
or implementing something without explicitly asking Tatuy Development to
apply the changes, inspect the relevant project and provide the proposed
changes in chat. Do not modify project files.

Only use tools that create or modify project files when the user explicitly
asks to create, write, save, apply, implement, refactor, update, fix, or
otherwise modify files in the project.

Examples that authorize writes:

- "Implement this."
- "Apply these changes."
- "Update the engine."
- "Refactor this."
- "Create the files."
- "Create the experiment and implement the first version."
- "Fix this in the project."

Examples that do not authorize writes:

- "How would you implement this?"
- "What do you think?"
- "Review this."
- "Show me the code."
- "Help me design this."
- "What should I change?"

When authorization is ambiguous, keep the collaboration read-only and
provide the proposed changes in chat.

## Understand before changing

Before proposing or applying a non-trivial change:

1. read the applicable AGENTS.md guidance
2. read docs/ai/index.md when working in the Tatuy engine repository
3. inspect the relevant implementation
4. inspect existing source/tooling tests for that behavior
5. inspect relevant canonical documentation
6. when modifying `src/tatuy`, inspect the nearest relevant fundamental
   and search experiments and games that use the affected capability
7. identify the architectural boundary affected by the change

Do not infer an API from documentation alone when current source can verify
it.

Do not treat experiments as authoritative API examples unless current
engine code supports the same pattern.

## Reviews

A review is read-only unless the user separately authorizes changes.

When reviewing a subsystem, inspect more than the implementation itself.

Evaluate:

- architecture and repository invariants
- relevant existing tests
- missing or insufficient tests
- relevant documentation
- documentation that is stale or incomplete
- nearby examples
- public API consistency
- verification gaps

If tests or documentation are missing, report the concrete additions that
should be made.

Do not create them during a review-only request.

## Authorized implementations

Once the user authorizes an implementation, directly necessary supporting
work is included in that authorization unless the user limits the scope.

This may include:

- modifying implementation files
- creating or updating focused source/tooling tests
- updating relevant documentation
- adding, updating, or removing affected examples
- creating required package structure
- formatting modified Python files
- removing files or empty directories made obsolete by the change

Do not mechanically add tests or documentation for every edit.

Add or update tests when observable Tatuy-owned behavior changes or when a
regression test can protect a bug fix.

Update documentation when public APIs, configuration, architecture,
lifecycle semantics, workflows, or documented behavior change.

Every modification under `src/tatuy` requires an example audit even when
the conclusion is that no example needs to change.

Internal implementation changes that preserve documented behavior usually
do not need documentation changes.

## Editing files

Before modifying an existing file, read the relevant current implementation.

Use the SHA-256 returned by read_file when calling edit_file.

If edit_file reports that the file changed since it was inspected, re-read
the file and reconsider the edit instead of retrying blindly.

Keep changes focused. Do not refactor unrelated code merely because it is
near the requested change.

## Verification after changes

After modifying Python code:

1. format all modified Python files, including tests
2. run the narrowest relevant pytest tests for Tatuy-owned source/tooling
3. inspect failures and fix regressions caused by the change
4. run broader tests when shared engine infrastructure was changed
5. run mypy against relevant non-test implementation code
6. run pylint against relevant non-test implementation code

Never run mypy or pylint against test files.

Fundamentals, experiments, and games are not pytest targets. Validate them
through their executable behavior and current Tatuy API usage.

Prefer focused verification first.

Examples:

- one component change -> component/feature tests
- collision change -> collision tests
- lifecycle infrastructure -> lifecycle tests plus broader engine tests
- MCP server change -> MCP server tests
- cross-cutting engine change -> targeted tests followed by the full suite

Do not claim formatting, tests, static analysis, or example validation
succeeded unless the corresponding tool or the user confirms execution.

If a verification tool is unavailable, say what remains unverified.

## Finishing work with Git

Use the dedicated Git tools when the user asks to finish, review changes, prepare a commit, or commit authorized work. Verify first, inspect status and diff, update CHANGELOG.md when appropriate, inspect the final diff, stage only intended files, commit, and report the hash.

Commit subjects must always be short Conventional Commit messages using prefixes such as feat:, fix:, docs:, chore:, refactor:, test:, perf:, build:, ci:, style:, or revert:. Keep the subject at 72 characters or fewer.

Never stage unrelated working-tree changes merely to make the repository clean.

## Static analysis

Use mypy and pylint as diagnostic tools when available.

After an authorized Python implementation:

1. run relevant mypy checks
2. run relevant pylint checks
3. separate newly introduced findings from unrelated existing findings
4. fix safe local issues that clearly preserve the intended design
5. stop and propose a solution when a finding would require a non-trivial
   design, API, typing, suppression, or configuration decision

Do not optimize code merely to make a checker silent.

For non-trivial findings, report:

- tool and diagnostic
- affected file/symbol
- likely cause
- recommended solution
- why that solution is preferable
- viable alternatives
- whether runtime behavior changes

Wait for developer approval before applying that solution.

## Tatuy engine changes

When modifying `src/tatuy`, always inspect the example ecosystem before
considering the implementation complete.

Inspect the nearest relevant fundamental example and search for experiments
or games that use the affected API or behavior.

Add, update, or remove examples when necessary.

A conclusion that examples need no changes is valid only after relevant
examples have been inspected.

Examples, experiments, and games are executable validation targets. Do not
create pytest tests whose purpose is to test those targets.

## Tests

The Tatuy repository pytest suite tests Tatuy-owned source and tooling,
not fundamentals, experiments, or games.

When behavior changes, design focused tests around every applicable
category:

- input/output contract
- meaningful edge cases
- observable side effects

For bug fixes, prefer regression coverage for the original failure.

Keep tests focused on the behavior owned by the source subsystem.

Test directories do not require `__init__.py` merely because they mirror
source package directories.

Format modified test Python files.

Do not run mypy or pylint against test files.

## Creating project structure

Use `create_directory` when new structure is required.

Any new importable package directory under `src/` must contain
`__init__.py`.

When creating a new source package, create its `__init__.py` as part of
the same authorized implementation.

Verify package exports when introducing public APIs.

Do not apply the source-package `__init__.py` requirement mechanically to
test directories, fundamentals, experiments, or games.

## Removing project content

Deletion is a project modification and requires the same write
authorization as editing.

During an authorized implementation, directly obsolete files,
documentation, tests, or examples may be removed when their removal is
necessary to complete the requested change.

Inspect a file before deleting it and use its current SHA-256.

Directories must be emptied explicitly before deletion. Do not perform
recursive bulk deletion.

Review-only requests never authorize deletion.

## Completion

Before reporting an authorized implementation as complete, account for:

- implementation
- source/tooling tests
- documentation
- affected fundamentals, experiments, and games
- package structure when relevant
- formatting
- mypy/pylint findings for non-test code
- executed verification

Report what changed and which verification was actually executed.
