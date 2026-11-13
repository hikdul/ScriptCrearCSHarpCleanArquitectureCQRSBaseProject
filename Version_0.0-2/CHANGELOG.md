# Changelog — Version_0.0-2

Based on `Version_Alpha`, with the concrete improvements found in `Version_0.0-1`.

## Added

- `Security` project (`<Name>.Security`): security abstractions only, no
  project references; `Application` and `Infrastructure` reference it.
- `Architecture.Tests`: Security boundary rules (Security must not depend on
  Domain/Application/Infrastructure/Api; Domain must not depend on Security).
  10 architecture facts, up from 5.
- `tests/<Name>.TestSupport` helper library: `SqliteDatabase` (in-memory
  SQLite factory), `DatabaseFact`/`DatabaseTheory` xUnit attributes that skip
  unless `<PROJECT_NAME>_CONNECTION_STRING` is set.
- Application layer: `IMediator`/`IRequest`/`IRequestHandler` (including
  `IRequestHandler<>` for void requests), `SimpleMediator` (compiled-delegate
  dispatch; throws `MediatorException` on zero or duplicate handler
  registrations), `MediatorException`, `Application.Abstractions.IUnitOfWork`.
- `ApplicationServiceCollectionExtensions.AddApplication()`: scans the
  Application assembly, registers every closed `IRequestHandler<,>` /
  `IRequestHandler<>` and `IMediator → SimpleMediator`; `Program.cs` calls it.
- Domain: UUIDv7 `EntityId.New()` (RFC 9562) with unit tests
  (version nibble, uniqueness, timestamp ordering).
- Infrastructure: `UnitOfWork` (scoped, commits through the context),
  assembly-scanned `OnModelCreating` on the `DbContext`, design-time
  `DbContextFactory` reading `<PROJECT_NAME>_CONNECTION_STRING` (no
  credentials in the repo), registered as scoped via `AddInfrastructure`.
- `.editorconfig` (space indentation, 4 spaces; 2 for YAML).
- EF Core `Design` package pinned and marked `PrivateAssets=all`.
- Docs in the generated project: two-tier testing strategy
  (`005-testing-strategy.md`), feature close protocol (new §14 of the TDP
  workflow and §27 of `AGENTS.md`), UUIDv7 identifier rule (§25), two-tier
  persistence testing (§26), known proof gaps (§28), the 586-line
  `000-example-specification.md` format reference (BR-/AC- identifiers,
  traceability, Draft → Approved → Implemented lifecycle, worked example,
  amendment flow), approval/closing semantics in `agent-usage.md` (new §9),
  `docs/README.md`, `docs/agents/README.md`, `docs/agent-runs/README.md`,
  Security layer in architecture docs (`architecture.md`,
  `001-clean-architecture.md`), concrete mediator/CQRS/UnitOfWork/api
  dispatch sections, `README.md` with architecture overview, test tiers and
  the credential-free connection string contract.
- `Version_0.0-2/README.md` and this changelog.

## Changed

- All NuGet packages pinned to net10.0-compatible versions
  (OpenApi/Mvc.Testing/EF Core 10.0.12, Sqlite/Tests pins, Npgsql 10.0.1,
  NetArchTest.Rules 1.3.2, FluentAssertions 8.11.0, xunit.extensibility.core
  2.9.3). Unpinned `dotnet add package` resolved to net11.0-only releases
  and broke generation with NU1202.
- `appsettings.json` now ships a **credential-free** connection string
  (SQL Server: no SA password; PostgreSQL unchanged). Override with
  `ConnectionStrings__Default` at run time.
- `Dockerfile` also copies the `Security` project before restore.
- `docker/README.postgres.md` / `docker/README.sqlserver.md` document the
  EF Core design-time factory (`<PROJECT_NAME>_CONNECTION_STRING`) and the
  credential-free `appsettings.json`.
- `dotnet format --verify-no-changes` is informational only and never fails
  generation (it did not gate generation before either).
- Name-sweep check in the generator now also flags the `{{Layer}}`,
  `{{TestLayer}}`, `{{ProviderName}}`, `{{ProviderMethod}}` and
  `{{ConnectionStringVariable}}` inline tokens.
- Repo-level docs (`README.md`, `AGENTS.md`) updated accordingly.

## Verified (this environment, SDK 10.0.403)

Generated project: `dotnet restore`/`build`/`test`/`format` PASS, name sweep
CLEAN; test totals 21 passed + 1 skipped (the gated provider test), including
the CQRS round trip. See "Verification status" in `README.md`.
