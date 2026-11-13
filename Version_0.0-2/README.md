# Version_0.0-2 — Clean Architecture Project Scaffolder

Scaffolder that generates a .NET solution following Clean Architecture with
CQRS (an in-process mediator), an agentic development setup for OpenCode, and
an EF Core persistence stack with a **two-tier test strategy**, based on
`Version_Alpha` with the concrete improvements found in `Version_0.0-1`.

This document describes what this version does, how to use it, and — honestly —
what has been verified to work in this environment.

## Relationship to the other versions

| Version      | Role                                                        | Status |
| ------------ | ----------------------------------------------------------- | ------ |
| `Version_Alpha` | Original Python generator; shallow specs, NU1202 failures on net10.0 at `dotnet add package` | Base copied into |
| `Version_0.0-1` | Bash rewrite; much more concrete specs and product-quality templates | **Broken** — crashes before producing a project (`copy_repo_file_rendered: command not found`) |
| `Version_0.0-2` | This version: Alpha's working pipeline + 0.0-1's concrete improvements | **Verified working** (see below) |

Notable: `Version_Alpha` fails today on net10.0 because `dotnet add package`
with no pinned version resolves to the newest (net11.0-only) releases.
`Version_0.0-2` pins every package to a net10.0-compatible version.

## Requirements

- .NET SDK 10+ (`dotnet` on `PATH`)
- git
- Python 3.10+

## Usage

```bash
python3 generate_project.py                          # interactive Gruvbox wizard
python3 generate_project.py <Name> [options]         # scriptable CLI
```

Generates:

- A solution with **five** layer projects:
  `<Name>.Domain` (framework-free), `<Name>.Security` (security abstractions
  only, no project references), `<Name>.Application` (use cases +
  abstractions + in-process mediator), `<Name>.Infrastructure` (EF Core,
  provider, UnitOfWork, design-time factory), `<Name>.Api` (HTTP + DI
  composition root).
- Six test projects: `Domain.Tests`, `Application.Tests`,
  `Infrastructure.Tests`, `Api.Tests`, `Architecture.Tests` (NetArchTest —
  now including the Security dependency rules) and `tests/<Name>.TestSupport`
  (a helper class library with an in-memory SQLite factory and the gated
  `[DatabaseFact]` / `[DatabaseTheory]` xUnit attributes).
- A working CQRS pipeline out of the box: `Application` registers every
  handler found in its assembly automatically via
  `services.AddApplication()` (called from `Program.cs`), dispatches through
  `SimpleMediator`, and fails loudly (`MediatorException`) on zero or
  duplicate handler registrations.
- Domain entities use **UUIDv7** identifiers (`Domain.EntityId.New()`).
- `IUnitOfWork` / `Infrastructure.UnitOfWork` committed through the scoped
  context; EF Core `DbContext` uses assembly-scanned entity configurations.
- **No secret enters `appsettings.json`**: its connection string is
  credential-free. SQL Server's SA password lives only in `docker/.env`
  (gitignored) and is injected at run time via `ConnectionStrings__Default`.
  `dotnet ef` uses the design-time factory, which reads
  `<PROJECT_NAME>_CONNECTION_STRING` from the environment.
- Docker files for both PostgreSQL and SQL Server, a root `docker-compose.yml`
  for the selected provider, and READMEs explaining how to run the API and
  apply migrations.
- `.editorconfig` declaring the repository's formatting contract.
- The agentic development contract: `AGENTS.md`, `README.md`,
  `docs/` (including the ported two-tier testing strategy, feature close
  protocol, UUIDv7 rule and the 586-line `000-example-specification.md`
  format reference with `BR-NNN`/`AC-NNN` identifiers and traceability) and
  `.opencode/` (8 subagents, 7 commands).

## Options

| Option                 | Description |
| ---------------------- | ----------- |
| `--database X`         | `postgres` (default) or `sqlserver` |
| `--db-password PASS`   | SQL Server SA password (default: random, stored in `docker/.env`) |
| `--dir DIR`            | Output directory (default: `<Name>` in current dir) |
| `--framework X`        | TFM of the form `net<major>.<minor>` (default: `net10.0`, minimum: `net10.0`) |
| `--api-style X`        | `controllers` (default) or `minimal` |
| `--no-validate`        | Skip `dotnet restore/build/test` |
| `--no-git`             | Skip `git init` and initial commits |
| `--include-agent-runs` | Also copy `docs/agent-runs` historical records |
| `--force`              | Delete and recreate the output directory if not empty |
| `--wizard`, `-w`       | Force the interactive Gruvbox wizard |

## Verification status (this environment, .NET SDK 10.0.403)

Four generation variants were produced into throwaway directories and
validated end to end: `--database postgres` (default) with git enabled,
`--database sqlserver --no-git`, `--api-style minimal --no-git`, and an
initial `--no-git` run used to develop the fixes above:

| Step              | Result |
| ----------------- | ------ |
| `dotnet restore`  | PASS (all variants) |
| `dotnet build`    | PASS (all variants) |
| `dotnet test`     | PASS — 21 passed, 1 skipped (all variants) |
| `dotnet format --verify-no-changes` | PASS (all variants; informational only, not a generation gate) |
| Name sweep        | CLEAN (all variants) |
| Git flow          | 3 commits on `develop`, tree clean (default variant) |
| SQL Server run    | appsettings.json credential-free; SA password only in gitignored `docker/.env` and printed once; no password found in generated sources |

Test counts: `Domain.Tests` 4 (EntityId UUIDv7/uniqueness/timestamp ordering),
`Application.Tests` 4 (CQRS probe: dispatch of unique command and void
request, loud failure on duplicate handlers, smoke test),
`Architecture.Tests` 10 (incl. the Security rules),
`Api.Tests` 1 (HTTP health round trip),
`Infrastructure.Tests` 5 passed + 1 skipped
(`Configured_provider_can_open_connection`, `[DatabaseFact]` — skips without
a connection string; **fails** loudly when one is set and the database is
unreachable, as verified against an unreachable host).

The CQRS probe verified end to end that `AddApplication()` registers handlers
from the Application assembly and `IMediator` dispatches to exactly one
handler, including the duplicate-registration error path.

## Known limitations

- `dotnet ef` was not run during verification (the `dotnet-ef` global tool is
  not installed here); the design-time factory compiles and follows the
  standard `IDesignTimeDbContextFactory` pattern.
- The gated tier has not been run against a real PostgreSQL/SQL Server (no
  database service was started in this environment); it was verified only for
  its skip/fail behavior.
- `dotnet format --verify-no-changes` is **informational** during generation:
  it reports deviations but never fails generation.
- The generated project is not security-audited; Security is a scaffolding
  layer with abstractions only.

## Comparison with Version_0.0-1

`Version_0.0-2` ports `Version_0.0-1`'s concrete improvements — UUIDv7
identifiers, the in-process mediator with single-handler enforcement,
`IUnitOfWork`/`UnitOfWork`, assembly-scanned entity configurations, the
design-time `DbContextFactory`, the Security project, the TestSupport
helpers, the two-tier testing strategy with a gated `[DatabaseFact]`/
`[DatabaseTheory]` tier, the 586-line specification format reference, the
feature close protocol and the UUIDv7/persistence/close/proof-gap sections of
its agent contract — while keeping `Version_Alpha`'s working generation
pipeline, its Docker setup, its git flow and its OpenCode tooling, and
fixing the net10.0 package-resolution failures that made `Version_Alpha`
unusable on current SDKs.

## Repository layout

- `generate_project.py` — the generator (single file, stdlib only).
- `HelpDocuments/` — source of the agentic development contract, copied (with
  name substitution) into every generated project.
- `templates/` — tokenized templates:
  - `templates/code/` — C# sources (mediator, UnitOfWork, factories, tests,
    per-database EF Core registration variants).
  - `templates/docker/` — Docker Compose files, READMEs, Dockerfiles.
  - `templates/dotfiles/.editorconfig` — the formatting contract.
- `TextOfChat.md` — original agentic-programming reference (not copied).

## Text conventions

- `HelpDocuments/` and `templates/docker/`, `templates/.gitignore`:
  `Matchly` → PascalCase of the project name, `matchly` → lowercase.
- `templates/code/` and `templates/dotfiles/`: `{{ProjectName}}` /
  `{{ProjectNameLower}}`, plus inline tokens substituted by hand in
  `Generator.write_custom_files()`: `{{Layer}}`, `{{TestLayer}}`,
  `{{ProviderName}}`, `{{ProviderMethod}}`, `{{ConnectionStringVariable}}`.
- Inline tokens appear only in `.cs` files written through the generator; a
  name sweep for leftover tokens runs at the end of every generation (reported,
  not enforced).
