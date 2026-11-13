# CQRS

## Definition

CQRS (Command Query Responsibility Segregation) is a pattern in which the
Application layer separates operations that modify application state from
operations that read application state.

Commands represent operations that modify application state.

Queries represent operations that read application state.

Commands and Queries must be separated.

## Commands

Examples:

```text
CreateUser
UpdateUser
DeleteUser
```

## Queries

Examples:

```text
GetUser
```

## Rules

* Commands must not be used as queries.
* Queries must not modify application state.
* Each use case should have a focused responsibility.
* Prefer explicit use cases over generic handlers or generic services.
* Do not introduce a generic CQRS framework unless explicitly required.
* The CQRS implementation must remain simple and consistent with the
  existing project.

## Command and Query Handlers

Each Command or Query should have a dedicated handler.

Examples:

```text
CreateUserCommand
CreateUserCommandHandler

UpdateUserCommand
UpdateUserCommandHandler

DeleteUserCommand
DeleteUserCommandHandler

GetUserQuery
GetUserQueryHandler
```

Handlers belong to the Application layer.

Handlers may depend on:

* Domain
* Application abstractions

Handlers must NOT depend directly on:

* Infrastructure implementations
* Entity Framework Core
* database providers (PostgreSQL, SQL Server)
* API
* ASP.NET Core

Handlers must not contain persistence implementation details.

## In-Process Mediator

The Application layer ships a minimal mediator (`SimpleMediator`) that
dispatches `IRequest<TResponse>` / `IRequest` messages to exactly one
`IRequestHandler<...>`.

Registration is automatic: the `AddApplication()` service-collection
extension scans the Application assembly for closed `IRequestHandler<,>`
and `IRequestHandler<>` implementations and registers them, plus
`IMediator` → `SimpleMediator`. A newly added handler works without
editing `Program.cs` or any manual registration list.

Dispatch requires exactly one handler per request. A missing or duplicate
registration throws `MediatorException` instead of silently resolving one
of several handlers. Handler failures surface with their original
exception type (compiled dispatch, no reflection wrappers).
