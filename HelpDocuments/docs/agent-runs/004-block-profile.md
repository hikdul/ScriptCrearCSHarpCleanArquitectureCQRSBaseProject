
# Feature: Block Profile

## Objective

A user can block another user's profile.

Blocking a profile prevents further interaction between the two users from the perspective of the user who created the block.

The behavior belongs entirely to the Domain layer.

---

## Required behavior

Given two different users:

1. User A blocks User B.
2. The block must be observable by User A.
3. User A must not be able to like User B while the block exists.
4. Blocking User B removes any existing like from User A toward User B.
5. If User A and User B had a mutual like, blocking User B removes the match.
6. The block is directional: blocking B does not automatically mean that B has blocked A.

---

## Rules

* A user cannot block themselves.
* A user cannot block the same profile twice.
* Blocking a profile must be observable.
* Blocking a profile removes the user's existing like toward that profile.
* A blocked profile cannot be liked by the user who created the block.
* A block removes an existing match between the two users.
* Blocking is directional.
* The behavior belongs to the Domain layer.
* The implementation must not introduce persistence concerns.

---

## Acceptance criteria

### Scenario 1 — User can block another profile

Given User A and User B.

When User A blocks User B.

Then User A reports that User B is blocked.

---

### Scenario 2 — User cannot block themselves

Given User A.

When User A attempts to block themselves.

Then the operation is rejected with a domain error.

---

### Scenario 3 — Duplicate blocks are rejected

Given User A and User B.

When User A has already blocked User B.

And User A attempts to block User B again.

Then the operation is rejected with a domain error.

---

### Scenario 4 — A blocked profile cannot be liked

Given User A and User B.

When User A blocks User B.

And User A attempts to like User B.

Then the operation is rejected with a domain error.

---

### Scenario 5 — Blocking removes an existing like

Given User A and User B.

When User A likes User B.

And User A blocks User B.

Then User A no longer reports that User B has been liked.

---

### Scenario 6 — Blocking removes a match

Given User A and User B.

When User A likes User B.

And User B likes User A.

Then User A and User B are matched.

When User A blocks User B.

Then User A and User B are no longer matched.

---

### Scenario 7 — Blocking is directional

Given User A and User B.

When User A blocks User B.

Then User A reports User B as blocked.

And User B does not automatically report User A as blocked.

---

## Constraints

Follow all rules defined in `AGENTS.md`.

Do not:

* modify existing tests
* weaken existing tests
* introduce unnecessary abstractions
* introduce persistence
* introduce Application or Infrastructure dependencies
* introduce API dependencies
* modify unrelated functionality
* introduce a Match entity
* implement Unblock behavior

The implementation must remain inside the Domain layer.

---

## TDD

The first implementation step is to create executable tests from this specification.

The tests must initially fail because the required blocking behavior does not yet exist.

Do not implement production code before establishing the RED state.

The TDD cycle is:

```text
RED
 ↓
GREEN
 ↓
REFACTOR
```

---

## Validation

The feature is complete only when:

1. All acceptance criteria have automated tests.
2. Tests pass.
3. The complete solution builds successfully.
4. The complete test suite passes.
5. Architecture tests pass.
6. No unrelated files are modified.
