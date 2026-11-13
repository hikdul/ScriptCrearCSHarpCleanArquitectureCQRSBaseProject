# API Controllers

## Definition

API Controllers are the HTTP entry points of the application.

Matchly uses ASP.NET Core Controllers for HTTP APIs.

Do not use Minimal APIs for application endpoints unless a future
specification explicitly requires them.

Controllers belong to:

```text
Matchly.Api
```

## Responsibilities

Controllers are responsible for:

* HTTP request handling
* HTTP response handling
* Model binding
* HTTP-specific validation
* Mapping HTTP requests to Application commands/queries
* Mapping Application results to HTTP responses

## Prohibitions

Controllers must not:

* contain business rules
* access repositories directly
* access `MatchlyDbContext`
* access Entity Framework Core directly
* implement application use cases

## Preferred Flow

```text
HTTP Request
    ↓
Controller
    ↓
Command / Query
    ↓
Handler
    ↓
Domain / Repository abstraction
    ↓
Infrastructure
```

## DTOs

API contracts must not expose Domain entities directly.

Requests and responses must use dedicated DTOs or API models.

For example:

```text
CreateUserRequest
UpdateUserRequest
UserResponse
```

Do not expose `User` directly from an API controller.

DTOs should contain only the data required by the API contract.

## Dependency Injection

Controllers must receive Application abstractions or handlers through
dependency injection.

Controllers must not construct infrastructure objects manually.
