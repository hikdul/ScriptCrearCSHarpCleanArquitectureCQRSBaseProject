# Specification Format and Guide

**Status:** Reference — not a feature to implement
**Purpose:** Define how every feature specification in this repository is
written, reviewed, implemented and validated.

This document is the bootstrap reference for `docs/specifications/`. It
defines the specification method used in this repository: a specification is
the source of truth for behavior, and the tests are its executable form.

Delete nothing here by accident: future features depend on these conventions.
The first real feature specification is `001-<short-name>.md`.

---

## 1. Why specifications exist

A specification answers **what the system must do**, not how the code should be
written. It exists so that:

- the user can review the intended behavior before code is written;
- the Test Agent can translate acceptance criteria into tests without
  inventing business decisions;
- the Implementation Agent knows when the feature is complete and when it is
  not;
- the Validation Agent can prove completion against observable behavior;
- later changes can be understood without reading the entire history.

A specification is not a design document, a task list, or a place to prescribe
classes. Architecture and design belong in `docs/architecture/` and in the
implementation, subject to the rules in `AGENTS.md`.

---

## 2. Location, naming and status

Specifications live in:

```text
docs/specifications/
```

The naming convention is:

```text
<feature-id>-<short-name>.md
```

Examples:

```text
001-leave-workspace.md
002-invite-member.md
003-transfer-ownership.md
```

Rules:

- The identifier is a three-digit sequential number (`001`, `002`, ...).
- The identifier is unique and never reused for a different feature.
- The short name is lowercase, hyphenated and descriptive.
- One file describes one feature. Do not create a specification that covers
  several unrelated capabilities.
- The feature branch uses the same identifier:
  `feature/<feature-id>-<short-name>`.

Every specification starts with a status line:

| Status | Meaning |
| --- | --- |
| `Draft` | Being written or under review; not yet a source of truth. |
| `Approved` | Reviewed and accepted as the source of truth; implementation may begin. |
| `Implemented` | Every acceptance criterion has code and a test, and the required suite is green. |

The status is changed to `Implemented` only during the approved close. An
agent must never mark a feature implemented while it awaits approval.

A specification delivered in increments may add an implementation-status table
listing which areas are complete. It must not claim `Implemented` for behavior
that is not built and tested.

---

## 3. Required structure

Every feature specification contains these sections, in this order:

```text
# <Feature Name>

Status: Draft

## Objective
## Context
## Dependencies
## Business Rules
## Acceptance Criteria
## Constraints
## Technical Requirements
## Out of Scope
## TDD
## Open Questions
```

Sections may be expanded, but not removed. If a section genuinely does not
apply, keep it and state why (for example, `## Dependencies` — none).

The document must stay focused. A reviewer should be able to read the
Objective, Business Rules and Acceptance Criteria and know exactly what is
being built.

---

## 4. Section-by-section guidance

### 4.1 Title and status

Use a human-readable feature name. The status is one of the values in section
2. Include the feature id in the file name, not necessarily in the title.

Good:

```text
# Leave a workspace
```

Avoid vague titles such as `# Feature 12` or `# Changes`.

### 4.2 Objective

Describe the business capability and why it exists. Answer:

```text
What behavior is introduced?
Why does the behavior exist?
```

Prefer:

```text
A workspace member can leave a workspace without deleting the workspace.
```

Avoid:

```text
Create a LeaveWorkspaceService with an IWorkspaceRepository.
```

Implementation terms are allowed only when the objective is itself an
architectural constraint (for example, "the check must be enforced by the
database").

### 4.3 Context

Explain where the behavior fits:

- the actors involved;
- the existing capability it extends or replaces;
- the data or state it depends on;
- the observable outcome for the user.

Inspect `docs/specifications/`, `src/` and `tests/` before writing this
section. Do not assume a capability does not exist; check.

### 4.4 Dependencies

List what must already exist for this feature to make sense:

- earlier features by identifier;
- domain concepts or entities;
- external services;
- configuration or infrastructure.

State whether the dependency is already implemented, planned, or out of scope.
If a dependency is missing, the Feature is not ready to implement; report it
instead of inventing it.

### 4.5 Business rules

Business rules are invariants that must always hold. They are explicit,
deterministic, independently testable and implementation-independent.

Give each rule an identifier:

```text
BR-001 A member who is the last owner cannot leave the workspace.
BR-002 A member who has already left cannot leave again.
BR-003 Leaving does not delete the member's historical records.
```

Rules must describe behavior, not code. Do not hide a rule inside an
acceptance criterion, and do not duplicate it in both places: the rule states
the invariant, the criterion proves it.

### 4.6 Acceptance criteria

Acceptance criteria describe observable behavior. Every meaningful business
rule must have at least one criterion.

Give each criterion an identifier and write it as Given/When/Then:

```text
### AC-001 — The last owner cannot leave
Given a workspace with exactly one owner
When the owner requests to leave
Then the request is refused with `LastOwnerCannotLeave`
And the workspace membership is unchanged
```

Rules for good criteria:

- One observable outcome per scenario; split when a scenario proves two things.
- Describe the outcome, not the method that produces it.
- Name the error or result the caller observes, not an internal exception type.
- State what must remain unchanged when the operation is refused.
- Use concrete starting conditions, not "valid data" or "normal state".
- Avoid implementation details such as "calls repository X" or "sets a field".

Prefer:

```text
A user cannot archive a task that is already archived.
```

Avoid:

```text
ArchiveTaskHandler must call _repository.Update.
```

### 4.7 Edge cases

Edge cases are acceptance criteria, not a separate category. When a feature has
boundaries, add explicit criteria for:

- empty or missing input;
- duplicate operations (idempotency);
- concurrent or repeated requests;
- unauthorized actors;
- objects that are in an unexpected state;
- the boundary values of a limit.

Do not leave an edge case implied. An implied case is a decision the
Implementation Agent will make on the user's behalf.

### 4.8 Constraints

State the architectural layer and the forbidden concerns explicitly.

```text
This behavior belongs to the Domain layer.
Domain must not depend on Application, Infrastructure, API, ASP.NET Core,
Entity Framework Core, or HTTP.

Persistence is out of scope for this feature.
```

For cross-layer features, describe each layer's responsibility:

| Layer | Responsibility |
| --- | --- |
| Domain | Invariants and domain decisions. |
| Application | Orchestration through a command/query handler. |
| Infrastructure | Persistence implementation only, if required. |
| API | HTTP mapping and dispatch through the mediator. |

Constraints must match `AGENTS.md` and `docs/architecture/`. If a feature
appears to require a new architectural decision, stop and report the
ambiguity. Do not silently invent a convention.

The security project exists for security abstractions. It must not depend on
the other layers.

### 4.9 Technical requirements

List technical constraints that are genuinely required by the feature, for
example:

- an index or uniqueness rule that must be enforced by the database;
- a transaction boundary;
- a migration requirement;
- a deterministic clock or time zone rule;
- a size or format limit;
- a compatibility requirement.

Do not use this section to prescribe classes, methods or project structure.
Those are implementation decisions governed by the architecture and the
existing code.

### 4.10 Out of scope

Explicitly list related behavior that is **not** part of this feature. This is
the main defense against autonomous scope expansion.

```text
Out of scope:
- notifications
- audit history
- UI changes
- bulk operations
- migration of existing data
```

If an item is uncertain, ask; do not silently include it.

### 4.11 TDD

Every specification ends with the same mandatory statement:

```text
The first implementation stage is test creation.

Tests must initially fail because the required behavior does not yet exist.
Production implementation must not begin before RED has been established.
```

Feature-specific test notes may follow, such as which test project should own
each criterion or which tier is required. Keep them about evidence, not
implementation.

### 4.12 Open questions

List unresolved decisions that affect behavior. Each question should name the
decision required and the options considered.

If a question blocks implementation, the specification is not ready. The
Specification Agent reports `SPECIFICATION BLOCKED` rather than guessing.

---

## 5. Traceability

Every business rule and acceptance criterion must be traceable through the
workflow:

```text
BR-001 ──► AC-001 ──► test name / filter ──► implementation ──► validation
```

A useful specification includes a mapping table:

| Rule | Criterion | Test |
| --- | --- | --- |
| BR-001 | AC-001 | `Last_owner_cannot_leave_workspace` |
| BR-002 | AC-002 | `Member_who_already_left_cannot_leave_again` |

At review time, an unmapped criterion is unproven. A mapped test that does not
exist is a false claim. Update the table when tests move or are renamed.

---

## 6. How agents interpret a specification

The workflow is defined in `docs/workflows/tdp-feature-workflow.md`. The
specification's role in it is:

1. **Specification Agent** — creates or validates the document. It may only
   write `docs/specifications/**` and `docs/agent-runs/**`. It must not
   implement behavior or invent requirements.
2. **Test Agent** — translates each acceptance criterion into executable tests
   and establishes a valid RED state. It must not modify production code.
3. **Implementation Agent** — writes the minimum production code that satisfies
   the specification and makes the tests pass. It must not add unspecified
   behavior.
4. **Refactor Agent** — improves structure without changing observable
   behavior. "No refactor required" is valid.
5. **Architecture Agent** — checks the layer rules and executes the
   architecture tests.
6. **Validation Agent** — runs the quality gate and reports the evidence,
   including passed, failed and skipped counts.

No agent may override `AGENTS.md`, weaken a test, or change the specification
silently. If implementation reveals that a requirement is wrong or impossible,
the workflow stops and the user decides.

---

## 7. Interaction with the architecture

The specification decides **what** is required. The architecture decides
**where** it may live and **which dependencies are legal**.

```text
Specification
     │  behavior
     ▼
Architecture
     │  layer and dependency rules
     ▼
Tests
     │  executable acceptance criteria
     ▼
Implementation
```

The layer rules are executable in
`tests/{{PROJECT_NAME}}.Architecture.Tests/`. A feature that would violate
them is either specified incorrectly or needs an explicit architectural
decision from the user; it is never solved by weakening the test.

Persistence is not automatically part of a Domain feature. If the
specification requires persistence, say so and name the observable behavior
that must survive a process restart. The implementation decides the mechanism
within the architecture.

---

## 8. Validating a specification

Before implementation begins, confirm:

- [ ] The feature has a unique sequential identifier.
- [ ] The file name follows `<feature-id>-<short-name>.md`.
- [ ] The status is `Draft` or `Approved`.
- [ ] The Objective describes a business capability and why it exists.
- [ ] The Context names actors, existing behavior and dependencies.
- [ ] Dependencies are listed and their state is known.
- [ ] Every invariant has a `BR-` identifier.
- [ ] Every meaningful rule has at least one `AC-` criterion.
- [ ] Every criterion is observable and deterministic.
- [ ] Edge cases, refusals and unchanged state are explicit.
- [ ] The architectural layer and forbidden concerns are stated.
- [ ] Technical requirements are real constraints, not a design prescription.
- [ ] Out-of-scope behavior is explicit.
- [ ] The TDD statement is present.
- [ ] Open questions are resolved or the specification is marked blocked.
- [ ] The traceability table maps rules to criteria and tests.

If any item is missing, the specification is not ready.

---

## 9. Amending a specification

Specifications change when the product changes. Amend them deliberately:

1. Add an `## Amendments` section at the end (or append to the existing one).
2. Record the date, the reason and the rule or criterion being changed.
3. Keep the old identifier if the meaning is extended; add a new identifier
   when the behavior is new.
4. Mark superseded text explicitly instead of deleting the history without a
   trace.
5. Update the traceability table and the tests.
6. Re-run the quality gate.

Example:

```text
## Amendments

### 2026-01-15 — BR-003 narrowed
The original rule forbade any update after leaving. The product now requires
that historical records remain readable but immutable. AC-004 was added.

Superseded: "Leaving has no effect on historical records."
```

Never rewrite a specification silently to match code that was already
written. That turns the source of truth into a description of the
implementation and removes the only check on scope.

---

## 10. Complete worked example

The following is illustrative. Replace it with real product behavior when the
first feature is specified; do not implement this example.

```markdown
# Leave a workspace

Status: Draft

## Objective
A workspace member can leave a workspace without deleting the workspace or
the member's historical records.

## Context
Workspaces have members with roles. The last owner is responsible for the
workspace, so ownership must be transferred before that owner can leave.
Existing memberships are read by the workspace administration feature.

## Dependencies
- Feature 001 — workspace ownership and membership already exist.
- No external service is required.

## Business Rules
BR-001 A member who is the last owner cannot leave the workspace.
BR-002 A member who has already left cannot leave again.
BR-003 Leaving does not delete historical records.
BR-004 A successful leave is idempotent for the same member.

## Acceptance Criteria

### AC-001 — The last owner cannot leave
Given a workspace with exactly one owner
When the owner requests to leave
Then the request is refused with `LastOwnerCannotLeave`
And the membership is unchanged

### AC-002 — A regular member can leave
Given a workspace with an owner and a regular member
When the regular member requests to leave
Then the membership is marked as left
And the workspace still exists

### AC-003 — Leaving twice is idempotent
Given a member who has already left
When that member requests to leave again
Then the request succeeds without creating another history record

### AC-004 — Historical records remain readable
Given a member who has left
When an administrator reads the workspace history
Then the member's past activity is still visible

## Constraints
This behavior belongs to the Domain layer for the invariant, with an
Application command for orchestration.

Domain must not depend on Application, Infrastructure, API, ASP.NET Core,
Entity Framework Core, or HTTP.

No HTTP endpoint is required by this feature.

## Technical Requirements
- The "last owner" check and the membership change must be one atomic
  operation; a concurrent leave must not leave the workspace ownerless.
- The membership change must be persisted before the command reports success.

## Out of Scope
- transferring ownership
- invitations
- notifications
- deleting a workspace
- restoring a member who has left

## TDD
The first implementation stage is test creation.

Tests must initially fail because the required behavior does not yet exist.
Production implementation must not begin before RED has been established.

## Open Questions
None.
```

---

## 11. Anti-patterns

| Anti-pattern | Why it is wrong |
| --- | --- |
| A specification that names classes, methods or repositories | Prescribes implementation and removes design judgment. |
| Acceptance criteria that assert a private method was called | Tests implementation, not behavior. |
| A business rule hidden inside a criterion | The invariant is not stated explicitly and cannot be reviewed. |
| "Handle errors appropriately" | Not deterministic and not testable. |
| A feature with no out-of-scope list | Invites scope expansion by autonomous agents. |
| A status changed to `Implemented` before approval and close | Turns an unverified claim into a source of truth. |
| A silent amendment made to match code | Removes the check that the code satisfies the requirement. |
| Several unrelated capabilities in one file | Makes one branch, one review and one rollback impossible. |

---

## 12. Final checklist

Before handing a specification to the workflow:

```text
[ ] One feature, one file, one sequential identifier
[ ] Objective states the capability and the reason
[ ] Context and dependencies are based on an inspection of the repository
[ ] Business rules have BR- identifiers
[ ] Acceptance criteria have AC- identifiers and are Given/When/Then
[ ] Edge cases and refusals are explicit
[ ] The architectural layer and forbidden concerns are stated
[ ] Technical requirements are real constraints
[ ] Out of scope is explicit
[ ] The TDD statement is present
[ ] Open questions are resolved
[ ] The traceability table is complete
```

A specification that passes this checklist is precise enough for another agent
to write tests without making business decisions on the user's behalf.
