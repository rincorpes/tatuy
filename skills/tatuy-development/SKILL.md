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
4. inspect existing tests for that behavior
5. inspect relevant canonical documentation
6. inspect a nearby fundamental example when useful
7. identify the architectural boundary affected by the change

Do not infer an API from documentation alone when current source can verify it.

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
- creating or updating focused tests
- updating relevant documentation
- updating examples when public usage changes
- formatting modified Python files

Do not mechanically add tests or documentation for every edit.

Add or update tests when observable behavior changes or when a regression
test can protect a bug fix.

Update documentation when public APIs, configuration, architecture,
lifecycle semantics, workflows, or documented behavior change.

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

1. format the modified Python files when formatting tools are available
2. run the narrowest relevant tests
3. inspect failures and fix regressions caused by the change
4. run broader tests when shared engine infrastructure was changed

Prefer focused verification first.

Examples:

- one component change -> component/feature tests
- collision change -> collision tests
- lifecycle infrastructure -> lifecycle tests plus broader engine tests
- MCP server change -> MCP server tests
- cross-cutting engine change -> targeted tests followed by the full suite

Do not claim formatting or tests succeeded unless the corresponding tool
actually ran successfully.

If a verification tool is unavailable, say what remains unverified.

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

## Completion

Before reporting an authorized implementation as complete, account for:

- implementation
- tests
- documentation
- examples when relevant
- formatting
- executed verification

Report what changed and which verification was actually executed.
