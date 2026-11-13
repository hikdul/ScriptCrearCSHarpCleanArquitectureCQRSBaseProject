# Matchly Architecture

## Overview

Matchly follows Clean Architecture principles inspired by
Robert C. Martin.

The system is divided into five layers:

- Domain
- Security
- Application
- Infrastructure
- API

## Dependency Rule

Dependencies must point toward the Domain.

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

The Domain layer contains:

* Entities
* Value Objects
* Domain Rules
* Domain Services
* Domain Exceptions

 The Domain layer must not depend on:

* ASP.NET Core
* Entity Framework Core
* database providers (PostgreSQL, SQL Server)
* Infrastructure
* API
* External services

## Security

The Security layer contains security abstractions only: interfaces for
authentication, authorization and principals. It references no other
project.

Application and Infrastructure may depend on Security.

Domain must not depend on Security.

## Application

The Application layer contains:

* Use Cases
* Commands
* Queries
* Application Services
* Interfaces required by use cases
* DTOs

Application may depend on Domain and Security.

Application must not depend on Infrastructure implementations.

## Infrastructure

Infrastructure contains implementation details:

* Entity Framework Core
* database providers (e.g. PostgreSQL, SQL Server)
* Repositories
* External services
* Persistence

Infrastructure depends on Application, Domain and Security.

## API

API contains:

* HTTP endpoints
* Request/response models
* Dependency injection composition
* Authentication configuration

API depends on Application and, as the composition root, Infrastructure
(for dependency injection wiring only).

## Dependency Inversion

Application defines abstractions required by the business use cases.

Infrastructure implements those abstractions.

Example:
```
Application

ILikeRepository
      ▲
      │
      │ implementation
      │
Infrastructure

LikeRepository

```

## Architectural Rules
1. Domain cannot depend on Application.
2. Domain cannot depend on Infrastructure.
3. Domain cannot depend on API.
4. Domain cannot depend on Security.
5. Domain cannot depend on external frameworks.
6. Security cannot depend on any other project.
7. Application cannot depend on Infrastructure.
8. Application cannot depend on API.
9. Infrastructure can depend on Application.
10. API can depend on Application.
11. API must not contain business rules.
12. Infrastructure must not contain business rules.


## Goal

Architecture violations must be detected automatically through tests.
