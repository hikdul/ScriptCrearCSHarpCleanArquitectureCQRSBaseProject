# Feature: Like Profile

**ID:** 001
**Status:** Ready
**Layer:** Domain
**Type:** Business Behavior

---

## 1. Goal

Allow a user to like another user's profile.

The Domain model must enforce the business rules associated with liking a profile.

---

## 2. Context

Matchly is a dating application.

A user can express interest in another user's profile by liking it.

The like behavior is a Domain business rule and must therefore be implemented in the Domain layer.

The current feature only covers the act of liking a profile.

Persistence, HTTP APIs, authentication and matching are outside the scope of this feature.

---

## 3. Business Rules

### BR-001 — A user can like another user

A user may like another user.

### BR-002 — A user cannot like themselves

A user must not be allowed to like their own profile.

Attempting to do so must result in a domain error.

### BR-003 — Duplicate likes are forbidden

A user must not like the same profile more than once.

Attempting to repeat an existing like must result in a domain error.

### BR-004 — A successful like is observable

After a successful like, the source user must report that the target user has been liked.

---

## 4. Acceptance Criteria

### AC-001 — User can like another user

**Given** a source user and a different target user

**When** the source user likes the target user

**Then** the source user reports that the target user has been liked.

---

### AC-002 — User cannot like themselves

**Given** a user

**When** the user attempts to like themselves

**Then** the operation is rejected with a domain error.

---

### AC-003 — User cannot like the same profile twice

**Given** a source user that has already liked a target user

**When** the source user attempts to like the same target user again

**Then** the operation is rejected with a domain error.

---

## 5. Constraints

The implementation must:

* Keep the business behavior in the Domain layer.
* Keep the Domain layer independent from infrastructure frameworks.
* Not introduce persistence concerns.
* Not introduce HTTP concerns.
* Not introduce authentication concerns.
* Not introduce matching behavior.
* Not implement functionality outside this specification.
* Follow the project rules defined in `AGENTS.md`.
* Follow the TDP workflow defined in `docs/workflows/tdp-feature-workflow.md`.

---

## 6. Out of Scope

The following are explicitly excluded from this feature:

* User registration.
* User authentication.
* Profile creation.
* Profile editing.
* Profile discovery.
* Match creation.
* Mutual likes.
* Messaging.
* Notifications.
* Persistence.
* Database integration.
* API endpoints.
* Frontend implementation.

---

## 7. Expected Domain Behavior

The Domain model should expose behavior that allows the application to express:

```text
user likes target
```

and determine:

```text
user has liked target
```

The specification does not prescribe the internal implementation.

The implementation details are left to the agent as long as all business rules and acceptance criteria are satisfied.

---

## 8. Validation

The feature is complete only when:

1. All acceptance criteria are represented by automated tests.
2. The tests pass.
3. The complete solution builds successfully.
4. The complete test suite passes.
5. Architecture tests pass.
6. No unrelated files are modified.
