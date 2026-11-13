#!/usr/bin/env python3
"""
generate_project.py - Generates a .NET 10 Clean Architecture project scaffold
with agentic development tooling (TDP workflow, specialized agents and OpenCode
commands), based on the Matchly experiment.

Usage:
    python3 generate_project.py                      # interactive Gruvbox wizard
    python3 generate_project.py <ProjectName> [options]

Options:
    --database postgres|sqlserver   Database provider (default: postgres)
    --db-password PASSWORD          SQL Server SA password (default: random)
    --api-style controllers|minimal API style (default: controllers)
    --framework net10.0             Target framework (default: net10.0)
    --dir DIR                       Output directory
    --no-validate                   Skip dotnet restore/build/test
    --no-git                        Skip git init and initial commits
    --include-agent-runs            Also copy docs/agent-runs records
    --force                         Delete and recreate the output directory
    --wizard                        Force the interactive Gruvbox wizard

The generated project substitutes every occurrence of "Matchly"/"matchly" with
the provided project name (PascalCase and lowercase forms). Template files
under templates/ are substituted with {{ProjectName}}/{{ProjectNameLower}}.
"""

import argparse
import json
import re
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

try:  # POSIX terminals only; the wizard falls back to numbered menus elsewhere
    import termios
    import tty
    POSIX_TTY = True
except ImportError:
    POSIX_TTY = False

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"
HELP_DOCS_DIR = SCRIPT_DIR / "HelpDocuments"

FRAMEWORK = "net10.0"
MIN_TFM_MAJOR = 10
API_STYLE = "controllers"

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

DATABASES = {
    "postgres": {
        "display": "PostgreSQL",
        "compose_source": "docker-compose.postgres.yml",
        "registration_source": "InfrastructureRegistration.Postgres.cs",
        "provider_package": "Npgsql.EntityFrameworkCore.PostgreSQL",
        "provider_name": "Npgsql.EntityFrameworkCore.PostgreSQL",
        "password_required": False,
    },
    "sqlserver": {
        "display": "SQL Server",
        "compose_source": "docker-compose.sqlserver.yml",
        "registration_source": "InfrastructureRegistration.SqlServer.cs",
        "provider_package": "Microsoft.EntityFrameworkCore.SqlServer",
        "provider_name": "Microsoft.EntityFrameworkCore.SqlServer",
        "password_required": True,
    },
}

# ------------------------------------------------------------------ gruvbox UI
# 256-color approximations of the Gruvbox dark palette.
GRUVBOX = {
    "bg0": "\x1b[48;5;235m",    # #282828
    "fg": "\x1b[38;5;223m",     # #ebdbb2
    "gray": "\x1b[38;5;244m",   # #928374
    "red": "\x1b[38;5;167m",    # #fb4934
    "green": "\x1b[38;5;142m",  # #b8bb26
    "yellow": "\x1b[38;5;214m", # #fabd2f
    "blue": "\x1b[38;5;109m",   # #83a598
    "purple": "\x1b[38;5;175m", # #d3869b
    "aqua": "\x1b[38;5;108m",   # #8ec07c
    "orange": "\x1b[38;5;208m", # #fe8019
    "bold": "\x1b[1m",
    "reset": "\x1b[0m",
}
WIDTH = 78
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class WizardAbort(Exception):
    pass


def _style(text: str, color: str, bold: bool = False) -> str:
    if not sys.stdout.isatty():
        return text
    code = GRUVBOX[color]
    if bold:
        code += GRUVBOX["bold"]
    return f"{code}{text}{GRUVBOX['reset']}"


def _pad_width(styled: str) -> int:
    return len(ANSI_RE.sub("", styled))


def cprint(text: str = "", color: str = "fg", bold: bool = False, end: str = "\n") -> None:
    print(_style(text, color, bold), end=end)


def header(title: str) -> None:
    cprint(f"\n{_style('===', 'yellow', True)} {_style(title, 'yellow', True)} {_style('===', 'yellow', True)}")


def box(lines: list, width: int = WIDTH, title: str | None = None) -> None:
    border = GRUVBOX["yellow"] + GRUVBOX["bold"]
    reset = GRUVBOX["reset"]
    if title:
        plain_title = f" {title} "
        if sys.stdout.isatty():
            print(f"{border}┌─{reset}{_style(plain_title, 'green', True)}{border}{'─' * max(0, width - _pad_width(plain_title) - 3)}┐{reset}")
        else:
            print(f"┌─{plain_title}{'─' * max(0, width - len(plain_title) - 3)}┐")
    else:
        if sys.stdout.isatty():
            print(f"{border}┌{'─' * (width - 2)}┐{reset}")
        else:
            print(f"┌{'─' * (width - 2)}┐")
    for item in lines:
        if isinstance(item, str):
            text, color, bold = item, "fg", False
        else:
            text, color, bold = item
        pad = max(0, width - 4 - _pad_width(text))
        if sys.stdout.isatty():
            print(f"{border}│{reset} {_style(text, color, bold)}{' ' * pad} {border}│{reset}")
        else:
            print(f"│ {text}{' ' * pad} │")
    if sys.stdout.isatty():
        print(f"{border}└{'─' * (width - 2)}┘{reset}")
    else:
        print(f"└{'─' * (width - 2)}┘")


def show_banner() -> None:
    box(
        [
            (f"  {_style('Clean Architecture', 'green', True)}  {_style('•', 'yellow')}  "
             f"{_style('CQRS', 'green', True)}  {_style('•', 'yellow')}  "
             f"{_style('.NET', 'green', True)}", "fg", False),
            (f"  Project Scaffolder  {_style('•', 'yellow')}  "
             f"{_style('OpenCode agentic tooling', 'gray')}  {_style('•', 'yellow')}  "
             f"{_style('Gruvbox', 'orange', True)}", "fg", False),
        ],
        title="Matchly Generator",
    )


def _read_key() -> str:
    if not POSIX_TTY:
        return ""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        data = sys.stdin.buffer.read(3)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    if data == b"\x1b[A":
        return "up"
    if data == b"\x1b[B":
        return "down"
    if data in (b"\r", b"\n"):
        return "enter"
    if data in (b"\x1b", b"q", b"Q"):
        return "quit"
    return ""


def _render_options(options: list[str], index: int) -> list[str]:
    rows = []
    for i, opt in enumerate(options):
        marker = "▸" if i == index else " "
        color = "aqua" if i == index else "gray"
        rows.append(f"  {_style(marker, 'yellow', True if i == index else False)} {_style(opt, color, bold=(i == index))}")
    return rows


def select_choice(prompt: str, options: list[str]) -> int:
    n = len(options)
    index = 0
    print()
    cprint(prompt, "yellow", bold=True)

    interactive = sys.stdin.isatty() and POSIX_TTY
    if not interactive:
        print()
        for i, opt in enumerate(options):
            print(f"  {i + 1}. {opt}")
        while True:
            try:
                raw = input(_style("  Select option: ", "aqua", bold=True)).strip()
            except EOFError:
                raise WizardAbort()
            if raw.isdigit() and 1 <= int(raw) <= n:
                print()
                return int(raw) - 1
            cprint(f"  ✗ Invalid option: {raw}", "red")

    sys.stdout.write("\n".join(_render_options(options, index)) + "\n")
    sys.stdout.flush()

    while True:
        key = _read_key()
        if key == "up":
            index = (index - 1) % n
        elif key == "down":
            index = (index + 1) % n
        elif key == "enter":
            print()
            return index
        elif key == "quit":
            print()
            raise WizardAbort()
        else:
            continue
        sys.stdout.write(f"\x1b[{n + 1}A")
        sys.stdout.write("\n".join(_render_options(options, index)) + "\n")
        sys.stdout.flush()


def ask_text(prompt: str, default: str | None = None, validator=None) -> str:
    while True:
        suffix = f" [{default}]" if default else ""
        try:
            raw = input(f"\n{_style(prompt, 'yellow', bold=True)}{_style(suffix, 'gray')} : ").strip()
        except EOFError:
            raise WizardAbort()
        if not raw and default:
            raw = default
        if validator is not None:
            try:
                validator(raw)
            except ValueError as exc:
                cprint(f"  ✗ {exc}", "red")
                continue
        return raw


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "(Y/n)" if default else "(y/N)"
    try:
        raw = input(f"\n{_style(prompt, 'aqua', bold=True)} {_style(suffix, 'gray')} : ").strip().lower()
    except EOFError:
        raise WizardAbort()
    if not raw:
        return default
    return raw in ("y", "yes")


def generate_db_password() -> str:
    return secrets.token_urlsafe(12)


def run_wizard() -> argparse.Namespace:
    print()
    show_banner()
    print()
    box(
        [
            ("Generates a .NET Clean Architecture solution with CQRS,", "gray", False),
            ("agents, commands and docker files for the selected database.", "gray", False),
            (f"  {_style('postgres', 'blue', True)}  |  {_style('sqlserver', 'blue', True)}", "gray", False),
        ],
        width=WIDTH,
    )
    print()

    name = ask_text("Project name", validator=normalize_name)

    db_keys = list(DATABASES)
    db_idx = select_choice("Select the database", [DATABASES[k]["display"] for k in db_keys])
    database = db_keys[db_idx]

    api_idx = select_choice("Select the API style", ["controllers", "minimal"])
    api_style = "controllers" if api_idx == 0 else "minimal"

    framework = ask_text("Target framework", default=FRAMEWORK, validator=validate_framework)
    out_dir = ask_text("Output directory", default=str(Path.cwd() / name))

    do_validate = ask_yes_no("Run dotnet restore/build/test validation?", True)
    do_git = ask_yes_no("Initialize git repository (three commits)?", True)

    if DATABASES[database]["password_required"]:
        db_password = generate_db_password()
    else:
        db_password = None

    print()
    box(
        [
            (f"  {_style('Project:', 'yellow', True)}   {name}", "fg", False),
            (f"  {_style('Database:', 'yellow', True)}  {DATABASES[database]['display']}", "fg", False),
            (f"  {_style('API:', 'yellow', True)}       {api_style}", "fg", False),
            (f"  {_style('Framework:', 'yellow', True)} {framework}", "fg", False),
            (f"  {_style('Output:', 'yellow', True)}    {out_dir}", "fg", False),
            (f"  {_style('Validate:', 'yellow', True)}  {'yes' if do_validate else 'no'}", "fg", False),
            (f"  {_style('Git init:', 'yellow', True)}  {'yes' if do_git else 'no'}", "fg", False),
        ],
        title="Summary",
    )
    if db_password:
        cprint(f"\n  SQL Server SA password: {_style(db_password, 'orange', True)}")
        cprint("  (stored in docker/.env, gitignored)", "gray")

    out_path = Path(out_dir).resolve()
    force = False
    if out_path.exists() and any(out_path.iterdir()):
        force = ask_yes_no(f"Output directory '{out_dir}' is not empty. Delete and recreate?", False)

    if not ask_yes_no("Generate the project now?", True):
        print()
        cprint("Aborted by user.", "red", bold=True)
        raise SystemExit(0)

    print()
    return argparse.Namespace(
        name=name,
        dir=out_dir,
        framework=framework,
        api_style=api_style,
        database=database,
        db_password=db_password,
        no_validate=not do_validate,
        no_git=not do_git,
        include_agent_runs=False,
        force=force,
    )


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
- Domain has no dependency on Application, Infrastructure, API, ASP.NET Core, EF Core or the database provider (PostgreSQL / SQL Server).
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
        hint = network_error_hint(tail)
        if hint:
            log(f"  -> {hint}")
        raise ScriptError(f"command failed: {printable}")
    log("  -> OK")
    return result


def run_soft(cmd: list, cwd: Path | None = None) -> subprocess.CompletedProcess:
    printable = " ".join(cmd)
    log(f"\n> {printable}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    log(f"  -> exit code {result.returncode}")
    return result


# Error markers that indicate a network problem (missing connectivity to
# NuGet.org) rather than a code or configuration issue.
NETWORK_ERROR_MARKERS = (
    "NU1301",                          # unable to load the service index
    "service index",
    "could not connect",
    "connection refused",
    "connection timed out",
    "no such host",
    "remote name could not be resolved",
    "the ssl connection could not be established",
    "securechannelfailure",
    "an error occurred while sending the request",
    "401 (unauthorized)",
    "403 (forbidden)",
    "407 (proxy authentication required)",
)


def network_error_hint(text: str) -> str:
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in NETWORK_ERROR_MARKERS):
        return (
            "This step needs network access to NuGet.org - check your "
            "internet connection and retry."
        )
    return ""


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


def validate_framework(framework: str) -> str:
    match = re.fullmatch(r"net(\d+)\.(\d+)", framework)
    if not match:
        raise ScriptError(
            f"Invalid target framework '{framework}'. Expected a TFM of the form "
            f"net<major>.<minor> (e.g. net10.0)."
        )
    major = int(match.group(1))
    if major < MIN_TFM_MAJOR:
        raise ScriptError(
            f"Target framework '{framework}' is not supported. "
            f"Minimum supported major version is net{MIN_TFM_MAJOR}.0 "
            f"(e.g. net10.0, net11.0, net12.0)."
        )
    return framework


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


def build_connection_string(database: str, lower: str, password: str | None = None) -> str:
    if database == "postgres":
        return f"Host=localhost;Port=5432;Database={lower};Username=postgres"
    return (
        f"Server=localhost,1433;Database={lower};User Id=sa;"
        f"Password={password};TrustServerCertificate=True"
    )


class Generator:
    def __init__(
        self,
        name: str,
        out_dir: Path,
        framework: str,
        api_style: str,
        database: str,
        db_password: str | None,
        include_agent_runs: bool,
        do_validate: bool,
        do_git: bool,
    ) -> None:
        self.pascal, self.lower = normalize_name(name)
        self.out = out_dir
        self.framework = framework
        self.api_style = api_style
        self.database = database
        self.db_info = DATABASES[database]
        if self.db_info["password_required"]:
            self.db_password = db_password or generate_db_password()
        else:
            self.db_password = None
        self.connection_string = build_connection_string(
            self.database, self.lower, self.db_password
        )
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
            "Api.Tests",
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
        header("Scaffolding projects")
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

        header("Removing template placeholder files")
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
        header("Adding project references")
        app = self.src_proj("Application")
        inf = self.src_proj("Infrastructure")
        api = self.src_proj("Api")
        domain = self.src_proj("Domain")

        run(["dotnet", "add", str(app / f"{self.pascal}.Application.csproj"), "reference", str(domain / f"{self.pascal}.Domain.csproj")])
        run(["dotnet", "add", str(inf / f"{self.pascal}.Infrastructure.csproj"), "reference", str(domain / f"{self.pascal}.Domain.csproj")])
        run(["dotnet", "add", str(inf / f"{self.pascal}.Infrastructure.csproj"), "reference", str(app / f"{self.pascal}.Application.csproj")])
        run(["dotnet", "add", str(api / f"{self.pascal}.Api.csproj"), "reference", str(app / f"{self.pascal}.Application.csproj")])
        # The API is the composition root: it wires persistence registered in
        # Infrastructure. No business rules live in the API layer.
        run(["dotnet", "add", str(api / f"{self.pascal}.Api.csproj"), "reference", str(inf / f"{self.pascal}.Infrastructure.csproj")])

        src_refs = {
            "Domain.Tests": ["Domain"],
            "Application.Tests": ["Application"],
            "Infrastructure.Tests": ["Infrastructure"],
            "Api.Tests": ["Api"],
            "Architecture.Tests": ["Domain", "Application", "Infrastructure", "Api"],
        }
        for test_layer, ref_layers in src_refs.items():
            test_proj_file = self.test_proj(test_layer) / f"{self.pascal}.{test_layer}.csproj"
            for ref_layer in ref_layers:
                ref_file = self.src_proj(ref_layer) / f"{self.pascal}.{ref_layer}.csproj"
                run(["dotnet", "add", str(test_proj_file), "reference", str(ref_file)])

        header("Adding NuGet packages")
        api_proj = api / f"{self.pascal}.Api.csproj"
        run([
            "dotnet", "add", str(api_proj), "package",
            "Microsoft.AspNetCore.OpenApi",
        ])
        arch_proj = self.test_proj("Architecture.Tests") / f"{self.pascal}.Architecture.Tests.csproj"
        run(["dotnet", "add", str(arch_proj), "package", "NetArchTest.Rules"])
        api_tests_proj = self.test_proj("Api.Tests") / f"{self.pascal}.Api.Tests.csproj"
        run(["dotnet", "add", str(api_tests_proj), "package", "Microsoft.AspNetCore.Mvc.Testing"])
        for test_layer in self.test_layers:
            test_proj_file = self.test_proj(test_layer) / f"{self.pascal}.{test_layer}.csproj"
            run(["dotnet", "add", str(test_proj_file), "package", "FluentAssertions"])

        header("Adding Entity Framework Core packages")
        infra_proj_file = inf / f"{self.pascal}.Infrastructure.csproj"
        run(["dotnet", "add", str(infra_proj_file), "package", "Microsoft.EntityFrameworkCore"])
        run(["dotnet", "add", str(infra_proj_file), "package", self.db_info["provider_package"]])

    def write_custom_files(self) -> None:
        header("Writing custom source files")
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

        program_template = (
            "ProgramControllers.cs" if self.api_style == "controllers" else "ProgramMinimal.cs"
        )
        program = self.src_proj("Api") / "Program.cs"
        program.write_text(
            substitute_template(
                (TEMPLATES_DIR / "code" / program_template).read_text(encoding="utf-8"),
                self.pascal, self.lower,
            ),
            encoding="utf-8",
        )

        if self.api_style == "controllers":
            health_controller = self.src_proj("Api") / "Controllers" / "HealthController.cs"
            health_controller.parent.mkdir(parents=True, exist_ok=True)
            health_controller.write_text(
                substitute_template(
                    (TEMPLATES_DIR / "code" / "HealthController.cs").read_text(encoding="utf-8"),
                    self.pascal, self.lower,
                ),
                encoding="utf-8",
            )

        health_tests = self.test_proj("Api.Tests") / "HealthTests.cs"
        health_tests.write_text(
            substitute_template(
                (TEMPLATES_DIR / "code" / "HealthTests.cs").read_text(encoding="utf-8"),
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

        header("Writing persistence wiring for " + self.db_info["display"])
        db_context = self.src_proj("Infrastructure") / f"{self.pascal}DbContext.cs"
        db_context.write_text(
            substitute_template(
                (TEMPLATES_DIR / "code" / "DbContext.cs").read_text(encoding="utf-8"),
                self.pascal, self.lower,
            ),
            encoding="utf-8",
        )

        registration = self.src_proj("Infrastructure") / "InfrastructureServiceCollectionExtensions.cs"
        registration.write_text(
            substitute_template(
                (TEMPLATES_DIR / "code" / self.db_info["registration_source"]).read_text(encoding="utf-8"),
                self.pascal, self.lower,
            ),
            encoding="utf-8",
        )

        reg_tests_content = (
            TEMPLATES_DIR / "code" / "InfrastructureRegistrationTests.cs"
        ).read_text(encoding="utf-8")
        reg_tests_content = (
            reg_tests_content.replace("{{ProjectName}}", self.pascal)
            .replace("{{ProviderName}}", self.db_info["provider_name"])
        )
        (self.test_proj("Infrastructure.Tests") / "InfrastructureRegistrationTests.cs").write_text(
            reg_tests_content, encoding="utf-8"
        )

    def write_appsettings(self) -> None:
        header("Writing connection string")
        appsettings = self.src_proj("Api") / "appsettings.json"
        data = json.loads(appsettings.read_text(encoding="utf-8"))
        data["ConnectionStrings"] = {"Default": self.connection_string}
        appsettings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def copy_docs(self) -> None:
        header("Copying documentation")
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

        header("Writing docker files for " + self.db_info["display"])
        compose_src = TEMPLATES_DIR / "docker" / self.db_info["compose_source"]
        (self.out / "docker-compose.yml").write_text(
            substitute_template(compose_src.read_text(encoding="utf-8"), self.pascal, self.lower),
            encoding="utf-8",
        )

        # Dockerfiles live at the project root so the compose build context
        # ('.') resolves their relative paths (src/<Name>.Api/...).
        for docker_file in ("Dockerfile", "Dockerfile.dev"):
            src_file = TEMPLATES_DIR / "docker" / docker_file
            (self.out / docker_file).write_text(
                substitute_template(src_file.read_text(encoding="utf-8"), self.pascal, self.lower),
                encoding="utf-8",
            )

        docker_dir = self.out / "docker"
        docker_dir.mkdir(parents=True, exist_ok=True)
        for compose_file in ("docker-compose.postgres.yml", "docker-compose.sqlserver.yml"):
            src = TEMPLATES_DIR / "docker" / compose_file
            (docker_dir / compose_file).write_text(
                substitute_template(src.read_text(encoding="utf-8"), self.pascal, self.lower),
                encoding="utf-8",
            )

        docker_readme = TEMPLATES_DIR / "docker" / f"README.{self.database}.md"
        (docker_dir / "README.md").write_text(
            substitute_template(docker_readme.read_text(encoding="utf-8"), self.pascal, self.lower),
            encoding="utf-8",
        )

        env_example = TEMPLATES_DIR / "docker" / ".env.example"
        (docker_dir / ".env.example").write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")

        if self.db_password:
            (docker_dir / ".env").write_text(f"MSSQL_SA_PASSWORD={self.db_password}\n", encoding="utf-8")

        gitignore = (TEMPLATES_DIR / ".gitignore").read_text(encoding="utf-8")
        (self.out / ".gitignore").write_text(gitignore, encoding="utf-8")

    def generate_opencode(self) -> None:
        header("Generating .opencode agents and commands")
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
        header("Validation")
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
                hint = network_error_hint((result.stdout or "") + (result.stderr or ""))
                if hint:
                    log(f"  -> {hint}")
            else:
                log(f"  {label}: PASS")
        self.validation_ok = all_ok
        return all_ok

    # ------------------------------------------------------------------- git
    def git_init(self) -> None:
        header("Initializing git repository")
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
                     ("Domain.Tests", "Application.Tests", "Infrastructure.Tests", "Api.Tests")]

        stage([
            ".gitignore",
            "docker-compose.yml",
            "Dockerfile",
            "Dockerfile.dev",
            "docker",
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

        run(["git", "checkout", "-b", "develop"], cwd=self.out)
        log("  switched to branch: develop (recommended state for feature development)")

    # ----------------------------------------------------------------- report
    def verify_no_leftovers(self) -> list:
        issues = []
        skip_names = {"obj", "bin", ".git", "__pycache__"}
        for f in self.out.rglob("*"):
            if f.is_file() and not any(part in skip_names for part in f.parts):
                if f.suffix in {".md", ".cs", ".csproj", ".yml", ".yaml", ".json", ".sln", ".txt"}:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    if "{{ProjectName}}" in text or "{{ProjectNameLower}}" in text:
                        issues.append((f, "{{...}} token"))
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
        print()
        box(
            [
                (f"  {_style('Project:', 'yellow', True)}     {self.pascal}", "fg", False),
                (f"  {_style('Namespace:', 'yellow', True)}   {self.pascal}", "fg", False),
                (f"  {_style('Directory:', 'yellow', True)}   {self.out}", "fg", False),
                (f"  {_style('Framework:', 'yellow', True)}   {self.framework}", "fg", False),
                (f"  {_style('API style:', 'yellow', True)}   {self.api_style}", "fg", False),
                (f"  {_style('Database:', 'yellow', True)}    {self.db_info['display']}", "fg", False),
                (
                    f"  {_style('Validation:', 'yellow', True)}  "
                    f"{_style('PASS', 'green', True) if self.validation_ok else _style('NOT RUN / FAILED', 'red', True)}",
                    "fg", False,
                ),
            ],
            title="GENERATION REPORT",
        )
        if self.db_password:
            cprint(f"  SQL Server SA password: {_style(self.db_password, 'orange', True)}")
            cprint("  (stored in docker/.env — not committed to git)", "gray")
        leftovers = self.verify_no_leftovers()
        if leftovers:
            cprint(f"  Name sweep: {_style(f'{len(leftovers)} leftover reference(s)', 'red', True)}")
            for path, token in leftovers:
                log(f"  - {path.relative_to(self.out)} contains '{token}'")
        else:
            cprint(f"  Name sweep: {_style('CLEAN', 'green', True)}")
        print()
        if self.validation_ok:
            cprint("  RESULT: SUCCESS — the generated project is green.", "green", bold=True)
        else:
            cprint("  RESULT: REVIEW REQUIRED — validation did not pass.", "red", bold=True)
        self.print_tree()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a .NET Clean Architecture project scaffold with "
                    "agentic development tooling."
    )
    parser.add_argument("name", nargs="?", help="Project name (e.g. Matchly, MyApp, My-App). Required unless the interactive wizard is used.")
    parser.add_argument("--dir", default=None, help="Output directory (default: <Name> in the current directory)")
    parser.add_argument("--framework", default=FRAMEWORK, help="Target framework, TFM form net<major>.<minor> (default: net10.0, minimum: net10.0)")
    parser.add_argument("--api-style", default=API_STYLE, choices=["controllers", "minimal"],
                        help="API style: 'controllers' generates a HealthController; 'minimal' uses minimal APIs (default: controllers)")
    parser.add_argument("--database", default="postgres", choices=sorted(DATABASES),
                        help="Database provider: 'postgres' (default) or 'sqlserver'")
    parser.add_argument("--db-password", default=None,
                        help="SQL Server SA password (default: a random password generated and stored in docker/.env)")
    parser.add_argument("--no-validate", action="store_true", help="Skip dotnet restore/build/test")
    parser.add_argument("--no-git", action="store_true", help="Skip git init and initial commits")
    parser.add_argument("--include-agent-runs", action="store_true", help="Also copy docs/agent-runs historical records")
    parser.add_argument("--force", action="store_true", help="Delete and recreate the output directory if it is not empty")
    parser.add_argument("--wizard", "-w", action="store_true", help="Force the interactive Gruvbox wizard")
    return parser


def main() -> None:
    parser = build_parser()
    raw = sys.argv[1:]
    if not raw or "--wizard" in raw or "-w" in raw:
        try:
            args = run_wizard()
        except WizardAbort:
            cprint("\nAborted by user.", "red", bold=True)
            sys.exit(0)
        except KeyboardInterrupt:
            cprint("\nInterrupted by user.", "red", bold=True)
            sys.exit(130)
    else:
        args = parser.parse_args(raw)

    try:
        validate_framework(args.framework)
        generator = Generator(
            name=args.name,
            out_dir=Path(args.dir).resolve() if args.dir else (Path.cwd() / args.name).resolve(),
            framework=args.framework,
            api_style=args.api_style,
            database=args.database,
            db_password=args.db_password,
            include_agent_runs=args.include_agent_runs,
            do_validate=not args.no_validate,
            do_git=not args.no_git,
        )

        generator.check_tools()
        generator.prepare_directory(force=args.force)
        generator.scaffold()
        generator.configure_projects()
        generator.write_custom_files()
        generator.write_appsettings()
        generator.copy_docs()
        generator.generate_opencode()

        if generator.do_validate:
            if not generator.validate():
                generator.report()
                log("\nERROR: validation failed (restore/build/test did not all pass).")
                sys.exit(1)
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