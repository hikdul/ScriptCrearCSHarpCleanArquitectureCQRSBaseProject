# Repository and Unit of Work

## Repository Pattern

### Definition

The Repository Pattern abstracts persistence access behind repositories.

Repositories are defined according to concrete Domain entities when
repository access is required.

For example:

```text
IUserRepository
```

and its Infrastructure implementation:

```text
UserRepository
```

### Rules

* Repositories must not be generic by default.
* Do not introduce `IRepository<T>`, `Repository<T>` or `BaseRepository<T>`
  unless explicitly required by a future specification.
* The Application layer defines the repository abstraction.
* Infrastructure implements the repository.
* Repositories must not contain business rules that belong to Domain.

## Unit of Work

### Definition

The Unit of Work pattern coordinates persistence changes that belong to a
single application operation.

The Unit of Work abstraction belongs to the Application layer
(`Application.Abstractions.IUnitOfWork`, exposing `CommitAsync`).
Infrastructure provides its implementation (`Infrastructure.UnitOfWork`),
which commits through the scoped `MatchlyDbContext`, and registers it as
scoped via `AddInfrastructure(...)`.

### Rules

* The Unit of Work must coordinate persistence operations that belong to a
  single application operation.
* The Unit of Work must not contain business rules.
* The Application layer must not depend directly on `MatchlyDbContext`.
* The Infrastructure implementation may use `MatchlyDbContext` to implement
  Unit of Work behavior.
* Do not introduce a Unit of Work abstraction if it is not required by the
  existing persistence design.
* When persistence is introduced, the Unit of Work must be explicit and
  testable.

## Preferred Relationship

```text
Application
    │
    ├── IUserRepository
    │
    └── IUnitOfWork
             ▲
             │
Infrastructure
    │
    ├── UserRepository
    │
    ├── UnitOfWork
    │
    └── MatchlyDbContext
```
