# {{PROJECT_NAME}} — Agent Instructions (Compact)

## Read first (authoritative)

- `docs/workflows/tdp-feature-workflow.md` (mandatory flow + close sequence)
- `docs/guides/agent-usage.md` (operational reference)
- `docs/specifications/*.md` (feature source of truth)
- `tests/{{PROJECT_NAME}}.Architecture.Tests/*.cs` (enforced boundaries)

If prose and code conflict, trust code/tests.

## Architecture that is enforced

- `{{PROJECT_NAME}}.sln` is the source of truth.
- Production projects are exactly:
  - `src/{{PROJECT_NAME}}.Domain` (framework-free)
  - `src/{{PROJECT_NAME}}.Security` (security abstractions only)
  - `src/{{PROJECT_NAME}}.Application` (use cases + abstractions)
  - `src/{{PROJECT_NAME}}.Infrastructure` (persistence and external implementations)
  - `src/{{PROJECT_NAME}}.Api` (composition root + HTTP)
- `Domain`, `Application`, `Infrastructure` and `Security` each have an
  `AssemblyMarker`; keep them.
- Controllers must dispatch via `IMediator`; controllers must not name
  Infrastructure types.
- EF Core and database provider packages belong only in Infrastructure
  (`src/{{PROJECT_NAME}}.Infrastructure/{{PROJECT_NAME}}.Infrastructure.csproj`).
- The host must not create or migrate schema at startup (`EnsureCreated` and
  auto-migrate are test-only patterns).

## Identifier rule (UUIDv7)

- Every new entity identifier is generated with
  `{{PROJECT_NAME}}.Domain.EntityId.New()` (which calls
  `Guid.CreateVersion7()`), never `Guid.NewGuid()`.
- Non-entity values (a JWT `jti`, a test fixture id) are exempt.
- New entities added later must follow the same rule.

## Current feature snapshot

No product feature is implemented yet. The bootstrap specification at
`docs/specifications/000-spec-example.md` explains the specification format;
it is a reference document, not a feature to implement.

## Commands (repo root)

- Mandatory validation:
  - `dotnet build`
  - `dotnet test`
  - `dotnet test tests/{{PROJECT_NAME}}.Architecture.Tests/{{PROJECT_NAME}}.Architecture.Tests.csproj`
  - `dotnet format --verify-no-changes`
- Focused runs:
  - `dotnet test tests/{{PROJECT_NAME}}.Domain.Tests/{{PROJECT_NAME}}.Domain.Tests.csproj`
  - `dotnet test tests/{{PROJECT_NAME}}.Application.Tests/{{PROJECT_NAME}}.Application.Tests.csproj`
  - `dotnet test tests/{{PROJECT_NAME}}.Infrastructure.Tests/{{PROJECT_NAME}}.Infrastructure.Tests.csproj`
  - `dotnet test tests/{{PROJECT_NAME}}.Api.Tests/{{PROJECT_NAME}}.Api.Tests.csproj`
- SQL Server local:
  - set `{{PROJECT_NAME_UPPER}}_SQLSERVER_SA_PASSWORD`
  - `docker compose up -d` (container: `{{PROJECT_NAME_LOWER}}-sqlserver`, host port `14330`)
  - set `{{PROJECT_NAME_UPPER}}_SQLSERVER_CONNECTION_STRING`
  - apply migrations:
    `dotnet ef database update --project src/{{PROJECT_NAME}}.Infrastructure --context {{PROJECT_NAME}}DbContext`

## Testing quirk that matters

- Two tiers are intentional:
  - default: SQLite in-memory (always runs)
  - gated: `[SqlServerFact]` / `[SqlServerTheory]` (skips unless
    `{{PROJECT_NAME_UPPER}}_SQLSERVER_CONNECTION_STRING` is set)
- For schema, provider or concurrency features, a run with skips is
  incomplete; require zero skips in the gated tier.

## Workflow / git rules that must not be broken

- One active feature at a time, on `feature/<id>-<slug>` from `develop`.
- Before user approval: **no history edits** (no commit/merge/rebase/reset/push/branch-delete).
- After user explicitly approves **and says “close”**: execute the full close
  sequence from `docs/workflows/tdp-feature-workflow.md` §13.7 without re-asking.
- `develop -> main` is release-only work (not feature close).

## Known proof gaps

None recorded at bootstrap. Record new gaps here when a validation gap is
accepted deliberately, with the feature id and the reason.
