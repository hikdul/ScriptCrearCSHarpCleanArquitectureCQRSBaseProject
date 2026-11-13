# TDP Prompt — Create Match Tests

## Objective

Transform the feature specification into executable acceptance tests.

## Source of truth

The source of truth is:

`docs/specifications/000-example-specification.md`

The example specification shows the required structure for every feature
specification. Replace the placeholder content with the real feature rules
before writing tests.

The project rules are defined in:

`AGENTS.md`

## Task

Read the specification and existing Domain code.

Create tests representing the required behavior.

The tests must describe behavior, not implementation details.

## Important constraint

Do NOT implement the production behavior.

Do NOT modify existing production code.

Do NOT modify existing tests.

Only create the new tests required by the specification.

## Expected state

After creating the tests:

```text
RED
```

The new tests should fail because the required Match behavior does not yet
exist.

Test quality

Tests should:

* describe business behavior
* use meaningful names
* be independent
* be deterministic
* avoid implementation details
* follow the existing test conventions

Prefer names such as:
```
Reciprocal_likes_create_match
One_way_like_does_not_create_match
User_cannot_match_with_themselves
Duplicate_mutual_likes_do_not_create_multiple_matches
```

## Validation

After creating the tests:

1. Run the relevant Domain tests.
2. Confirm that the new tests fail.
3. Run the existing test suite.
4. Confirm that existing tests still pass.

Do not change production code to make the new tests pass.

## Completion criteria

The task is complete when:

* The specification has been translated into executable tests.
* New tests fail because the behavior is not implemented.
* Eisting tests continue to pass.
* No production code was modified.
* No existing tests were modified.
* No unrelated files were modified.

Report:

1. Tests created.
2. Tests executed.
3. RED result.
4. Existing test result.
5. Files changed.
