# Project Generators — English Usage Guide

This repository ships **two generators** that create a new .NET Clean
Architecture solution with agentic development tooling (`.opencode/` agents and
commands, the TDP workflow docs, specifications). Neither is currently clean
in a fresh checkout: Version_Alpha scaffolds correctly but its final NuGet
step is reported to fail here (§1.5); Version_0.0-1 fails earlier (§2.5).

| Generator | Language | Status (verified) |
| --- | --- | --- |
| `Version_Alpha/generate_project.py` | Python 3.10+ | ⚠️ Scaffolding works; final `dotnet add package` reported incompatible on `net10.0` — see §1.5 |
| `Version_0.0-1/create-project.sh` | Bash | ⚠️ Incomplete — fails during generation (see the verified defect list, §2.5) |

This guide is written in English for general use and is the single reference.

---

## 1. Version_Alpha — the more complete generator

### 1.1 Layout

```text
Version_Alpha/
  generate_project.py   # the generator (stdlib only, no dependencies)
  HelpDocuments/        # agentic contract copied into every generated project
    AGENTS.md           #   -> becomes the generated project's AGENTS.md
    README.md           #   -> becomes the generated project's README.md
    docs/               #   -> becomes docs/ (agents, architecture, workflows, ...)
  templates/            # tokenized .NET templates (<ProjectName>)
    code/               #   C# sources + per-database EF Core registration variants
    docker/             #   Compose files and Dockerfiles
```

### 1.2 What it generates

- A `<Name>.sln` solution with 4 layer projects
  (`<Name>.Domain`, `<Name>.Application`, `<Name>.Infrastructure`,
  `<Name>.Api`) plus 5 test projects.
- Clean Architecture dependency graph: Domain → nothing, Application → Domain,
  Infrastructure → Application + Domain, Api → Application + Infrastructure
  (composition root only).
- A `HealthController` exposing `GET /health` (default; `--api-style minimal`
  uses `MapGet` instead).
- Database selection: `--database postgres|sqlserver` wires the EF Core
  provider, the connection string in `appsettings.json`, and which
  `docker-compose.yml` is the root one. Both compose files are always also
  placed in `docker/`.
- Documentation: `AGENTS.md`, `README.md`, `docs/` (agents, architecture,
  workflows, guides, specifications) and `.opencode/` with 8 agents and 7
  commands.
- A git repository initialized with 3 logical commits and switched to the
  `develop` branch (recommended feature-development state).
- Token substitution: `Matchly`/`matchly` → `<ProjectName>`/`<projectname>`
  for file and folder names and contents of `HelpDocuments/`;
  `{{ProjectName}}`/`{{ProjectNameLower}}` for `templates/`.

### 1.3 Requirements

- .NET SDK 10+ (`dotnet` on PATH)
- git
- Python 3.10+

### 1.4 Usage

```bash
cd Version_Alpha

# Interactive Gruvbox wizard (project name, database, API style, ...)
python3 generate_project.py

# Scriptable CLI
python3 generate_project.py MyNewProject
python3 generate_project.py MyNewProject --database sqlserver
python3 generate_project.py MyNewProject --api-style minimal
python3 generate_project.py MyNewProject --framework net10.0
python3 generate_project.py MyNewProject --dir /path/to/output
python3 generate_project.py MyNewProject --no-validate      # skip restore/build/test
python3 generate_project.py MyNewProject --no-git           # skip git init + commits
python3 generate_project.py MyNewProject --force            # recreate a non-empty --dir
python3 generate_project.py                                 # interactive wizard
```

| Option | Description |
| --- | --- |
| `--database X` | `postgres` (default) or `sqlserver` |
| `--db-password PASS` | SQL Server SA password (default: random; stored in `docker/.env`, gitignored, printed once) |
| `--dir DIR` | Output directory (default: `<Name>` in the current directory) |
| `--framework X` | `net<major>.<minor>`, minimum `net10.0` (default: `net10.0`) |
| `--api-style X` | `controllers` (default) or `minimal` |
| `--no-validate` | Skip `dotnet restore/build/test` |
| `--no-git` | Skip `git init` and the three initial commits |
| `--include-agent-runs` | Also copy `docs/agent-runs/` historical records |
| `--force` | Delete and recreate the output directory if not empty |
| `--wizard`, `-w` | Force the interactive wizard |

Project names are normalized to PascalCase from most separators
(`My-App`, `my app` → `MyApp`); reserved C# keywords are rejected.

### 1.5 Verified status and known issues

Ran here:

```bash
python3 generate_project.py DocCheckTest --dir /tmp/opencode/DocCheckTest --no-validate --no-git
```

The generator scaffolded `DocCheckTest.sln`, all projects, references, docs,
`.opencode/` and docker files correctly (all `dotnet add` steps reported
`-> OK`), but generation died at the final NuGet step:

```text
> dotnet add .../DocCheckTest.Api.Tests/DocCheckTest.Api.Tests.csproj package Microsoft.AspNetCore.Mvc.Testing
  -> FAILED
error: NU1202: Package Microsoft.AspNetCore.Mvc.Testing 11.0.0 is not compatible with net10.0
       (.NETCoreApp,Version=v10.0). Package Microsoft.AspNetCore.Mvc.Testing 11.0.0
       supports: net11.0 (.NETCoreApp,Version=v11.0)
```

This is a "latest package ahead of the TFM" incompatibility, not a logic
bug in the scaffolder: `dotnet add package` with no version resolves the
latest stable (11.0.0, net11.0-only) for a `net10.0` project. A project built
with `net11.0` should hit no issue, and pinning the package to a `net10.0`-
compatible version (e.g. `dotnet add ... package Microsoft.AspNetCore.Mvc.Testing
--version <net10-compatible>`) should also make it generate successfully.

Other known issues (from reading the source):

- Architecture tests use `NetArchTest.Rules` and the test assembly references
  all four source projects to inspect dependency edges.
- Generation normally requires network access to NuGet.org.

### 1.6 After generation

```bash
cd <Name>
dotnet build
dotnet test
dotnet test tests/<Name>.Architecture.Tests/<Name>.Architecture.Tests.csproj
dotnet format --verify-no-changes
cat src/<Name>.Api/appsettings.json   # inspect the generated connection string
```

Then open the project in OpenCode and start the TDP workflow with
`/feature "short description"`. Read `AGENTS.md` and
`docs/guides/agent-usage.md` first.

---

## 2. Version_0.0-1 — the unfinished port

An attempt to re-implement the Version_Alpha generator as a self-contained
Bash tool. **It does not currently generate a working project.** This section
documents how it is intended to work, its actual status, and how to use it if
you provide a source repository.

### 2.1 Layout

```text
Version_0.0-1/
  create-project.sh                  # entry point -> tools/project-generator/lib/generate.sh
  tools/project-generator/
    lib/
      common.sh      # logging, templates rendering, REUSABLE_ROOT resolution, cleanup
      validate.sh    # arguments, project-name validation, and prepare_destination
      scaffold.sh    # solution/projects, git init, render root configuration
      opencode.sh    # copy .opencode/agents and .opencode/commands from source
      docs.sh        # copy docs/architecture, docs/workflows and guides
      finalize.sh    # structural verification, validation, initial commit, report
      generate.sh    # main(): orchestrates steps 1-5
    templates/       # {{PROJECT_NAME}}-tokenized content
      root/          # README.md, AGENTS.md for the generated project
      docs/          # specs guide, agents README, specifications reference
      src/           # Domain, Security, Application, Infrastructure, Api skeletons
    config/
      opencode-exclude.txt  # excludable agents/commands (default: nothing excluded)
```

### 2.2 Intended flow (`generate.sh`)

1. Parse arguments; if the name is missing, prompt (interactive TTY only).
2. Verify prerequisites: `dotnet` (≥ TFM major), `git`, base POSIX commands.
3. Prepare the destination: `<output>/<Name>` (default output root =
   parent of the generator's source repository). The destination is never
   overwritten; generation fails instead.
4. Step 1 — create the directory, `git init` on branch `develop`, render
   root config (`.editorconfig`, `.gitignore`, `docker-compose.yml`,
   `README.md`, `AGENTS.md`).
5. Step 2 — copy source and test projects from `templates/`, render all
   tokens, create the `.sln`, add all projects to it.
6. Step 3 — copy `.opencode/agents` and `.opencode/commands` from the
   reusable source (excluding `config/opencode-exclude.txt`), and copy
   `docs/architecture`, `docs/workflows`, `docs/agents/agents-list.md`,
   `docs/guides/agent-usage.md`, `docs/README.md`, `docs/agent-runs/README.md`.
7. Step 4 — write `docs/specifications/000-spec-example.md`.
8. Step 5 — verify the generated tree, then (optionally) validate:
   `dotnet build`, `dotnet test`, `dotnet format --verify-no-changes`.
   If git is enabled, an initial commit `chore: bootstrap <Name> from the
   project generator` is created on `develop`.

### 2.3 Command-line interface

```bash
cd Version_0.0-1
./create-project.sh [OPTIONS] [PROJECT_NAME]

  -n, --name NAME        Project name (PascalCase: MyProject)
  -o, --output DIR       Parent directory for the project (default: see below)
  --source DIR           Reusable assets to copy (overrides live repo/snapshot)
  --no-git               Skip git init/commit
  --skip-validation      Skip build/test/format (structure is still verified)
  -h, --help             Show help
  --version              Show generator version (1.0.0)
```

Environment variables: `GENERATOR_TFM` (default `net10.0`),
`GENERATOR_OUTPUT_ROOT`, `GENERATOR_SOURCE_ROOT`, `KEEP_PARTIAL=1` (keep a
half-generated directory for inspection), `KEEP_PARTIAL=0` (default: remove it
on failure), `NO_COLOR=1`.

Default output root: the parent of the generator's source repository
(`IN_PLACE=1`), otherwise the current working directory — or, when invoked
inside a guarded source tree, the parent of the guard root. Project names must
match `^[A-Z][A-Za-z0-9]*$` (≤ 100 chars; reserved device names rejected).

### 2.4 The reusable-assets model (why it fails here)

The generator does not synthesize `.opencode/`, `docs/architecture/`,
`.editorconfig`, `docker-compose.yml` or `.gitignore` from nothing. It copies
them from a **reusable source**, resolved by `resolve_reusable_root()` in
`common.sh`, with this precedence:

1. `--source DIR` / `GENERATOR_SOURCE_ROOT` — an explicit source tree; or
2. the live source repository, when the generator runs in place
   (`IN_PLACE=1`), i.e. `<repo>/tools/project-generator` is itself part of a
   repository with `.git`, `.opencode/`, `docs/architecture/`, etc.; or
3. a bundled snapshot at `tools/project-generator/snapshot/`, created by
   `tools/project-generator/sync-snapshot.sh` from the source repository.

The snapshot does **not** exist in this checkout, and the reusable assets are
present in neither (`.git` exists only at the workspace root, which is not
`IN_PLACE` because the generator lives under `Version_0.0-1/tools/project-generator`,
not `<repo>/tools/project-generator`).

### 2.5 Verified status — do not ship it yet

Verified by running `./create-project.sh --name TestProject --output /tmp/opencode --skip-validation`:

```text
[1/5] Preparing project structure...
✔ Initialized git repository on branch 'develop'.
tools/project-generator/lib/scaffold.sh: line 24: copy_repo_file_rendered: command not found
```

Concrete defects in this checkout:

1. **`copy_repo_file_rendered` and `copy_repo_directory_rendered` are called but
   never defined** (`lib/scaffold.sh`, `lib/opencode.sh`, `lib/docs.sh`).
   Nothing can pass step 1. [blocking]
2. **`REUSABLE_ROOT` is never populated for the in-place case.** It is only
   set when `--source` is passed (`lib/validate.sh`, `parse_arguments`).
   `resolve_reusable_root()` is implemented but **never called**; there is no
   call site anywhere in `lib/`. [blocking]
3. **`check_reusable_assets()` is implemented but never called.** It is
   meant to fail early with the list above (agents, commands, docs,
   `.editorconfig`, `.gitignore`, `docker-compose.yml`) when the source is
   absent. [usability]
4. **`PROTECTED_ROOT` was undefined** in `prepare_destination()`
   (`lib/validate.sh`) and exploded with
   `PROTECTED_ROOT: unbound variable`. Fixed to use `tree_root_for_guard()`
   (the same value `default_output_root()` uses). [fixed]
   - Note: `$(tree_root_for_guard)` is then used in the error message; it
     respects the `IN_PLACE` guard above.
5. **`templates/tests/` does not exist.** `scaffold.sh` copies
   `templates/tests` unconditionally, so even with a source provided the
   copy would die with `Template directory not found`. The final
   verification (`finalize.sh` §`verify_generated_project`) also requires
   `tests/<Name>.Domain.Tests/EntityIdTests.cs`,
   `tests/<Name>.TestSupport/SqliteDatabase.cs` and
   `tests/<Name>.Architecture.Tests/ArchitectureTests.cs` — test templates
   that simply are not in this tree. [blocking for verification]
6. The generator tree is not `IN_PLACE` in this workspace (see 2.4),
   so even an in-place run falls back to an empty `REUSABLE_ROOT`.
   `docs.sh` also expects the source to contain `docs/agents/agents-list.md`,
   which this checkout does not provide for itself. [environment-specific]
7. `render_string()` rewrites `PostgreSQL` → `SQL Server` inside every text
   file. A generated project therefore always targets SQL Server — even if
   the source uses PostgreSQL. [design caveat, by design]

**Bottom line.** Version_0.0-1 is an incomplete re-implementation. It can be
made to work only if (a) the missing functions are implemented, (b) the
`REUSABLE_ROOT` resolution is wired, (c) the missing `templates/tests` are
added, and (d) you supply a source repository containing `.opencode/`,
`docs/architecture/`, `docs/workflows/`, `docs/agents/agents-list.md`,
`.editorconfig`, `.gitignore` and `docker-compose.yml` (or bundle a
`snapshot/`). Version_Alpha (§1) is the more complete generator, but note the
`net10.0` package-compatibility caveat in §1.5.

### 2.6 Using Version_0.0-1 with a source repository

If you have (or are reconstructing) the source repository, the invocation
looks like:

```bash
# Source tree must contain: .opencode/agents, .opencode/commands,
# docs/architecture, docs/workflows/tdp-feature-workflow.md,
# docs/agents/agents-list.md, .editorconfig, .gitignore, docker-compose.yml
cd Version_0.0-1
./create-project.sh --source /path/to/source-repo --output /path/to/out MyNewProject

# Keep the half-generated tree for inspection:
KEEP_PARTIAL=1 ./create-project.sh --source /path/to/source-repo MyNewProject
```

Even then it will stop at step 2 until the missing functions and test
templates are added (see 2.5). Passing `--skip-validation` does not help —
the failure happens earlier, during scaffolding.

### 2.7 Troubleshooting

- `copy_repo_file_rendered: command not found` → see 2.5 (1).
- `Reusable assets are missing: ...` → `--source` must point at a complete
  source repository, or run inside the source repository, or create
  `tools/project-generator/snapshot/` (`sync-snapshot.sh`, absent here).
- `Destination already exists` → the generator never overwrites; delete the
  directory or choose another `--output`.
- `The .NET SDK ... is N` → install the SDK matching `GENERATOR_TFM`
  (e.g. net10.0) or set `GENERATOR_TFM` appropriately.
- Colors interfere with logs → `NO_COLOR=1`.

---

## 3. Which one should I use?

| Need | Recommended |
| --- | --- |
| Generate a project and validate it yourself | `Version_Alpha/generate_project.py` (mind the `net10.0` package caveat in §1.5 — pin `Microsoft.AspNetCore.Mvc.Testing` to a net10.0-compatible version) |
| Understand the bash port / contribute to it | Read §2, `lib/*.sh` above |
| Extend generation behaviour | Patch `Version_Alpha` — it is the maintained path |
| CI/automation | `python3 generate_project.py <Name> --dir out --no-git --no-validate` then validate yourself with an explicit NuGet version of `Microsoft.AspNetCore.Mvc.Testing` |
