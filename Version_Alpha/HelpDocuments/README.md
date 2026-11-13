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
its connection string from `ConnectionStrings:Default` (override with the
`ConnectionStrings__Default` environment variable).


