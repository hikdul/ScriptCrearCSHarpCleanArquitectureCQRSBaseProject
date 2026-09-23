# Clean Code Script CSharp

Scaffolder that generates a complete .NET Clean Architecture project with
agentic development tooling (agents, commands, docs) ready for OpenCode.

## Requirements

- .NET SDK 10+ (`dotnet` on `PATH`)
- git
- Python 3.10+

## Usage

```bash
python3 generate_project.py                          # interactive Gruvbox wizard
python3 generate_project.py <Name> [options]         # scriptable CLI
```

Generates a new project with:

- Solution + 4 layer projects (`<Name>.Domain`, `<Name>.Application`,
  `<Name>.Infrastructure`, `<Name>.Api`) and 4 test projects (one per layer,
  plus an architecture-test project with NetArchTest rules that enforce the
  layer dependency graph).
- Controllers-based API (default) with a `HealthController` exposing `GET /health`,
  and OpenAPI in Development. Minimal API mode is available via `--api-style minimal`.
- **Database selection** (`--database postgres|sqlserver`): generates the
  Docker Compose file for the selected provider, wires EF Core + the matching
  provider package in Infrastructure, and writes the connection string to
  `appsettings.json`.
- Docker files: a root `docker-compose.yml` for the selected database plus a
  `docker/` folder with compose files and READMEs for **both** PostgreSQL and
  SQL Server, so the team can switch providers.
- A copy of the agentic development contract: `AGENTS.md`, `README.md` and
  `docs/` (agents, architecture, specifications, prompts, workflows, guides).
- `.opencode/` with 8 subagents and 7 commands wired to that contract.
- Automatic validation: `dotnet restore`, `dotnet build` and `dotnet test`
  must all pass, otherwise generation fails.
- `git init` with three logical commits and a clean working tree.

Run with no arguments to use the interactive **Gruvbox-themed wizard**
(project name, database, API style, framework, output directory and
validate/git toggles).

The tokens `Matchly`/`matchly` are replaced with the given project name
(PascalCase / lowercase) in file names, folder names and file contents.

## Target frameworks

The default target framework is `net10.0`. The script supports any TFM of the
form `net<major>.<minor>` with a major version of `10` or later (for example
`net10.0`, `net11.0`, `net12.0`). Framework-specific NuGet packages
(`Microsoft.AspNetCore.OpenApi`) are resolved by NuGet to the latest stable
version compatible with the chosen TFM, so no package versions are hardcoded.

Set it with `--framework`:

```bash
python3 generate_project.py MyApp --framework net11.0
```

Invalid or unsupported values (for example `net9.0`, `foo`) are rejected with
a clear error before any file is created.

## API style

By default the API uses ASP.NET Core Controllers: a `HealthController` is
generated in `src/<Name>.Api/Controllers/` exposing `GET /health`, and the
`Program.cs` configures `AddControllers()`/`MapControllers()`. This matches the
project contract (`docs/architecture/004-api-controllers.md`), which mandates
Controllers for HTTP endpoints.

To generate a minimal API instead:

```bash
python3 generate_project.py MyApp --api-style minimal
```

In minimal mode `Program.cs` registers the `/health` endpoint with
`MapGet` and no `Controllers/` folder is created. Both styles keep the same
public URL (`GET /health`) and the generated `Api.Tests` project verifies it
with a `WebApplicationFactory` test in both cases.

## Options

| Option                 | Description                                            |
| ---------------------- | ------------------------------------------------------ |
| `--database X`         | Database provider: `postgres` (default) or `sqlserver` |
| `--db-password PASS`   | SQL Server SA password (default: random, stored in `docker/.env`) |
| `--dir DIR`            | Output directory (default: `<Name>` in current dir)    |
| `--framework X`        | Target framework, TFM form `net<major>.<minor>` (default: `net10.0`, minimum: `net10.0`) |
| `--api-style X`        | API style: `controllers` (default) or `minimal`        |
| `--no-validate`        | Skip `dotnet restore/build/test`                       |
| `--no-git`             | Skip `git init` and initial commits                    |
| `--include-agent-runs` | Also copy `docs/agent-runs` historical records         |
| `--force`              | Delete and recreate the output directory if not empty  |
| `--wizard`, `-w`       | Force the interactive Gruvbox-themed selection wizard  |

## Examples

```bash
# Interactive wizard (project name, database, API style, etc.)
python3 generate_project.py

# Postgres + Controllers (default options)
python3 generate_project.py Matchly --dir ~/workspace/Matchly

# SQL Server with a custom SA password
python3 generate_project.py My-App --database sqlserver --db-password 'Str0ng!Pass'

# Minimal API, net10.0, skip git
python3 generate_project.py MyApp --api-style minimal --no-git

# Force the wizard even when flags are provided
python3 generate_project.py MyApp --wizard
```

## Databases & Docker

The `--database` flag selects which Docker Compose file becomes the root
`docker-compose.yml`. A `docker/` folder containing compose files and
READMEs for **both** PostgreSQL and SQL Server is always generated so the
team can switch providers without regenerating the project.

A `ConnectionStrings:Default` entry is written to
`src/<Name>.Api/appsettings.json` with the correct connection string for
the selected provider. For SQL Server, a random SA password is generated,
stored in `docker/.env` (gitignored) and printed in the summary.

After generation, the repository is on the `develop` branch (the recommended
state). Open the project in OpenCode and run `/feature` to start the agentic
TDP feature workflow. Read the generated
`docs/guides/agent-usage.md` for the full agent usage guide: recommended
state, commands, agents and feature specification format.

## Repository layout

- `generate_project.py` — the generator (single file, stdlib only).
- `HelpDocuments/` — source of the agentic development contract that is copied
  (with name substitution) into every generated project.
- `templates/` — tokenized code/config templates (`{{ProjectName}}`,
  `{{ProjectNameLower}}`):
  - `templates/code/` — C# sources, including the per-database EF Core
    registration variants (`InfrastructureRegistration.Postgres.cs` /
    `InfrastructureRegistration.SqlServer.cs`).
  - `templates/docker/` — Docker Compose files and per-database READMEs for
    PostgreSQL and SQL Server.
- `TextOfChat.md` — original agentic-programming guide the contract is derived
  from.

## Validation

Generated projects are validated with the script itself (`Restore`, `Build`,
`Tests`) and by manual checks: the architecture tests must fail when an illegal
layer dependency is introduced, and the `.opencode/` frontmatter must be valid
YAML (verified with `yaml.safe_load`).
