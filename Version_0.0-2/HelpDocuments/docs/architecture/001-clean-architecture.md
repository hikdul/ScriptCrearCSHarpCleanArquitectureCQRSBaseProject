# Clean Architecture

## Definition

Clean Architecture is an architectural style that separates software into
layers with strict, unidirectional dependency rules.

Each layer contains a specific category of responsibility. Dependencies
point inward toward the Domain and never outward.

The goal is to keep business rules independent from frameworks, databases,
HTTP and external services, so they can be tested and evolved without
touching infrastructure.

## Layers

### Domain

The Domain contains business rules and business concepts.

The Domain must NOT depend on:

* Application
* Infrastructure
* API
* ASP.NET Core
* Entity Framework Core
* database providers (PostgreSQL, SQL Server)
* HTTP
* external services

Domain code must remain framework independent.

### Application

The Application contains:

* Use Cases
* Commands
* Queries
* Application Services
* DTOs
* Interfaces required by use cases

The Application may depend on:

* Domain
* Security

The Application must NOT depend on:

* Infrastructure implementations
* API
* ASP.NET Core
* Entity Framework Core

The Application defines the abstractions required by the use cases.

### Security

The Security layer contains security abstractions only: interfaces for
authentication, authorization and principals. It references no other
project. Application and Infrastructure may depend on it; Domain must not.

### Infrastructure

The Infrastructure contains implementation details, for example:

* Entity Framework Core
* database providers (e.g. PostgreSQL, SQL Server)
* Repository implementations
* External services
* Persistence
* File systems

The Infrastructure may depend on:

* Application
* Domain
* Security

The Infrastructure implements the abstractions defined by Application.

The Infrastructure must not contain business rules that belong to Domain.

### API

The API contains:

* HTTP endpoints
* Request models
* Response models
* Dependency injection composition
* Authentication configuration
* HTTP-specific concerns

The API may depend on:

* Application
* Infrastructure (composition root: dependency injection wiring only)

The API must not contain business rules.

## Dependency Rules

The following dependencies are forbidden:

```text
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

## Verification

Architecture tests must detect violations of these rules.

Never bypass an architecture test by weakening or removing the test.
