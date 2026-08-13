# Feature: Like Profile

## Objective

Implement the minimum production code required to satisfy the existing
tests for the "Like Profile" behavior.

## Context

The domain tests already define the required behavior.

The implementation must satisfy those tests without changing their expected
behavior.

The feature belongs to the Domain layer.

## Required behavior

A User must be able to like another User.

A User must not be able to like themselves.

A User must not be able to like the same User more than once.

## Implementation constraints

Follow the rules defined in AGENTS.md.

In particular:

- Keep the implementation in the Domain layer.
- Do not introduce Application, Infrastructure or API dependencies.
- Do not add persistence concerns.
- Do not add Entity Framework dependencies.
- Do not add unnecessary abstractions.
- Do not add speculative functionality.
- Do not modify existing tests to make them pass.
- Do not modify unrelated files.
- Keep the implementation small and explicit.
- Follow Clean Code principles.
- Preserve the existing architecture.

## TDD state

The tests have already been created.

The next objective is GREEN:

    RED -> GREEN

Implement only what is necessary for the existing tests to pass.

## Validation

After implementation:

1. Run the Domain tests.
2. Run all tests.
3. Run the build.
4. Verify that architecture tests still pass.
5. Inspect the Git diff.
6. Verify that no unrelated files were modified.

Required commands:

```bash
dotnet test tests/Matchly.Domain.Tests/Matchly.Domain.Tests.csproj
dotnet test
dotnet build
git diff
git status
```

## Completion criteria

The feature is complete only if:

* The three Like Profile behaviors are implemented.
* Domain tests pass.
* All project tests pass.
* Build passes.
* Architecture tests pass.
* No tests were weakened or removed.
* No unrelated functionality was introduced.
* No unrelated files were modified.

If validation fails, diagnose the failure and fix the production code.

Do not modify the tests merely to obtain a passing result.

## Agent output

When finished, report:

1. Files changed.
2. Production behavior implemented.
3. Tests executed.
4. Validation results.
5. Any remaining issues.

Do not claim success without executing the validation commands.
