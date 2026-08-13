# Clean Code Script CSharp

Scaffolder that generates a complete .NET Clean Architecture project with
agentic development tooling (agents, commands, docs) ready for OpenCode.

## Requirements

- .NET SDK 10+ (`dotnet` on `PATH`)
- git
- Python 3.10+

## Usage

```bash
python3 generate_project.py <Name> [options]
```

Generates a new project with:

- Solution + 4 layer projects (`<Name>.Domain`, `<Name>.Application`,
  `<Name>.Infrastructure`, `<Name>.Api`) and 4 test projects (one per layer,
  plus an architecture-test project with NetArchTest rules that enforce the
  layer dependency graph).
- Controllers-based API (default) with a `HealthController` exposing `GET /health`,
  and OpenAPI in Development. Minimal API mode is available via `--api-style minimal`.
- `docker-compose.yml` with PostgreSQL 17.
- A copy of the agentic development contract: `AGENTS.md`, `README.md` and
  `docs/` (agents, architecture, specifications, prompts, workflows, guides).
- `.opencode/` with 8 subagents and 7 commands wired to that contract.
- Automatic validation: `dotnet restore`, `dotnet build` and `dotnet test`
  must all pass, otherwise generation fails.
- `git init` with three logical commits and a clean working tree.

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

| Option                | Description                                            |
| --------------------- | ------------------------------------------------------ |
| `--dir DIR`           | Output directory (default: `<Name>` in current dir)    |
| `--framework X`       | Target framework, TFM form `net<major>.<minor>` (default: `net10.0`, minimum: `net10.0`) |
| `--api-style X`       | API style: `controllers` (default) or `minimal`        |
| `--no-validate`       | Skip `dotnet restore/build/test`                       |
| `--no-git`            | Skip `git init` and initial commits                    |
| `--include-agent-runs`| Also copy `docs/agent-runs` historical records         |
| `--force`             | Delete and recreate the output directory if not empty  |

## Examples

```bash
python3 generate_project.py Matchly --dir ~/workspace/Matchly
python3 generate_project.py My-App --framework net10.0 --no-git
python3 generate_project.py MyApp --api-style minimal
```

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
  `{{ProjectNameLower}}`).
- `TextOfChat.md` — original agentic-programming guide the contract is derived
  from.

## Validation

Generated projects are validated with the script itself (`Restore`, `Build`,
`Tests`) and by manual checks: the architecture tests must fail when an illegal
layer dependency is introduced, and the `.opencode/` frontmatter must be valid
YAML (verified with `yaml.safe_load`).
