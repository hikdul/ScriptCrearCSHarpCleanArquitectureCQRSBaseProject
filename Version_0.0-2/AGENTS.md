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

Two places break the simple rule:

- Agent bodies are files under `HelpDocuments/docs/agents/*.md` (Matchly
  tokens); command bodies are inline in `generate_project.py` (the `COMMANDS`
  list) and use `{{ProjectName}}` tokens.
- `templates/code/` also carries inline-only tokens — `{{Layer}}`,
  `{{TestLayer}}`, `{{ProviderName}}`, `{{ProviderMethod}}`,
  `{{ConnectionStringVariable}}` — substituted by hand in
  `Generator.write_custom_files()`, not by the generic pass.

## Validation pipeline

The script runs validation after generation unless `--no-validate` is passed:

1. `dotnet restore`
2. `dotnet build`
3. `dotnet test`

`dotnet format --verify-no-changes` also runs, but only as an informational
check — it never fails generation. Generation fails with a non-zero exit if
any step of 1–3 fails. A name sweep for leftover
`Matchly`/`matchly`/`{{...}}`/`{{ProviderMethod}}`/`{{ConnectionStringVariable}}`
references also runs every time, but it only reports in the summary — it does
not fail the run, so verify the output yourself when adding templates.

## Architecture constraints

Designed dependency graph, wired with `dotnet add reference` in
`Generator.configure_projects`:

```
Domain -> nothing (pure business rules)
Security -> nothing (security abstractions only; no project references)
Application -> Domain, Security
Infrastructure -> Application, Domain, Security
API -> Application; API -> Infrastructure (composition root, DI wiring only)
```

`Application` references no ASP.NET Core; it needs
`Microsoft.Extensions.DependencyInjection.Abstractions` only to register the
handlers from `AddApplication()`. Tests enforce part of this: the 10
`[Fact]`s in `templates/code/ArchitectureTests.cs` are namespace-level
checks. Domain has no dependency on Application/Infrastructure/Api/Security;
Security has none on any other layer; Application has none on
Infrastructure/Api. Infrastructure and Api are never the inspected subject,
and no rule scans for ASP.NET Core / EF Core / provider packages — new
project references or packages added to those layers will **not** be caught.
The stronger bans (Domain must not reference ASP.NET Core, EF Core, or a
database provider) are contract rules in `HelpDocuments/` docs, not enforced
tests.

## Structure

```
generate_project.py          # The generator (stdlib only, no deps)
HelpDocuments/               # Source docs copied into generated projects
  AGENTS.md                  # -> becomes the generated project's AGENTS.md
  README.md                  # -> becomes the generated project's README.md
  docs/                      # -> docs/ in generated project (workflows,
                             #    architecture, agents/, specifications/,
                             #    guides/, prompts/, agent-runs/ (empty))
templates/
  code/                      # Tokenized .cs files: flat files at the root
                             #   (DbContext, Program*, ArchitectureTests, ...)
                             #   and subfolders mirroring target layout
                             #   (application/, domain/, infrastructure/,
                             #   testsupport/, tests/)
  docker/                    # Docker Compose files + per-database READMEs
                             #   plus Dockerfile / Dockerfile.dev, mirrored
                             #   into the generated project root
  dotfiles/.editorconfig     # Formatting contract, copied verbatim
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
- All NuGet packages are pinned to net10.0-compatible versions in
  `PACKAGE_VERSIONS` (notably `Microsoft.AspNetCore.Mvc.Testing` 10.0.12 and
  `Microsoft.AspNetCore.OpenApi` 10.0.12). Leaving them unpinned resolves to
  newest (net11.0-only) releases and fails restore with NU1202. The EF Core
  `Design` package is pinned and its `PackageReference` is rewritten with
  `PrivateAssets=all` after `dotnet add package`.
- The Application project gets `Microsoft.Extensions.DependencyInjection.Abstractions`
  10.0.12 only to register handlers; it must not get ASP.NET Core references.
- `tests/<Name>.TestSupport` is a **class library** (not an xunit project) so
  generated test projects reference it without creating a test assembly.
- The generated project is git-initialized with 3 commits and lands on `develop`.
- `--force` deletes the output directory without prompting.
- The `--api-style minimal` flag omits `Controllers/` and uses `MapGet` instead.
- Architecture tests use `NetArchTest.Rules` — the test assembly references all
  5 source projects (incl. Security) to inspect dependency edges.
- `AppV02`-style throwaway verification: `python3 generate_project.py AppV02
  --dir /tmp/opencode/AppV02 --no-git` then inspect
  `AppV02.sln` build/test output; remove the directory afterwards.
- The `HelpDocuments/AGENTS.md` content is the contract for **generated**
  projects. This file (`AGENTS.md` at the root) is for agents working on
  **this scaffolder**.
- `copy_tree()` / `renamed_path()` in `generate_project.py` are dead code —
  never called. Docs are copied inline in `Generator.copy_docs()`.
- Generation normally needs network: `dotnet add package` and the validation
  `restore` hit NuGet. On network-shaped failures the script prints a
  "check your internet connection" hint; the code is fine.
- For a fast local dev loop use `--no-validate --no-git --force` into a
  throwaway `--dir` — it skips all NuGet and git work.
- The initial `git init` commits require `git user.name`/`user.email` to be
  configured, otherwise generation fails with a clear error.
