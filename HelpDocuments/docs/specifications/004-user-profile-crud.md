
# Feature 005 — User Profile CRUD

short:
```
Implement feature 005: User Profile CRUD.

Requirements:
- User profile with basic appointment-system data.
- CQRS.
- Repository per aggregate/entity.
- Unit of Work.
- MatchlyDbContext.
- PostgreSQL in production.
- InMemory database for integration tests.
- REST Controllers.
- Clean Architecture.
- TDD.

```

**ID:** 005
**Status:** no Implement
**Type:** Cross-Layer Feature
**Scope:** Domain → Application → Infrastructure → API

---

## 1. Objective

Allow Matchly to create, retrieve, update and delete the basic profile information of a user.

This feature is the first complete vertical slice of the application.

Unlike previous features, the behavior crosses the following architectural layers:

```text
API
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Application
 ↓
Domain
```

The implementation must preserve the dependency rules defined in `AGENTS.md`.

---

## 2. Business Context

Matchly requires a basic user profile before users can participate in the application.

A profile contains the minimum information required to identify and describe a user.

The current feature does not implement authentication, authorization, matching discovery, messaging or recommendations.

---

# 3. Profile Data

A user profile must contain:

* `Id`
* `FirstName`
* `LastName`
* `BirthDate`
* `Bio`

The `Id` uniquely identifies the user.

The application must not expose persistence-specific identifiers or implementation details beyond the domain identifier.

---

# 4. Domain Rules

## BR-001 — User must have an identifier

Every user must have a unique identifier.

The identifier must be generated when a new user is created unless the existing architecture provides another explicit mechanism.

---

## BR-002 — First name is required

A user cannot be created without a first name.

The first name must not be empty or whitespace.

---

## BR-003 — Last name is required

A user cannot be created without a last name.

The last name must not be empty or whitespace.

---

## BR-004 — Birth date is required

A user must have a birth date.

---

## BR-005 — User must be an adult

A user must be at least 18 years old.

The age calculation must be based on the current date.

---

## BR-006 — Bio is optional

A user may have an empty bio.

---

## BR-007 — Profile information can be updated

The user may update:

* FirstName
* LastName
* BirthDate
* Bio

The same domain validation rules must apply during updates.

---

# 5. Application Behavior

The Application layer must expose use cases for:

```text
Create User
Get User
Update User
Delete User
```

The Application layer must not depend on Infrastructure or API.

Application use cases must operate through abstractions where persistence or external behavior is required.

---

# 6. Create User

Given valid profile information:

```text
FirstName
LastName
BirthDate
Bio
```

When the Create User use case executes:

Then:

1. A new User is created.
2. The domain rules are validated.
3. The user is persisted.
4. The created user can subsequently be retrieved.
5. The operation returns the created user's identifier and profile information.

Invalid domain data must be rejected before persistence.

---

# 7. Get User

Given an existing user identifier:

When the Get User use case executes:

Then the corresponding profile is returned.

If the user does not exist, the application must return an appropriate application-level result representing the missing resource.

---

# 8. Update User

Given an existing user:

When valid profile information is submitted:

Then the user's profile information is updated.

The updated information must be persisted.

The domain rules must be applied to the new values.

An update must not create another user.

---

# 9. Delete User

Given an existing user:

When the Delete User use case executes:

Then the user is removed from persistence.

Subsequent retrieval of the user must indicate that the user no longer exists.

---

# 10. API

The API must expose HTTP endpoints for the CRUD operations.

The exact routing and implementation mechanism is left to the agent as long as the API follows conventional REST semantics.

The API must support:

```text
POST   /users
GET    /users/{id}
PUT    /users/{id}
DELETE /users/{id}
```

The API must:

* Validate request input at the application boundary.
* Delegate business behavior to Application.
* Not contain domain business rules.
* Not access Infrastructure directly.
* Return appropriate HTTP status codes.
* Return DTOs rather than persistence entities.

---

# 11. Persistence

Infrastructure must provide persistence for User.

The application uses PostgreSQL.

Persistence must be implemented through the existing Infrastructure architecture.

The implementation must:

* Persist all required profile fields.
* Preserve the user identifier.
* Allow create, read, update and delete operations.
* Use Entity Framework Core only inside Infrastructure.
* Not introduce EF Core dependencies into Domain.
* Not introduce EF Core dependencies into Application.

A database migration must be created when required by the existing project configuration.

---

# 12. Application Abstractions

If persistence abstractions are required, they must be defined in the appropriate architectural layer.

Do not introduce generic abstractions such as:

```text
IRepository<T>
BaseRepository<T>
GenericService<T>
GenericManager<T>
```

unless a concrete requirement requires them.

Prefer the smallest abstraction that satisfies the CRUD use cases.

---

# 13. Architecture Requirements

The following dependency rules remain mandatory:

```text
Domain
  ↓
must depend on nothing external

Application
  ↓
Domain

Infrastructure
  ↓
Application
  ↓
Domain

API
  ↓
Application
```

Forbidden:

```text
Domain → Application
Domain → Infrastructure
Domain → API

Application → Infrastructure
Application → API

Domain → EF Core
Domain → PostgreSQL
Domain → ASP.NET Core
```

Architecture tests must verify these rules.

---

# 14. Test Requirements

The feature must follow TDD.

The implementation must not begin before RED tests exist for the relevant behavior.

The feature must be tested at multiple levels.

## Domain tests

Domain tests must verify:

* valid user creation
* required first name
* required last name
* required birth date
* adult validation
* optional bio
* valid profile update
* invalid profile update

---

## Application tests

Application tests must verify:

* create user use case
* get user use case
* update user use case
* delete user use case
* missing user behavior
* persistence abstraction interaction where interaction is part of the application contract

Application tests must not depend on PostgreSQL.

---

## Infrastructure tests

Infrastructure tests must verify:

* user persistence
* user retrieval
* user update
* user deletion
* mapping between Domain and persistence model

Tests must use the project's existing Infrastructure testing strategy.

---

## API tests

API tests must verify:

* POST creates a user
* GET returns a user
* PUT updates a user
* DELETE removes a user
* invalid requests are rejected
* missing users return the expected HTTP response
* API responses do not expose persistence implementation details

---

# 15. Test Pyramid

The feature should follow approximately:

```text
             API
          ┌───────┐
          │ Tests │
          └───────┘

        Application
      ┌─────────────┐
      │    Tests    │
      └─────────────┘

        Infrastructure
     ┌────────────────┐
     │     Tests      │
     └────────────────┘

            Domain
   ┌─────────────────────┐
   │     Many tests      │
   └─────────────────────┘
```

Most business behavior should remain covered by fast Domain tests.

---

# 16. TDD Workflow

The feature must progress through:

```text
Specification
     ↓
RED — Domain
     ↓
GREEN — Domain
     ↓
REFACTOR — Domain
     ↓
RED — Application
     ↓
GREEN — Application
     ↓
REFACTOR — Application
     ↓
RED — Infrastructure
     ↓
GREEN — Infrastructure
     ↓
REFACTOR — Infrastructure
     ↓
RED — API
     ↓
GREEN — API
     ↓
REFACTOR — API
     ↓
Architecture Validation
     ↓
Full Validation
```

An agent must not skip directly to GREEN.

---

# 17. GitFlow

This feature must be developed using GitFlow.

The feature branch must originate from:

```text
develop
```

The expected branch is:

```text
feature/005-user-profile-crud
```

The feature must not be developed directly on:

```text
main
```

or:

```text
develop
```

When the feature is complete:

```text
feature/005-user-profile-crud
        ↓
      develop
```

A release to `main` is outside this feature and must be explicitly requested.

---

# 18. Agent Ownership

The feature must be processed by specialized agents.

### Specification / Orchestrator

Responsible for:

* reading this specification
* creating the execution plan
* determining affected layers
* delegating work
* tracking state
* enforcing TDD order

### Domain Agent

Responsible for:

* Domain RED
* Domain GREEN
* Domain REFACTOR

### Implementation Agent

Responsible for:

* Application
* Infrastructure
* API implementation
* following the existing Domain contract

### Refactor Agent

Responsible for:

* simplifying implementation
* removing unnecessary abstractions
* preserving behavior

### Architecture Agent

Responsible for:

* dependency verification
* architecture tests
* detecting forbidden dependencies

### Validation Agent

Responsible for:

```text
dotnet build
dotnet test
dotnet format --verify-no-changes
```

when applicable.

### Release Agent

Responsible for:

* verifying feature completion
* GitFlow state
* release readiness
* preparing the feature for merge into `develop`

The Release Agent must not merge to `main` unless explicitly instructed.

---

# 19. Scope Restrictions

This feature must NOT implement:

* authentication
* authorization
* profile discovery
* matching
* blocking
* messaging
* notifications
* recommendations
* image upload
* social login
* payments
* subscriptions
* frontend UI

Do not introduce functionality that is not required by this specification.

---

# 20. Definition of Done

Feature 005 is complete only when:

```text
Specification satisfied
        AND
Domain tests pass
        AND
Application tests pass
        AND
Infrastructure tests pass
        AND
API tests pass
        AND
Architecture tests pass
        AND
dotnet build passes
        AND
dotnet test passes
        AND
format validation passes when applicable
        AND
No unrelated files were modified
        AND
Feature branch follows GitFlow
```

The feature must remain on:

```text
feature/005-user-profile-crud
```

until the user explicitly authorizes merging it into `develop`.

A release to `main` is a separate operation.
