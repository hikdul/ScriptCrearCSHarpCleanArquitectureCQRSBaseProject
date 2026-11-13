# {{PROJECT_NAME}}

{{PROJECT_NAME}} is a .NET solution bootstrapped from a reusable Clean
Architecture project generator. The product is intentionally empty: the
engineering practices, workflow, agents and test infrastructure are in place,
but no business feature has been implemented yet.

## Goals

- Agentic software development
- Test-Driven Development (TDD)
- Test-Driven Prompting (TDP)
- Clean Code
- Clean Architecture
- SOLID principles
- Automated validation
- Controlled agent iterations

## Architecture

The solution follows Clean Architecture with strict project boundaries:

- `src/{{PROJECT_NAME}}.Domain`: entities and business rules (framework-free)
- `src/{{PROJECT_NAME}}.Security`: security abstractions
- `src/{{PROJECT_NAME}}.Application`: use cases, mediator handlers, abstractions
- `src/{{PROJECT_NAME}}.Infrastructure`: persistence and external implementations
- `src/{{PROJECT_NAME}}.Api`: HTTP API and composition root

```text
{{PROJECT_NAME}}.Api
     ↓
{{PROJECT_NAME}}.Application
     ↓
{{PROJECT_NAME}}.Domain

{{PROJECT_NAME}}.Infrastructure
     ↓
{{PROJECT_NAME}}.Application
     ↓
{{PROJECT_NAME}}.Domain
```

The API is the composition root and is the only project allowed to reference
Infrastructure, and only to register its implementations. Controllers dispatch
Application requests through `IMediator`; they never name Infrastructure types.

Architecture rules are executable. See
`tests/{{PROJECT_NAME}}.Architecture.Tests/ArchitectureTests.cs`.

## Run on localhost

### 1) Prerequisites

- .NET SDK matching the solution's target framework
- SQL Server running locally, or Docker

### 2) Configure the connection string

No credential is committed. Set the connection string in your shell:

```bash
export {{PROJECT_NAME_UPPER}}_SQLSERVER_CONNECTION_STRING="Server=localhost;Database={{PROJECT_NAME_LOWER}};User Id=sa;Password=<your-password>;Encrypt=True;TrustServerCertificate=True;"
```

### 3) Start SQL Server (optional, Docker)

```bash
export {{PROJECT_NAME_UPPER}}_SQLSERVER_SA_PASSWORD="<local password>"
docker compose up -d
export {{PROJECT_NAME_UPPER}}_SQLSERVER_CONNECTION_STRING="Server=localhost,14330;Database={{PROJECT_NAME_LOWER}};User Id=sa;Password=${{PROJECT_NAME_UPPER}}_SQLSERVER_SA_PASSWORD;Encrypt=True;TrustServerCertificate=True;"
```

The container is `{{PROJECT_NAME_LOWER}}-sqlserver` and listens on host port
`14330`. It is local development only.

### 4) Apply migrations

The schema is created by Entity Framework Core migrations. The host never
creates or alters the schema at startup.

```bash
dotnet ef database update --project src/{{PROJECT_NAME}}.Infrastructure --context {{PROJECT_NAME}}DbContext
```

### 5) Run the API

```bash
dotnet run --project src/{{PROJECT_NAME}}.Api
```

The API starts on the local Kestrel URLs shown in the console. It has no
product endpoints yet; add the first feature through the workflow.

## Validate the repository

```bash
dotnet build
dotnet test
dotnet test tests/{{PROJECT_NAME}}.Architecture.Tests/{{PROJECT_NAME}}.Architecture.Tests.csproj
dotnet format --verify-no-changes
```

The default test tier uses in-memory SQLite and runs anywhere. Tests marked
`[SqlServerFact]` or `[SqlServerTheory]` skip unless
`{{PROJECT_NAME_UPPER}}_SQLSERVER_CONNECTION_STRING` is set. For schema,
provider or concurrency work, require zero skips in that gated tier.

## Development workflow

Features are developed incrementally and each one must be:

1. Specified
2. Planned
3. Tested (RED)
4. Implemented (GREEN)
5. Refactored
6. Architecture-validated
7. Validated

The mandatory process is
[`docs/workflows/tdp-feature-workflow.md`](docs/workflows/tdp-feature-workflow.md).
The operational agent reference is
[`docs/guides/agent-usage.md`](docs/guides/agent-usage.md).

## Agentic development

The repository ships with an OpenCode configuration in `.opencode/`:
8 agents and 7 commands driven by the documentation contract in `docs/`.

Start the full workflow from OpenCode:

```text
/feature "short description of the first feature"
```

Or run the stages individually: `/plan`, `/tests`, `/implement`, `/refactor`,
`/architecture`, `/validate`.

Read `AGENTS.md` first. It contains the mandatory rules that no agent may
override.

## Specifications

`docs/specifications/` is the source of truth for feature behavior.
`docs/specifications/000-spec-example.md` explains how to write a valid
specification. It is a reference document, not an implemented feature.

## Database

Entity Framework Core and the SQL Server provider are referenced only by
`src/{{PROJECT_NAME}}.Infrastructure`. Domain, Security and Application stay
provider independent.

Create the first migration after modelling the first entity:

```bash
dotnet ef migrations add InitialCreate \
  --project src/{{PROJECT_NAME}}.Infrastructure \
  --context {{PROJECT_NAME}}DbContext
```

## Project generation

This project was generated from a reusable template repository. The generator
itself lives in `tools/project-generator/` in that source repository and is
not part of this product repository.
