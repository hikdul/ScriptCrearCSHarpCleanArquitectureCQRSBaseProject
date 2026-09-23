# Repository

Scaffolder that generates .NET Clean Architecture projects with agentic
development tooling (OpenCode agents, commands, docs) for OpenCode.

Single entry point: `generate_project.py`.

## What this repo is NOT

This is not the generated application. The `.NET` code under `templates/` and
the docs under `HelpDocuments/` are **source templates** that get copied
(with name substitution) into the output project. Do not treat them as a
buildable .NET project.

## Quick reference

```bash
# Generate a project (requires: dotnet SDK 10+, git, Python 3.10+)
python3 generate_project.py <Name> [--dir <output>] [--framework net10.0]
                                  [--api-style controllers|minimal]
                                  [--database postgres|sqlserver]
                                  [--no-validate] [--no-git] [--force]
python3 generate_project.py       # interactive Gruvbox wizard

# Validate a generated project (inside the generated directory)
dotnet restore && dotnet build && dotnet test

# Architecture tests only
dotnet test tests/<Name>.Architecture.Tests/<Name>.Architecture.Tests.csproj
```

## Token substitution

The generator replaces tokens in two passes:

1. `Matchly` -> `<ProjectName>` (PascalCase), `matchly` -> lowercase form
   - Applied to: file names, folder names, file contents in `HelpDocuments/`
2. `{{ProjectName}}` / `{{ProjectNameLower}}` -> PascalCase / lowercase
   - Applied to: `templates/` files only

If you add new templates, use the correct token convention for the directory.
Mixing them up is a common bug.

## Validation pipeline

The script runs validation after generation unless `--no-validate` is passed:

1. `dotnet restore`
2. `dotnet build`
3. `dotnet test`

Generation fails with a non-zero exit if any step fails. The script also
performs a name sweep to catch leftover `Matchly`/`matchly` references.

## Architecture constraints (enforced by generated tests)

Dependency graph that `ArchitectureTests.cs` enforces via NetArchTest:

```
Domain -> nothing (pure business rules)
Application -> Domain only
Infrastructure -> Application, Domain
API -> Application; API -> Infrastructure (composition root, DI wiring only)
```

Domain must never reference ASP.NET Core, EF Core, or PostgreSQL. These rules
are in `templates/code/ArchitectureTests.cs`.

## Structure

```
generate_project.py          # The generator (stdlib only, no deps)
HelpDocuments/               # Source docs copied into generated projects
  AGENTS.md                  # -> becomes the generated project's AGENTS.md
  README.md                  # -> becomes the generated project's README.md
  docs/                      # -> docs/ in generated project
templates/
  code/                      # Tokenized .cs files (including per-database
                             #   EF Core registration variants)
  docker/                    # Docker Compose files + per-database READMEs
                             #   (PostgreSQL and SQL Server)
TextOfChat.md                # Original reference material (not copied)
```

## Database selection

`--database postgres|sqlserver` selects the EF Core provider wired into
Infrastructure, the connection string written to `appsettings.json`, and
which compose file becomes the generated project's root `docker-compose.yml`.
The `docker/` folder always contains compose files and READMEs for **both**
databases so the team can switch. SQL Server credentials are generated with
Python `secrets`, stored in `docker/.env` (gitignored) and printed once in
the summary.

## Gotchas

- The script uses only Python stdlib — no `requirements.txt` needed.
- `dotnet SDK 10+` is required; the script rejects TFMs below `net10.0`.
- The generated project is git-initialized with 3 commits and lands on `develop`.
- `--force` deletes the output directory without prompting.
- The `--api-style minimal` flag omits `Controllers/` and uses `MapGet` instead.
- Architecture tests use `NetArchTest.Rules` — the test assembly references all
  4 source projects to inspect dependency edges.
- The `HelpDocuments/AGENTS.md` content is the contract for **generated**
  projects. This file (`AGENTS.md` at the root) is for agents working on
  **this scaffolder**.
