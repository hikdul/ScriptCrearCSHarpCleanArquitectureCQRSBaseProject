# Matchly Architecture

## Overview

Matchly follows Clean Architecture principles inspired by
Robert C. Martin.

The system is divided into four main layers:

- Domain
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

Infrastructure
 ↓
Application
 ↓
Domain

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
* Infrastructure
* API
* PostgreSQL
* External services

## Application

The Application layer contains:

* Use Cases
* Commands
* Queries
* Application Services
* Interfaces required by use cases
* DTOs

Application may depend on Domain.

Application must not depend on Infrastructure implementations.

## Infrastructure

Infrastructure contains implementation details:

* Entity Framework Core
* PostgreSQL
* Repositories
* External services
* Persistence

Infrastructure depends on Application and Domain.

## API

API contains:

* HTTP endpoints
* Request/response models
* Dependency injection composition
* Authentication configuration

API depends on Application.

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
4. Domain cannot depend on external frameworks.
5. Application cannot depend on Infrastructure.
6. Application cannot depend on API.
7. Infrastructure can depend on Application.
8. API can depend on Application.
9. API must not contain business rules.
10. Infrastructure must not contain business rules.


## Goal

Architecture violations must be detected automatically through tests.
