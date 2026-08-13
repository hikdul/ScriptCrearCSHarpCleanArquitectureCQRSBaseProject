# Feature: Create Match

## Objective

A match is created when two users like each other.

## Required behavior

Given two different users:

1. User A likes User B.
2. User B likes User A.
3. The system must recognize that a match exists between them.

## Rules

- A user cannot match with themselves.
- A match only exists when the two users have mutually liked each other.
- A single like is not a match.
- The same pair of users must not create multiple matches.
- The behavior belongs to the Domain layer.
- The implementation must not introduce persistence concerns.

## Acceptance criteria

### Scenario 1 — Reciprocal likes create a match

Given User A and User B.

When User A likes User B.

And User B likes User A.

Then User A and User B are matched.

### Scenario 2 — One-way like does not create a match

Given User A and User B.

When User A likes User B.

Then User A and User B are not matched.

### Scenario 3 — A user cannot match with themselves

A user must never be considered matched with itself.

### Scenario 4 — Duplicate mutual likes do not create multiple matches

The relationship between two users represents one match.

## Constraints

Follow all rules defined in `AGENTS.md`.

Do not:

- modify existing tests
- weaken existing tests
- introduce unnecessary abstractions
- introduce persistence
- introduce Application or Infrastructure dependencies
- modify unrelated functionality

The implementation must remain inside the Domain layer.

## TDD

The first step is to create executable tests from this specification.

The tests must initially fail because the required behavior does not yet exist.

Do not implement production code before establishing the RED state.
