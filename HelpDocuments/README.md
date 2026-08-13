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

Matchly.Infrastructure
     ↓
Matchly.Application
     ↓
Matchly.Domain
```

## Development

The project is developed incrementally through small features.

Each feature must be:

1. Specified
2. Planned
3. Tested
4. Implemented
5. Validated
6. Reviewed

## Database

The application uses PostgreSQL. To start a local database with Docker:

```bash
docker compose up -d
```

This starts `matchly-postgres` on `localhost:5432` with database `matchly`
and user `postgres` (trust auth, local development only).

On startup, the API creates the database schema automatically via
`EnsureCreatedAsync`, so no migration step is required.


