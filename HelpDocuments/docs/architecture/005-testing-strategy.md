# Testing Strategy

## Definition

The testing strategy defines how Matchly validates behavior across the
application.

The project distinguishes between:

```text
Unit tests
Integration tests
```

Unit tests validate a single layer or unit of behavior in isolation.

Integration tests validate interactions between multiple application layers.

## Persistence Testing

Infrastructure persistence behavior must be tested independently from
Domain and Application unit tests.

The initial testing strategy may use:

```text
Microsoft.EntityFrameworkCore.InMemory
```

for fast persistence-oriented tests where relational database behavior is
not the subject of the test.

## Rules

* Tests must not rely on InMemory behavior when validating
  PostgreSQL-specific behavior.
* When PostgreSQL-specific behavior becomes important, integration tests
  should use a real PostgreSQL test database or a disposable PostgreSQL
  environment.
* The testing strategy must not weaken production behavior merely to make
  InMemory tests pass.

## Tests Are Specifications

Tests verify behavior, not implementation details.

Prefer:

```text
User_cannot_like_themselves
Duplicate_like_is_rejected
Reciprocal_likes_create_match
```

Tests must not be weakened to make production code pass.

## Validation

A feature is complete only when the complete validation succeeds:

```text
dotnet build
dotnet test
```

Architecture tests must also pass.
