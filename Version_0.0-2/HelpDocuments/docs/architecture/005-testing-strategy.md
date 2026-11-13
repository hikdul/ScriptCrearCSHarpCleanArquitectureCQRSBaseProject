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

## Persistence Testing — Two Tiers

Persistence is validated on two tiers, and this is the single most
important thing to know when reading a test report:

| Tier | Database | Covers | Runs when |
| --- | --- | --- | --- |
| Default | in-memory SQLite | entity mapping, relationships, repository reads, unit-of-work commit, failed-commit atomicity, API composition, HTTP round trips | always — no service required |
| Gated | the configured provider (PostgreSQL or SQL Server) reached through `<PROJECT_NAME>_CONNECTION_STRING` | the migration-created schema, column types, provider-specific behavior | a matching database is reachable |

The default tier uses a shared in-memory SQLite helper
(`tests/<Project>.TestSupport/SqliteDatabase.cs`). It runs anywhere,
including a clean checkout. It does not prove that the configured
provider behaves the same way; that is what the gated tier is for.

Gated tests carry `[DatabaseFact]` or `[DatabaseTheory]` and **skip**
when the connection string environment variable is not set. A skipped test
is not a passing test: the gated tier is what proves the configured
provider and the migration-created schema. A green `dotnet test` that
reports skips has not verified those.

So, when a feature touches persistence:

* If it only changes provider-agnostic code, a green run with skips is
  sufficient.
* If it changes the schema, a migration, the provider configuration, or
  anything provider-specific, run the suite with
  `<PROJECT_NAME>_CONNECTION_STRING` set and confirm **zero tests are
  skipped**. Treat skips as a failure for those features.
* Always report the passed/failed/skipped counts. Do not describe a run
  with skips as fully validated.

## Rules

* Tests must not rely on InMemory-provider behavior when validating
  relational database semantics; use the SQLite default tier or the
  gated provider tier instead.
* Tests that depend on the host, the wire or a full pipeline are
  integration tests and must be identified as such.
* Schema is created and changed only by committed EF Core migrations.
  `EnsureCreated` is a test-only pattern.
* The testing strategy must not weaken production behavior merely to make
  tests pass.

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
