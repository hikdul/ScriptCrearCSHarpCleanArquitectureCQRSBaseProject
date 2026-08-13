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
- Minimal API with a `/health` endpoint and OpenAPI in Development.
- `docker-compose.yml` with PostgreSQL 17.
- A copy of the agentic development contract: `AGENTS.md`, `README.md` and
  `docs/` (agents, architecture, specifications, prompts, workflows).
- `.opencode/` with 8 subagents and 7 commands wired to that contract.
- Automatic validation: `dotnet restore`, `dotnet build` and `dotnet test`
  must all pass, otherwise generation fails.
- `git init` with three logical commits and a clean working tree.

The tokens `Matchly`/`matchly` are replaced with the given project name
(PascalCase / lowercase) in file names, folder names and file contents.

## Options

| Option                | Description                                            |
| --------------------- | ------------------------------------------------------ |
| `--dir DIR`           | Output directory (default: `<Name>` in current dir)    |
| `--framework X`       | Target framework (default: `net10.0`)                  |
| `--no-validate`       | Skip `dotnet restore/build/test`                       |
| `--no-git`            | Skip `git init` and initial commits                    |
| `--include-agent-runs`| Also copy `docs/agent-runs` historical records         |
| `--force`             | Delete and recreate the output directory if not empty  |

## Examples

```bash
python3 generate_project.py Matchly --dir ~/workspace/Matchly
python3 generate_project.py My-App --framework net9.0 --no-git
```

After generation, open the project in OpenCode and run `/feature` to start the
agentic TDP feature workflow.

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
