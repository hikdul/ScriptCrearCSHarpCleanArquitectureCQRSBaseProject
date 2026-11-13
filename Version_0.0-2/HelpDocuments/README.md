# Matchly

Matchly is an experimental web application used to study
agentic programming, TDD, Test-Driven Prompting and Clean Architecture.

## Goals

- Agentic software development
- Test-Driven Development
- Test-Driven Prompting
- Clean Code
- Clean Architecture
- SOLID principles
- Automated validation
- Controlled agent iterations

## Architecture

The project follows Clean Architecture.

```text
Matchly.Api
     ↓
Matchly.Application
     ↓
Matchly.Domain

Matchly.Application
     ↓
Matchly.Security

Matchly.Infrastructure
     ↓
Matchly.Application
     ↓
Matchly.Domain

Matchly.Infrastructure
     ↓
Matchly.Security
```

- `Matchly.Domain` — business rules; no framework dependencies
- `Matchly.Security` — security abstractions only; no project references
- `Matchly.Application` — use cases, CQRS handlers, abstractions
- `Matchly.Infrastructure` — EF Core, provider, persistence, UnitOfWork
- `Matchly.Api` — HTTP API and composition root

## Development

The project is developed incrementally through small features.

Each feature must be:

1. Specified
2. Planned
3. Tested
4. Implemented
5. Validated
6. Reviewed

## Agentic Development

The project ships with an agentic development setup (OpenCode agents,
commands and documentation contract). Before using it, read
[`docs/guides/agent-usage.md`](docs/guides/agent-usage.md): recommended
repository state, commands, agents and feature specification format.

Run the full feature workflow from OpenCode with:

```text
/feature "short description of the feature"
```

## Database

The application uses the database selected at generation time
(**PostgreSQL** or **SQL Server**). Docker Compose files are included for
both so the team can switch providers.

To start the selected database with Docker:

```bash
docker compose up -d
```

Read `docker/README.md` for provider-specific details: images, ports,
connection strings and how to switch to the other database. The API reads
its connection string from `ConnectionStrings:Default` in `appsettings.json`,
which carries no credentials. Override it with the `ConnectionStrings__Default`
environment variable whenever a secret is required — never commit one.

## Test Tiers

Persistence is covered by two tiers: a default in-memory SQLite tier that
runs anywhere, and a gated tier (`[DatabaseFact]` / `[DatabaseTheory]`)
that runs only when `<PROJECT_NAME>_CONNECTION_STRING` is set. A skipped
gated test is not a passing test; see `docs/architecture/005-testing-strategy.md`.


