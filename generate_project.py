#!/usr/bin/env python3
"""
generate_project.py - Generates a .NET 10 Clean Architecture project scaffold
with agentic development tooling (TDP workflow, specialized agents and OpenCode
commands), based on the Matchly experiment.

Usage:
    python3 generate_project.py <ProjectName> [--dir <output>] [--no-validate]
                                [--no-git] [--include-agent-runs] [--force]
                                [--framework net10.0]

The generated project substitutes every occurrence of "Matchly"/"matchly" with
the provided project name (PascalCase and lowercase forms).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"
HELP_DOCS_DIR = SCRIPT_DIR / "HelpDocuments"

FRAMEWORK = "net10.0"
OPENAPI_PACKAGE_VERSION = "10.0.10"

C_SHARP_KEYWORDS = {
    "abstract", "as", "base", "bool", "break", "byte", "case", "catch",
    "char", "checked", "class", "const", "continue", "decimal", "default",
    "delegate", "do", "double", "else", "enum", "event", "explicit", "extern",
    "false", "finally", "fixed", "float", "for", "foreach", "goto", "if",
    "implicit", "in", "int", "interface", "internal", "is", "lock", "long",
    "namespace", "new", "null", "object", "operator", "out", "override",
    "params", "private", "protected", "public", "readonly", "ref", "return",
    "sbyte", "sealed", "short", "sizeof", "stackalloc", "static", "string",
    "struct", "switch", "this", "throw", "true", "try", "typeof", "uint",
    "ulong", "unchecked", "unsafe", "ushort", "using", "virtual", "void",
    "volatile", "while",
}

AGENTS = [
    {
        "name": "orchestrator",
        "source": "orchestrator.md",
        "mode": "all",
        "description": "Coordinates the autonomous TDP development workflow, enforces Clean Architecture and GitFlow, and controls agent transitions.",
        "edit": {"*": "deny"},
        "bash": True,
        "task": True,
    },
    {
        "name": "specification",
        "source": "specification-agent.md",
        "mode": "subagent",
        "description": "Transforms feature requests into precise, testable feature specifications (source of truth).",
        "edit": {"docs/specifications/**": "allow", "docs/agent-runs/**": "allow", "*": "deny"},
        "bash": False,
        "task": False,
    },
    {
        "name": "test",
        "source": "test-agent.md",
        "mode": "subagent",
        "description": "Translates acceptance criteria into executable tests and establishes the RED state.",
        "edit": {"tests/**": "allow", "docs/agent-runs/**": "allow", "*": "deny"},
        "bash": True,
        "task": False,
    },
    {
        "name": "implementation",
        "source": "implementation-agent.md",
        "mode": "subagent",
        "description": "Implements the minimum production code required to turn RED into GREEN.",
        "edit": {"src/**": "allow", "docs/agent-runs/**": "allow", "*": "deny"},
        "bash": True,
        "task": False,
    },
    {
        "name": "refactor",
        "source": "refactor-agent.md",
        "mode": "subagent",
        "description": "Reviews and refactors the implementation without changing observable behavior.",
        "edit": {"src/**": "allow", "docs/agent-runs/**": "allow", "*": "deny"},
        "bash": True,
        "task": False,
    },
    {
        "name": "architecture",
        "source": "architecture-agent.md",
        "mode": "subagent",
        "description": "Validates that the implementation respects Clean Architecture rules.",
        "edit": {"docs/agent-runs/**": "allow", "*": "deny"},
        "bash": True,
        "task": False,
    },
    {
        "name": "validation",
        "source": "validation-agent.md",
        "mode": "subagent",
        "description": "Final quality gate: build, tests, architecture tests and scope validation.",
        "edit": {"docs/agent-runs/**": "allow", "*": "deny"},
        "bash": True,
        "task": False,
    },
    {
        "name": "release",
        "source": "release-agent.md",
        "mode": "subagent",
        "description": "Prepares and executes controlled GitFlow releases from develop to main.",
        "edit": {"*": "deny"},
        "bash": True,
        "task": False,
    },
]

COMMANDS = [
    {
        "name": "feature",
        "agent": "orchestrator",
        "description": "Run the full TDP feature workflow (specification -> tests -> implementation -> refactor -> architecture -> validation, max 3 attempts).",
        "body": """Run the full agentic feature development workflow for: $ARGUMENTS

Read @AGENTS.md and @docs/workflows/tdp-feature-workflow.md.

Execute the stages in order, delegating to the specialized subagents via the task tool:

1. PLAN - delegate to the `specification` agent to create or validate the feature specification at docs/specifications/<feature>.md.
2. TESTS - delegate to the `test` agent to translate the acceptance criteria into executable tests and establish a valid RED state.
3. IMPLEMENT - delegate to the `implementation` agent to achieve GREEN with the minimum production code.
4. REFACTOR - delegate to the `refactor` agent to evaluate and apply justified refactoring.
5. ARCHITECTURE - delegate to the `architecture` agent to validate Clean Architecture rules.
6. VALIDATE - delegate to the `validation` agent to run the final quality gate (build, tests, architecture tests, git scope).

Loop control (MANDATORY):
- Maximum implementation attempts: 3 (the initial attempt counts as attempt 1).
- After a FAIL, route the feature back to the responsible agent and re-run validation.
- The loop is bounded by the workflow, not by the model. Track the attempt count explicitly and STOP after 3 failed attempts.

Final report:
- Feature, branch, specification used, agents executed, tests created, files changed, refactoring, validation results, attempt count, remaining issues and final status (FEATURE COMPLETE / FAILED).
""",
    },
    {
        "name": "plan",
        "agent": "specification",
        "description": "Create or validate a feature specification following the TDP workflow.",
        "body": """Create or validate the feature specification for: $ARGUMENTS

Read @AGENTS.md and @docs/workflows/tdp-feature-workflow.md.

If a specification already exists in docs/specifications/, validate it against the workflow requirements and the structure defined in @docs/agents/specification-agent.md.

Otherwise create docs/specifications/<feature-id>-<short-name>.md with:

- Objective
- Context
- Business Rules
- Acceptance Criteria
- Constraints
- Out of Scope
- TDD

Do not implement production code.

Return SPECIFICATION READY (with the file path) or SPECIFICATION BLOCKED (with the exact decision required).
""",
    },
    {
        "name": "tests",
        "agent": "test",
        "description": "Translate a feature specification into executable tests and establish RED.",
        "body": """Create the tests for the feature: $ARGUMENTS

Read @AGENTS.md, @docs/workflows/tdp-feature-workflow.md and the feature specification at docs/specifications/$ARGUMENTS.md.

Translate every acceptance criterion into executable tests in the appropriate test project:

- tests/{{ProjectName}}.Domain.Tests
- tests/{{ProjectName}}.Application.Tests
- tests/{{ProjectName}}.Infrastructure.Tests
- tests/{{ProjectName}}.Architecture.Tests

Rules:
- Do not modify production code (src/**).
- Do not weaken, skip or remove existing tests.
- Execute the relevant test project and confirm the new tests fail for the expected missing behavior (valid RED).

Return RED READY with the tests created, the acceptance criteria mapping and the RED evidence.
""",
    },
    {
        "name": "implement",
        "agent": "implementation",
        "description": "Implement the minimum production code to turn RED into GREEN.",
        "body": """Implement the feature: $ARGUMENTS

Read @AGENTS.md, @docs/workflows/tdp-feature-workflow.md, the feature specification and the RED tests.

Implement the minimum production code required to satisfy the specification and make the tests pass.

Rules:
- Do not modify tests.
- Follow Clean Architecture and Clean Code.
- Do not add speculative abstractions, persistence, API endpoints or unrelated functionality.
- Run the affected tests, then the full suite, then the build.

Return STATUS: PASS/FAIL/BLOCKED with the changes, tests executed and validation results.
""",
    },
    {
        "name": "refactor",
        "agent": "refactor",
        "description": "Review and refactor the implementation without changing behavior.",
        "body": """Refactor the feature implementation if justified: $ARGUMENTS

Read @AGENTS.md, the feature specification and the current implementation.

Evaluate naming, structure, duplication, cohesion, coupling, readability and simplicity. Refactor ONLY when there is concrete value.

Rules:
- Do not change observable behavior.
- Do not introduce speculative abstractions.
- Do not modify tests.
- Run the full test suite after any meaningful refactor.
- "No refactor required" is a valid result.

Return REFACTORED or NO_REFACTOR_REQUIRED with validation results.
""",
    },
    {
        "name": "architecture",
        "agent": "architecture",
        "description": "Validate that the implementation respects Clean Architecture rules.",
        "body": """Validate the architecture of the current feature implementation: $ARGUMENTS

Read @AGENTS.md, the feature specification, the changed files and @docs/architecture/architecture.md.

Verify:
- Domain has no dependency on Application, Infrastructure, API, ASP.NET Core, EF Core or PostgreSQL.
- Application depends only on Domain.
- Infrastructure depends only on Application and Domain.
- API depends only on Application and contains no business rules.
- Architecture tests pass:

  dotnet test tests/{{ProjectName}}.Architecture.Tests/{{ProjectName}}.Architecture.Tests.csproj

Return PASS or FAIL (with violation, location, rule, evidence and required correction). Do not fix violations yourself.
""",
    },
    {
        "name": "validate",
        "agent": "validation",
        "description": "Run the final validation gate for a feature.",
        "body": """Run the final validation for the feature: $ARGUMENTS

Execute and observe:

- dotnet build
- dotnet test
- dotnet test tests/{{ProjectName}}.Architecture.Tests/{{ProjectName}}.Architecture.Tests.csproj
- git status / git diff (scope check)

Verify the specification exists, tests exist and pass, the build passes, architecture tests pass, no unrelated files changed and no secrets were introduced.

Do not modify code or tests.

Return PASS or FAIL with objective evidence. Never claim a command passed without executing it.
""",
    },
]


class ScriptError(Exception):
    pass


def log(message: str) -> None:
    print(message)


def run(cmd: list, cwd: Path | None = None) -> subprocess.CompletedProcess:
    printable = " ".join(cmd)
    log(f"\n> {printable}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        tail = (result.stdout or "")[-2000:]
        tail += (result.stderr or "")[-2000:]
        log("  -> FAILED")
        log(tail.strip())
        raise ScriptError(f"command failed: {printable}")
    log("  -> OK")
    return result


def run_soft(cmd: list, cwd: Path | None = None) -> subprocess.CompletedProcess:
    printable = " ".join(cmd)
    log(f"\n> {printable}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    log(f"  -> exit code {result.returncode}")
    return result


def normalize_name(raw: str) -> tuple[str, str]:
    name = raw.strip()
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", name) if p]
    if not parts:
        raise ValueError(f"'{raw}' is not a valid project name.")
    pascal = "".join(p[0].upper() + p[1:] for p in parts)
    if not re.match(r"^[A-Za-z][A-Za-z0-9]*$", pascal):
        raise ValueError(f"'{raw}' is not a valid C# project name.")
    if pascal.lower() in C_SHARP_KEYWORDS:
        raise ValueError(f"'{pascal}' is a reserved C# keyword.")
    return pascal, pascal.lower()


def yaml_scalar(value: str) -> str:
    return json.dumps(value)


def substitute(text: str, pascal: str, lower: str) -> str:
    text = text.replace("Matchly", pascal)
    text = text.replace("matchly", lower)
    return text


def substitute_template(text: str, pascal: str, lower: str) -> str:
    return (
        text.replace("{{ProjectName}}", pascal)
        .replace("{{ProjectNameLower}}", lower)
    )


def renamed_path(path: Path, pascal: str, lower: str) -> Path:
    name = path.name
    renamed = substitute(name, pascal, lower)
    if renamed != name:
        return path.parent / renamed
    return path


def copy_tree(source: Path, target: Path, pascal: str, lower: str) -> None:
    if not source.exists():
        return
    for item in sorted(source.rglob("*")):
        rel = item.relative_to(source)
        dest = target / substitute(str(rel), pascal, lower)
        if item.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            content = item.read_text(encoding="utf-8", errors="replace")
            dest.write_text(substitute(content, pascal, lower), encoding="utf-8")


class Generator:
    def __init__(
        self,
        name: str,
        out_dir: Path,
        framework: str,
        include_agent_runs: bool,
        do_validate: bool,
        do_git: bool,
    ) -> None:
        self.pascal, self.lower = normalize_name(name)
        self.out = out_dir
        self.framework = framework
        self.include_agent_runs = include_agent_runs
        self.do_validate = do_validate
        self.do_git = do_git
        self.sln = self.out / f"{self.pascal}.sln"
        self.src = self.out / "src"
        self.tests = self.out / "tests"
        self.layers = ("Domain", "Application", "Infrastructure", "Api")
        self.test_layers = (
            "Domain.Tests",
            "Application.Tests",
            "Infrastructure.Tests",
            "Architecture.Tests",
        )
        self.validation_ok = False

    # ------------------------------------------------------------------ paths
    def proj(self, name: str) -> Path:
        return self.out / name

    def src_proj(self, layer: str) -> Path:
        return self.src / f"{self.pascal}.{layer}"

    def test_proj(self, layer: str) -> Path:
        return self.tests / f"{self.pascal}.{layer}"

    # ------------------------------------------------------------------ setup
    def prepare_directory(self, force: bool) -> None:
        if self.out.exists() and any(self.out.iterdir()):
            if not force:
                raise ScriptError(
                    f"Output directory '{self.out}' is not empty. "
                    "Use --force to delete it and regenerate."
                )
            log(f"Deleting existing directory: {self.out}")
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True, exist_ok=True)

    def check_tools(self) -> None:
        if shutil.which("dotnet") is None:
            raise ScriptError("dotnet SDK not found on PATH.")
        if shutil.which("git") is None:
            raise ScriptError("git not found on PATH.")
        result = subprocess.run(
            ["dotnet", "--version"], capture_output=True, text=True
        )
        if result.returncode != 0:
            raise ScriptError("Could not determine the dotnet SDK version.")
        log(f"Using dotnet SDK {result.stdout.strip()}")

    # -------------------------------------------------------------- scaffolding
    def scaffold(self) -> None:
        log("\n=== Scaffolding projects ===")
        run(["dotnet", "new", "sln", "-n", self.pascal, "-o", str(self.out), "--format", "sln"])

        for layer in self.layers:
            if layer == "Api":
                run([
                    "dotnet", "new", "web", "-n", f"{self.pascal}.Api",
                    "-o", str(self.src_proj("Api")),
                    "--framework", self.framework, "--no-restore",
                ])
            else:
                run([
                    "dotnet", "new", "classlib", "-n", f"{self.pascal}.{layer}",
                    "-o", str(self.src_proj(layer)),
                    "--framework", self.framework, "--no-restore",
                ])

        for layer in self.test_layers:
            run([
                "dotnet", "new", "xunit", "-n", f"{self.pascal}.{layer}",
                "-o", str(self.test_proj(layer)),
                "--framework", self.framework, "--no-restore",
            ])

        projects = [
            self.src_proj(layer) / f"{self.pascal}.{layer}.csproj" for layer in self.layers
        ] + [
            self.test_proj(layer) / f"{self.pascal}.{layer}.csproj" for layer in self.test_layers
        ]
        run(["dotnet", "sln", str(self.sln), "add", *[str(p) for p in projects]])

        log("\n=== Removing template placeholder files ===")
        for layer in self.layers:
            if layer == "Api":
                continue
            placeholder = self.src_proj(layer) / "Class1.cs"
            if placeholder.exists():
                placeholder.unlink()
        for layer in self.test_layers:
            placeholder = self.test_proj(layer) / "UnitTest1.cs"
            if placeholder.exists():
                placeholder.unlink()

    def configure_projects(self) -> None:
        log("\n=== Adding project references ===")
        app = self.src_proj("Application")
        inf = self.src_proj("Infrastructure")
        api = self.src_proj("Api")
        domain = self.src_proj("Domain")

        run(["dotnet", "add", str(app / f"{self.pascal}.Application.csproj"), "reference", str(domain / f"{self.pascal}.Domain.csproj")])
        run(["dotnet", "add", str(inf / f"{self.pascal}.Infrastructure.csproj"), "reference", str(domain / f"{self.pascal}.Domain.csproj")])
        run(["dotnet", "add", str(inf / f"{self.pascal}.Infrastructure.csproj"), "reference", str(app / f"{self.pascal}.Application.csproj")])
        run(["dotnet", "add", str(api / f"{self.pascal}.Api.csproj"), "reference", str(app / f"{self.pascal}.Application.csproj")])

        src_refs = {
            "Domain.Tests": ["Domain"],
            "Application.Tests": ["Application"],
            "Infrastructure.Tests": ["Infrastructure"],
            "Architecture.Tests": ["Domain", "Application", "Infrastructure", "Api"],
        }
        for test_layer, ref_layers in src_refs.items():
            test_proj_file = self.test_proj(test_layer) / f"{self.pascal}.{test_layer}.csproj"
            for ref_layer in ref_layers:
                ref_file = self.src_proj(ref_layer) / f"{self.pascal}.{ref_layer}.csproj"
                run(["dotnet", "add", str(test_proj_file), "reference", str(ref_file)])

        log("\n=== Adding NuGet packages ===")
        api_proj = api / f"{self.pascal}.Api.csproj"
        run([
            "dotnet", "add", str(api_proj), "package",
            "Microsoft.AspNetCore.OpenApi", "--version", OPENAPI_PACKAGE_VERSION,
        ])
        arch_proj = self.test_proj("Architecture.Tests") / f"{self.pascal}.Architecture.Tests.csproj"
        run(["dotnet", "add", str(arch_proj), "package", "NetArchTest.Rules"])
        for test_layer in self.test_layers:
            test_proj_file = self.test_proj(test_layer) / f"{self.pascal}.{test_layer}.csproj"
            run(["dotnet", "add", str(test_proj_file), "package", "FluentAssertions"])

    def write_custom_files(self) -> None:
        log("\n=== Writing custom source files ===")
        for layer in ("Domain", "Application", "Infrastructure"):
            marker = self.src_proj(layer) / "AssemblyMarker.cs"
            content = (
                TEMPLATES_DIR / "code" / "AssemblyMarker.cs"
            ).read_text(encoding="utf-8")
            content = (
                content.replace("{{ProjectName}}", self.pascal)
                .replace("{{Layer}}", layer)
            )
            marker.write_text(content, encoding="utf-8")

        program = self.src_proj("Api") / "Program.cs"
        program.write_text(
            substitute_template(
                (TEMPLATES_DIR / "code" / "Program.cs").read_text(encoding="utf-8"),
                self.pascal, self.lower,
            ),
            encoding="utf-8",
        )

        arch_test = self.test_proj("Architecture.Tests") / "ArchitectureTests.cs"
        arch_test.write_text(
            substitute_template(
                (TEMPLATES_DIR / "code" / "ArchitectureTests.cs").read_text(encoding="utf-8"),
                self.pascal, self.lower,
            ),
            encoding="utf-8",
        )

        smoke_template = (TEMPLATES_DIR / "code" / "SmokeTests.cs").read_text(encoding="utf-8")
        for test_layer, ref_layer in (
            ("Domain.Tests", "Domain"),
            ("Application.Tests", "Application"),
            ("Infrastructure.Tests", "Infrastructure"),
        ):
            content = (
                smoke_template.replace("{{ProjectName}}", self.pascal)
                .replace("{{Layer}}", ref_layer)
                .replace("{{TestLayer}}", test_layer)
            )
            (self.test_proj(test_layer) / "SmokeTests.cs").write_text(content, encoding="utf-8")

    def copy_docs(self) -> None:
        log("\n=== Copying documentation ===")
        docs_src = HELP_DOCS_DIR / "docs"
        docs_dst = self.out / "docs"

        excludes = {"agent-runs"} if not self.include_agent_runs else set()
        for item in sorted(docs_src.rglob("*")):
            rel = item.relative_to(docs_src)
            if rel.parts[0] in excludes:
                continue
            dest = docs_dst / substitute(str(rel), self.pascal, self.lower)
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(
                    substitute(item.read_text(encoding="utf-8", errors="replace"), self.pascal, self.lower),
                    encoding="utf-8",
                )

        agents_md = (HELP_DOCS_DIR / "AGENTS.md").read_text(encoding="utf-8")
        (self.out / "AGENTS.md").write_text(substitute(agents_md, self.pascal, self.lower), encoding="utf-8")

        readme = (HELP_DOCS_DIR / "README.md").read_text(encoding="utf-8")
        (self.out / "README.md").write_text(substitute(readme, self.pascal, self.lower), encoding="utf-8")

        docker = (TEMPLATES_DIR / "docker-compose.yml").read_text(encoding="utf-8")
        (self.out / "docker-compose.yml").write_text(
            substitute_template(docker, self.pascal, self.lower), encoding="utf-8"
        )

        gitignore = (TEMPLATES_DIR / ".gitignore").read_text(encoding="utf-8")
        (self.out / ".gitignore").write_text(gitignore, encoding="utf-8")

    def generate_opencode(self) -> None:
        log("\n=== Generating .opencode agents and commands ===")
        agents_dir = self.out / ".opencode" / "agents"
        commands_dir = self.out / ".opencode" / "commands"
        agents_dir.mkdir(parents=True, exist_ok=True)
        commands_dir.mkdir(parents=True, exist_ok=True)

        for agent in AGENTS:
            source = HELP_DOCS_DIR / "docs" / "agents" / agent["source"]
            body = source.read_text(encoding="utf-8").strip()
            body = substitute(body, self.pascal, self.lower)

            frontmatter = [
                "---",
                f"description: {yaml_scalar(agent['description'])}",
                f"mode: {agent['mode']}",
                "permission:",
                "  read: allow",
                "  edit:",
            ]
            for pattern, action in agent["edit"].items():
                frontmatter.append(f'    "{pattern}": {action}')
            frontmatter.append(f"  bash: {'allow' if agent['bash'] else 'deny'}")
            if agent.get("task") is not None:
                frontmatter.append(f"  task: {'allow' if agent['task'] else 'deny'}")
            frontmatter.append("---")

            content = "\n".join(frontmatter) + "\n\n" + body + "\n"
            (agents_dir / f"{agent['name']}.md").write_text(content, encoding="utf-8")

        for command in COMMANDS:
            body = substitute_template(command["body"], self.pascal, self.lower)
            content = (
                "---\n"
                f"description: {yaml_scalar(command['description'])}\n"
                f"agent: {command['agent']}\n"
                "---\n\n"
                f"{body.strip()}\n"
            )
            (commands_dir / f"{command['name']}.md").write_text(content, encoding="utf-8")

    # -------------------------------------------------------------- validation
    def validate(self) -> bool:
        log("\n=== Validation ===")
        steps = [
            (["dotnet", "restore", str(self.sln)], "Restore"),
            (["dotnet", "build", str(self.sln), "--no-restore"], "Build"),
            (["dotnet", "test", str(self.sln), "--no-restore", "--no-build"], "Tests"),
        ]
        all_ok = True
        for cmd, label in steps:
            result = run_soft(cmd, cwd=self.out)
            if result.returncode != 0:
                all_ok = False
                log(f"  {label}: FAILED")
            else:
                log(f"  {label}: PASS")
        self.validation_ok = all_ok
        return all_ok

    # ------------------------------------------------------------------- git
    def git_init(self) -> None:
        log("\n=== Initializing git repository ===")
        run(["git", "init", "-b", "main"], cwd=self.out)

        def stage(paths: list[str]) -> None:
            run(["git", "add", "--", *paths], cwd=self.out)

        def commit(message: str) -> None:
            result = run_soft(["git", "commit", "-m", message], cwd=self.out)
            if result.returncode != 0:
                log(
                    "  Git commit failed. This usually means git user.name/user.email "
                    "are not configured. Configure them and commit manually."
                )
                raise ScriptError(
                    "Git commit failed (check git user.name/user.email configuration)."
                )
            log(f"  committed: {message}")

        test_dirs = [f"tests/{self.pascal}.{layer}" for layer in
                     ("Domain.Tests", "Application.Tests", "Infrastructure.Tests")]

        stage([
            ".gitignore",
            "docker-compose.yml",
            "README.md",
            f"{self.pascal}.sln",
            "src",
            *test_dirs,
        ])
        commit(f"chore: initialize {self.pascal} project")

        stage([f"tests/{self.pascal}.Architecture.Tests", "docs/architecture"])
        commit("test: enforce clean architecture boundaries")

        stage(["AGENTS.md", "docs", ".opencode"])
        commit("docs: define agent development contract")

    # ----------------------------------------------------------------- report
    def verify_no_leftovers(self) -> list:
        issues = []
        skip_names = {"obj", "bin", ".git", "__pycache__"}
        for f in self.out.rglob("*"):
            if f.is_file() and not any(part in skip_names for part in f.parts):
                if f.suffix in {".md", ".cs", ".csproj", ".yml", ".yaml", ".json", ".sln", ".txt"}:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    if self.pascal != "Matchly" and "Matchly" in text:
                        issues.append((f, "Matchly"))
                    if self.lower != "matchly" and "matchly" in text:
                        issues.append((f, "matchly"))
        return issues

    def print_tree(self) -> None:
        skip_names = {"obj", "bin", ".git", "__pycache__"}
        log("\n=== Generated structure ===")
        log(str(self.out) + "/")

        def walk(path: Path, prefix: str) -> None:
            entries = [e for e in sorted(path.iterdir()) if e.name not in skip_names]
            for index, entry in enumerate(entries):
                last = index == len(entries) - 1
                connector = "`-- " if last else "|-- "
                if entry.is_dir():
                    log(f"{prefix}{connector}{entry.name}/")
                    walk(entry, prefix + ("    " if last else "|   "))
                else:
                    log(f"{prefix}{connector}{entry.name}")

        for entry in sorted(self.out.iterdir()):
            if entry.name in skip_names:
                continue
            if entry.is_dir():
                log(f"|-- {entry.name}/")
                walk(entry, "|   ")
            else:
                log(f"|-- {entry.name}")

    def report(self) -> None:
        log("\n" + "=" * 60)
        log("GENERATION REPORT")
        log("=" * 60)
        log(f"Project:      {self.pascal}")
        log(f"Namespace:    {self.pascal}")
        log(f"Directory:    {self.out}")
        log(f"Framework:    {self.framework}")
        log(f"Validation:   {'PASS' if self.validation_ok else 'NOT RUN / FAILED'}")
        leftovers = self.verify_no_leftovers()
        log(f"Name sweep:   {'CLEAN' if not leftovers else f'{len(leftovers)} leftover reference(s)'}")
        for path, token in leftovers:
            log(f"  - {path.relative_to(self.out)} contains '{token}'")
        log("=" * 60)
        if self.validation_ok:
            log("RESULT: SUCCESS - the generated project is green.")
        else:
            log("RESULT: REVIEW REQUIRED - validation did not pass.")
        self.print_tree()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a .NET Clean Architecture project scaffold with "
                    "agentic development tooling."
    )
    parser.add_argument("name", help="Project name (e.g. Matchly, MyApp, My-App)")
    parser.add_argument("--dir", default=None, help="Output directory (default: <Name> in the current directory)")
    parser.add_argument("--framework", default=FRAMEWORK, help="Target framework (default: net10.0)")
    parser.add_argument("--no-validate", action="store_true", help="Skip dotnet restore/build/test")
    parser.add_argument("--no-git", action="store_true", help="Skip git init and initial commits")
    parser.add_argument("--include-agent-runs", action="store_true", help="Also copy docs/agent-runs historical records")
    parser.add_argument("--force", action="store_true", help="Delete and recreate the output directory if it is not empty")
    args = parser.parse_args()

    try:
        generator = Generator(
            name=args.name,
            out_dir=Path(args.dir).resolve() if args.dir else (Path.cwd() / args.name).resolve(),
            framework=args.framework,
            include_agent_runs=args.include_agent_runs,
            do_validate=not args.no_validate,
            do_git=not args.no_git,
        )

        generator.check_tools()
        generator.prepare_directory(force=args.force)
        generator.scaffold()
        generator.configure_projects()
        generator.write_custom_files()
        generator.copy_docs()
        generator.generate_opencode()

        if generator.do_validate:
            generator.validate()
        else:
            log("\n=== Validation skipped (--no-validate) ===")

        if generator.do_git:
            generator.git_init()
        else:
            log("\n=== Git skipped (--no-git) ===")

        generator.report()
    except ScriptError as exc:
        log(f"\nERROR: {exc}")
        sys.exit(1)
    except ValueError as exc:
        log(f"\nERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
