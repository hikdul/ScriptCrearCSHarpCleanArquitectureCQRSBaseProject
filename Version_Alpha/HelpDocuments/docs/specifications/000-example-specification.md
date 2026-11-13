
> [!WARNING]
> this file is use only for show to a humar the mode to creating a spec. for the agents only ignore

# Example Specification

This file shows how a feature specification must be written for this project.
Use it as a structural reference. Do not modify acceptance criteria or business
rules without understanding the TDP workflow.

---

# Feature: \<Feature Name\>

**ID:** 000
**Status:** Example
**Layer:** Domain
**Type:** Business Behavior

---

## 1. Objective

Describe what behavior is introduced and why.

Focus on the business capability, not the implementation.

---

## 2. Context

Where this feature fits in the existing system.

What it depends on and what it does not depend on.

Be explicit about the boundary: what is already in place and what is NOT
part of this feature.

---

## 3. Business Rules

Each rule must be independently testable and implementation-independent.

Number every rule so acceptance criteria can reference them.

### BR-001 — \<Rule title\>

\<Clear description of the invariant that must always hold.\>

### BR-002 — \<Rule title\>

\<Clear description of the invariant that must always hold.\>

### BR-003 — \<Rule title\>

\<When the rule involves an error condition, say so explicitly.\>

Attempt to violate this rule must result in a domain error.

### BR-004 — \<Rule title\>

\<After a successful operation, what must be observable.\>

---

## 4. Acceptance Criteria

Every business rule must have at least one acceptance criterion.

Use Given/When/Then format.

### AC-001 — \<Happy path title\>

**Given** \<initial state\>

**When** \<action\>

**Then** \<observable result\>

---

### AC-002 — \<Error case title\>

**Given** \<initial state\>

**When** \<invalid action\>

**Then** the operation is rejected with a domain error.

---

### AC-003 — \<Edge case title\>

**Given** \<state that already exists\>

**When** \<repeated or conflicting action\>

**Then** the operation is rejected with a domain error.

---

## 5. Constraints

The implementation must:

* Keep the business behavior in the correct architectural layer.
* Keep the Domain layer independent from infrastructure frameworks.
* Not introduce persistence concerns.
* Not introduce HTTP concerns.
* Not introduce authentication concerns.
* Not implement functionality outside this specification.
* Follow the project rules defined in `AGENTS.md`.
* Follow the TDP workflow defined in `docs/workflows/tdp-feature-workflow.md`.

If the feature spans multiple layers, list each layer and what it must contain.

If the feature is Domain-only, state that explicitly.

---

## 6. Out of Scope

List behavior that is explicitly excluded. This prevents scope expansion.

* \<Excluded behavior 1\>
* \<Excluded behavior 2\>
* \<Excluded behavior 3\>

---

## 7. Expected Behavior

Describe what the Domain model should expose in natural language.

Do not prescribe the internal implementation. Leave the design decision to
the agent as long as all business rules and acceptance criteria are satisfied.

```text
\<Describes the observable behavior in plain terms.\>
```

---

## 8. Validation

The feature is complete only when:

1. All acceptance criteria are represented by automated tests.
2. The tests pass.
3. The complete solution builds successfully.
4. The complete test suite passes.
5. Architecture tests pass.
6. No unrelated files are modified.

---

## How to use this template

1. Copy this file and rename it to `\<NNN\>-\<short-name\>.md`
   (for example `006-block-profile.md`).
2. Replace every `\<placeholder\>` with real content.
3. Add or remove business rules and acceptance criteria as needed.
4. Keep the structure. Every section exists for a reason:
   - **Objective** keeps the feature focused.
   - **Business Rules** define invariants the agent must not violate.
   - **Acceptance Criteria** become executable tests in the RED phase.
   - **Constraints** prevent architecture violations.
   - **Out of Scope** prevents silent scope expansion.
   - **Validation** defines the definition of done.

### Quality checklist

Before finalizing a specification:

- [ ] Every business rule has at least one acceptance criterion.
- [ ] Acceptance criteria use Given/When/Then format.
- [ ] The layer constraint is explicit (Domain-only or cross-layer).
- [ ] Out of Scope lists realistic temptations, not obvious exclusions.
- [ ] No implementation details leak into business rules.
- [ ] No persistence, HTTP, or authentication assumptions unless the feature
      explicitly requires them.
