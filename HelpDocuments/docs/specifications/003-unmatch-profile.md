
# Feature: Unmatch Profile

## Objective

A user must be able to remove a like from another user.

If two users were mutually liking each other, removing one of those likes must also remove the match between them.

---

## Required behavior

Given two different users:

1. User A likes User B.
2. User B likes User A.
3. User A and User B are matched.
4. User A removes their like from User B.
5. User A and User B are no longer matched.

---

## Rules

* A user can remove a like from another user.
* A user cannot remove a like from themselves.
* Removing an existing like succeeds.
* Removing a like that does not exist must not create a like or a match.
* A match only exists while both users have mutually liked each other.
* Removing either side of a mutual like relationship removes the match.
* Removing a like must not affect likes involving other users.
* The behavior belongs to the Domain layer.
* The implementation must not introduce persistence concerns.

---

## Acceptance criteria

### Scenario 1 — User can remove an existing like

Given User A and User B.

When User A likes User B.

And User A removes the like from User B.

Then User A has not liked User B.

---

### Scenario 2 — Removing a like removes a match

Given User A and User B.

When User A likes User B.

And User B likes User A.

Then User A and User B are matched.

When User A removes the like from User B.

Then User A and User B are no longer matched.

---

### Scenario 3 — Removing a non-existing like does not create a relationship

Given User A and User B.

When User A removes the like from User B.

Then User A has not liked User B.

And User A and User B are not matched.

---

### Scenario 4 — A user cannot remove a like from themselves

Given User A.

When User A attempts to remove their own like.

Then the operation is rejected with a domain error.

---

### Scenario 5 — Removing one like does not affect other relationships

Given User A, User B and User C.

When User A likes User B.

And User A likes User C.

When User A removes the like from User B.

Then User A has not liked User B.

And User A still likes User C.

---

## Constraints

Follow all rules defined in `AGENTS.md`.

Do not:

* modify existing tests
* weaken existing tests
* introduce unnecessary abstractions
* introduce persistence
* introduce Application or Infrastructure dependencies
* introduce HTTP concerns
* introduce authentication concerns
* modify unrelated functionality
* implement functionality outside this specification

The implementation must remain inside the Domain layer.

---

## TDD

The first implementation step is to create executable tests from this specification.

The tests must initially fail because the required behavior does not yet exist.

Do not implement production code before establishing the RED state.

---

## Validation

The feature is complete only when:

1. All acceptance criteria have automated tests.
2. The tests initially fail before implementation.
3. Production code makes all tests pass.
4. Existing tests continue to pass.
5. Architecture tests pass.
6. The complete solution builds successfully.
7. No unrelated files are modified.
