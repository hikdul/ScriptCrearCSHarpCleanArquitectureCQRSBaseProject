# TDP Feature Development Workflow

## Purpose

This workflow defines how Matchly features must be developed using Test-Driven Prompting (TDP), Test-Driven Development (TDD), Clean Code and Clean Architecture.

The workflow is mandatory for feature development.

---

# 1. Source of Truth

Every feature must begin with an explicit specification.

The specification is the primary source of truth.

A specification must define:

* Feature name
* Feature goal
* Business rules
* Acceptance criteria
* Constraints
* Expected behavior
* Out-of-scope behavior

The agent must not implement behavior that is not required by the specification.

---

# 2. Feature Analysis

Before changing code, the agent must:

1. Read the complete specification.
2. Inspect the existing project structure.
3. Identify the affected architectural layers.
4. Inspect existing production code related to the feature.
5. Inspect existing tests related to the feature.
6. Identify existing architectural constraints.
7. Determine the minimum change required.

The agent must not modify code before completing this analysis.

---

# 3. Acceptance Criteria

Every acceptance criterion must be represented by executable tests whenever technically possible.

Acceptance criteria should describe behavior rather than implementation details.

Prefer:

```text
A user cannot like their own profile.
```

over:

```text
User.Like must call validation method X.
```

---

# 4. Test Design

Before implementing production behavior, create or update the tests required by the acceptance criteria.

Tests must:

* Express observable behavior.
* Have meaningful names.
* Be deterministic.
* Be independent when possible.
* Avoid testing implementation details.
* Preserve existing test integrity.

The agent must not weaken existing tests to make the implementation pass.

---

# 5. RED Phase

Run the relevant tests before implementing the production behavior.

The expected result is failure caused by the missing behavior.

The agent must verify that the failure corresponds to the requirement.

An unexpected compilation or infrastructure failure does not constitute a valid RED phase.

The agent must fix unrelated test infrastructure problems before continuing.

The agent must not proceed to implementation if the intended test cannot be demonstrated to fail for the expected reason.

---

# 6. GREEN Phase

Implement the minimum production code necessary to satisfy the failing tests.

The implementation must:

* Satisfy the specification.
* Satisfy the tests.
* Preserve architectural boundaries.
* Follow Clean Code principles.
* Avoid speculative functionality.
* Avoid unnecessary abstractions.

Do not implement future requirements.

Do not refactor unrelated code.

After implementation, run the relevant tests.

The result must be GREEN.

---

# 7. REFACTOR Phase

Refactoring begins only after the tests are GREEN.

Refactoring may improve:

* Naming
* Structure
* Duplication
* Cohesion
* Coupling
* Readability
* Simplicity

Refactoring must not change externally observable behavior.

After every meaningful refactoring, run the relevant tests again.

The final refactored state must remain GREEN.

---

# 8. Quality Gate

After the feature implementation and refactoring are complete, execute:

```bash
dotnet build
dotnet test
```

When applicable:

```bash
dotnet format --verify-no-changes
```

Architecture tests must pass.

The feature cannot be considered complete if any required validation fails.

---

# 9. Retry Loop

If validation fails, the agent may retry the implementation cycle.

The maximum number of implementation attempts is three.

The attempt counter includes the initial implementation attempt.

```text
Attempt 1
    ↓
Implementation
    ↓
Validation
    ↓
FAIL
    ↓
Attempt 2
    ↓
Implementation
    ↓
Validation
    ↓
FAIL
    ↓
Attempt 3
    ↓
Implementation
    ↓
Validation
    ↓
FAIL
    ↓
STOP
```

The agent must never perform more than three implementation attempts for the same feature.

---

# 10. Failure Analysis

When validation fails, the agent must determine the category of failure before changing code.

Possible categories include:

* Production code failure
* Test failure
* Specification inconsistency
* Architecture violation
* Build failure
* Dependency failure
* Environment failure
* Unrelated existing failure

The agent must address the actual cause.

The agent must not modify tests merely to make them pass.

The agent must not weaken architectural rules.

The agent must not change the specification silently.

---

# 11. Retry Rules

On each retry:

1. Read the complete failure output.
2. Identify the root cause.
3. Determine whether the previous implementation was incorrect.
4. Make the smallest reasonable correction.
5. Run the relevant tests.
6. Run the complete validation again.

If the failure is caused by the specification itself, stop implementation and report the inconsistency.

If the failure is caused by the environment and cannot be resolved safely, stop and report it.

---

# 12. Completion

A feature is complete only when all of the following are true:

```text
Specification satisfied
        AND
Acceptance criteria satisfied
        AND
Tests pass
        AND
Build passes
        AND
Architecture tests pass
        AND
Clean Code principles are respected
        AND
No unrelated changes were introduced
```

Only then may the agent report the feature as complete.

---

# 13. Completion Report

The agent must report:

1. Feature implemented.
2. Specification used.
3. Tests created or modified.
4. Production code created or modified.
5. Refactoring performed.
6. Validation commands executed.
7. Validation results.
8. Number of attempts used.
9. Remaining issues, if any.

The agent must never claim successful validation without actually executing the validation commands.

