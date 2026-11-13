# Matchly Agent Contract

## 1. Project

Matchly is an experimental web application used to study:

- Agentic Programming
- Test-Driven Development
- Test-Driven Prompting
- Clean Code
- SOLID
- Clean Architecture

The project is developed incrementally through small, independently
validated features.

---

# 2. Core Development Principles

The following principles are mandatory:

1. Correctness over speed.
2. Simplicity over unnecessary abstraction.
3. Explicit behavior over implicit behavior.
4. Tests are executable specifications.
5. Production code must satisfy the tests.
6. Architectural rules must be automatically verifiable.
7. Do not implement functionality that is not required.
8. Do not modify unrelated code.
9. Do not weaken tests to make an implementation pass.
10. Do not declare success without executing validation.

---

# 3. Clean Architecture

Matchly follows Clean Architecture principles.

The architecture is:

```text
API
 ↓
Application
 ↓
Domain

Application
 ↓
Security

Infrastructure
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Security

```

## Domain

Domain contains business rules and business concepts.

Domain must NOT depend on:

* Application
* Infrastructure
* API
* ASP.NET Core
* Entity Framework Core
* database providers (PostgreSQL, SQL Server)
* HTTP
* external services

Domain code must remain framework independent.

## Application

Application contains:

* Use Cases
* Commands
* Queries
* Application Services
* DTOs
* Interfaces required by use cases

Application may depend on:

* Domain

Application must NOT depend on:

* Infrastructure implementations
* API
* ASP.NET Core
* Entity Framework Core

Application defines abstractions required by the use cases.

## Security

Security contains security abstractions only: interfaces for authentication,
authorization and principal concepts. No implementations and no other
references.

Security may depend on:

* Nothing (it references no other project)

Application and Infrastructure may depend on:

* Security

Domain must NOT depend on Security.

## Infrastructure

Infrastructure contains implementation details.

Examples:

* Entity Framework Core
* database providers (e.g. PostgreSQL, SQL Server)
* Repository implementations
* External services
* Persistence
* File systems

Infrastructure may depend on:

* Application
* Domain

Infrastructure implements abstractions defined by Application.

Infrastructure must not contain business rules that belong to Domain.

## API

API contains:

* HTTP endpoints
* Request models
* Response models
* Dependency injection composition
* Authentication configuration
* HTTP-specific concerns

API may depend on:

* Application
* Infrastructure (composition root: dependency injection wiring only)

API must not contain business rules.

4. Dependency Rules

The following dependencies are forbidden:

```
Domain → Application
Domain → Infrastructure
Domain → API
Domain → Security

Security → Domain
Security → Application
Security → Infrastructure
Security → API

Application → Infrastructure
Application → API

Domain → ASP.NET Core
Domain → Entity Framework Core
Domain → database providers (PostgreSQL, SQL Server)

```

Architecture tests must detect violations of these rules.

Never bypass an architecture test by weakening or removing the test.

# 5. Clean Code

Follow Clean Code principles inspired by Robert C. Martin.

## Naming

Names must communicate intent.

Prefer:

```
CreateUser
LikeProfile
CreateMatch
FindProfile
```

Avoid:

```
DoIt
Process
Manager
Helper
Handler2
Data
Info

```

unless the name is genuinely appropriate.


## Functions

Functions should:

* have one clear responsibility
* be small
* have meaningful names
* avoid unnecessary parameters
* avoid hidden side effects

Avoid large methods containing multiple responsibilities.

## Classes

Classes should have a focused responsibility.

Avoid:

* God classes
* large service classes
* classes with unrelated responsibilities
* unnecessary inheritance

## Abstractions

Do not create abstractions speculatively.

Do not create:

```
IRepository<T>
BaseService<T>
BaseHandler<T>
GenericManager<T>

```

without a concrete requirement.
Prefer the simplest design that satisfies the current requirement.

# 6. SOLID

Apply SOLID principles when they improve the design.

## Single Responsibility

A class should have one clear reason to change.

## Open/Closed

Prefer designs that can evolve without modifying stable business rules.

Do not introduce abstractions solely to satisfy this principle.

## Liskov Substitution

Implementations must honor the contract of their abstractions.

## Interface Segregation

Prefer focused interfaces over large interfaces.

## Dependency Inversion

High-level application logic must depend on abstractions rather than infrastructure implementations.


# 7. Test-Driven Development

Development follows TDD.

The default cycle is:

```
RED
 ↓
GREEN
 ↓
REFACTOR
```

## RED

Create a test describing required behavior.

Run the test.

The test should fail because the required behavior does not exist.

## GREEN

Implement the minimum production code necessary to make the test pass.

Do not implement speculative functionality.

## REFACTOR

Improve the implementation while preserving behavior.

After refactoring, tests must remain green.

# 8. Test-Driven Prompting

Features are developed from explicit requirements.

The development flow is:

```
Requirement
 ↓
Test Specification
 ↓
Tests
 ↓
Implementation
 ↓
Validation
```

The requirement is the source of truth.

Tests represent executable acceptance criteria.

Implementation must satisfy the tests and the requirement.

# 9. Tests Are Specifications
Tests must verify behavior.

Prefer:

```
User_cannot_like_themselves
Duplicate_like_is_rejected
Reciprocal_likes_create_match
```

Avoid tests that only verify implementation details.

Do not write tests such as:

```
Repository_method_X_was_called

```

unless the interaction itself is part of the required behavior.

# 10. Test Integrity

Tests must not be weakened to make production code pass.

Never:

* remove an assertion because it fails
* make an assertion less strict
* skip a failing test
* delete a test without a requirement change
* change expected behavior merely to match the implementation

If production code fails a valid test:

```
Fix production code.
```


If the requirement changed:
```
Update the requirement.
Update the affected tests.
Then update production code.
```

# 11. Validation

Never declare a feature complete based only on code inspection.

At minimum, validate:

```
dotnet build
dotnet test
```

When applicable also run:

```
dotnet format --verify-no-changes
```

Architecture tests must pass.

A feature is complete only when validation succeeds.


# 12. Scope Control

Work on one feature at a time.

Do not:

* refactor unrelated code
* rename unrelated classes
* modify unrelated tests
* introduce unrelated dependencies
* implement future requirements

If a discovered problem is outside the current feature:

1. Document it.
2. Do not silently expand the scope.
3. Continue with the current requirement if possible


# 13. Database

The application uses the database selected at generation time
(PostgreSQL or SQL Server).

Persistence belongs to Infrastructure.

Domain entities must not depend on Entity Framework Core attributes.

Avoid leaking persistence concerns into the Domain model.

The host must not create or migrate the schema at start-up. The schema is
created and changed only by committed EF Core migrations
(`dotnet ef migrations add ...`). The design-time factory reads the
connection string from the `<PROJECT_NAME>_CONNECTION_STRING` environment
variable; no credential is stored in the repository. `EnsureCreated` is a
test-only pattern.

The connection string written to `appsettings.json` carries no credentials.
Override it at run time with the `ConnectionStrings__Default` environment
variable (or user secrets) whenever a password is required.

# 14. Error Handling

Errors must represent meaningful business or application conditions.

Do not use exceptions as normal control flow.

Do not catch exceptions unless the code can meaningfully handle them.

Do not silently swallow exceptions.

# 15. Logging

Logging belongs to infrastructure/application boundaries.

Do not add logging everywhere by default.

Log meaningful operational information.

Never log:

* passwords
* authentication tokens
* secrets
* sensitive personal data


16. Security

Security code lives in the `Security` project only: abstractions for
authentication, authorization and principals. No secrets, credentials or
environment-specific values belong in it. Concrete authentication schemes
belong to Infrastructure (or the host) and plug in through those
abstractions.

Never hardcode:

* passwords
* API keys
* database credentials
* tokens
* secrets

Do not commit secrets to Git.

Validate external input at application boundaries.

# 17. Dependencies

Do not add a NuGet package unless it provides concrete value for the current requirement.

Before adding a dependency:

1. Determine whether the framework already provides the functionality.
2. Determine whether the requirement genuinely needs the dependency.
3. Keep the dependency limited to the appropriate layer.

# 18. Git Discipline

Changes must be focused.

Do not modify files unrelated to the current feature.

Do not rewrite Git history unless explicitly requested.

Do not commit generated artifacts.

Commit messages should describe the change.

Examples:

```
feat: add profile matching
test: add reciprocal like tests
refactor: simplify match creation
fix: prevent duplicate likes
```

# 19. Agent Behavior

The agent must reason about the existing code before modifying it.

Before implementing:

1. Read the requirement.
2. Inspect the relevant code.
3. Identify affected layers.
4. Identify existing tests.
5. Identify architectural constraints.

Do not immediately start writing code.

20. Completion Criteria

Never report:

```
Done
```

only because implementation was written.

A feature is complete only when:
```
Requirement satisfied
        AND
Tests pass
        AND
Build passes
        AND
Architecture rules pass
        AND
No unrelated changes were introduced
```

# 21. When Tests Fail

When tests fail:

1. Read the failure.
2. Identify the failing behavior.
3. Determine whether the problem is in production code.
4. Fix the production code.
5. Run the tests again.

Do not modify tests simply to make them pass.

# 22. When Architecture Tests Fail

Architecture violations are blocking failures.

Do not bypass them.

Do not:

* remove the architecture test
* weaken the rule
* add exclusions without justification
* move code to another namespace to hide the violation

Fix the dependency direction.

# 23. Implementation Philosophy

Prefer:
```
Simple
Explicit
Testable
Small
Focused
Maintainable

```
Avoid:
```
Clever
Generic
Speculative
Over-engineered
Highly coupled
```

The simplest correct implementation is preferred.


# 24. Agent Output

When reporting work, provide:

1. What was changed.
2. What tests were added or modified.
3. What validation was executed.
4. Validation results.
5. Any remaining issues.

Never claim that a command passed if it was not actually executed.

# 25. Identifier Rule (UUIDv7)

Every new entity identifier is generated with
`<Project>.Domain.EntityId.New()` (which calls `Guid.CreateVersion7()`),
never with `Guid.NewGuid()`. Identifiers carry a millisecond timestamp in
their leading bits, so they sort by creation time.

Non-entity values (a JWT `jti`, a test fixture id) are exempt. New entities
added later must follow the same rule.

# 26. Two-Tier Persistence Testing

Persistence is validated on two tiers:

- **Default tier** — an in-memory SQLite database, always runs, no external
  service required. Covers mapping, relationships, reads, unit-of-work
  commit and failed-commit atomicity.
- **Gated tier** — the configured provider reached through the connection
  string, proving the migration-created schema and provider-specific
  behavior. Gated tests carry `[DatabaseFact]` / `[DatabaseTheory]` and
  **skip** unless `<PROJECT_NAME>_CONNECTION_STRING` is set.

A skipped test is not a passing test. When a feature touches the schema, a
migration, the provider configuration or provider-specific behavior, a
green run with skips is not validation: run with the environment variable
set and require **zero skips**. Report passed/failed/skipped counts in
every validation claim.

# 27. Feature Close Protocol

A feature is closed only after the user explicitly approves it and says
"close". Until then git is read-only for the agent: no commit, stage,
merge, rebase, reset, stash, push, tag or branch deletion, and the
specification must not be marked `Implemented`.

Once approval plus "close" is given, the agent executes the close sequence
in `docs/workflows/tdp-feature-workflow.md` §14 without re-asking: verify
the tree, re-run validation on green, commit outstanding work in logical
groups, `git merge --no-ff` into `develop`, verify on `develop`, delete the
feature branch with `git branch -d`, report the outcome and stop.

`develop -> main` is a release, not a feature close.

# 28. Known Proof Gaps

None recorded at bootstrap. When a validation gap is accepted deliberately
(a tier that cannot run in the current environment, an assertion that is
weaker than intended), record it here with the feature id and the reason.
Delete the entry when the gap closes.


