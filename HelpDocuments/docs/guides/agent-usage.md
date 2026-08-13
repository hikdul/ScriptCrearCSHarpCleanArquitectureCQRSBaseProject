# Agent Usage Guide

This guide explains how to use the agentic development setup of Matchly:

- the recommended state before starting a feature
- the available commands and agents
- how feature specification documents must look
- the full TDP workflow

The mandatory contracts are `AGENTS.md` and
`docs/workflows/tdp-feature-workflow.md`. This guide is the operational
reference: read it before using the agents.

---

# 1. Setup Overview

The project ships with an OpenCode configuration (`.opencode/`) that provides
8 agents and 7 commands, all driven by the documentation contract under
`docs/`.

| Piece          | Location                          | Purpose                                   |
| -------------- | --------------------------------- | ----------------------------------------- |
| Contract       | `AGENTS.md`                       | Mandatory development rules               |
| Workflow       | `docs/workflows/tdp-feature-workflow.md` | TDP feature development process     |
| Agents         | `.opencode/agents/`               | Specialized roles with scoped permissions |
| Commands       | `.opencode/commands/`             | User-facing entry points                  |
| Specifications | `docs/specifications/`            | Source of truth for features              |
| Architecture   | `docs/architecture/`              | Architectural rules and ADRs              |

---

# 2. Recommended State Before Using the Agents

Start every feature from a known, clean state. The Orchestrator verifies this
state itself, but you should ensure it before invoking a command.

## 2.1 Repository State

```text
Current branch = develop
Working tree   = clean
```

Commands to verify:

```bash
git branch --show-current
git status --porcelain
```

A freshly generated project already lands on `develop`. If not:

```bash
git checkout develop        # or: git checkout -b develop
git pull                    # if a remote exists
```

## 2.2 Feature Branch

Never implement on `main` or `develop`. The Orchestrator creates and uses a
feature branch automatically:

```text
feature/<feature-id>-<short-name>
```

Example:

```bash
git checkout -b feature/005-report-profile
```

The `<feature-id>` matches the specification document id in
`docs/specifications/` (e.g. `005-report-profile.md`).

## 2.3 Infrastructure

If the feature touches persistence or the database, start PostgreSQL first:

```bash
docker compose up -d
```

This starts `matchly-postgres` on `localhost:5432`
(database `matchly`, user `postgres`, trust auth for local
development).

## 2.4 Scope

- Work on **one feature at a time**.
- Do not start a feature while another feature is unfinished.
- A feature is only one branch with one specification.

---

# 3. Commands Reference

All commands are run inside OpenCode:

```text
/command-name arguments
```

## 3.1 Full Workflow

| Command     | Delegates to      | What it does                                              |
| ----------- | ----------------- | --------------------------------------------------------- |
| `/feature`  | Orchestrator      | Runs the complete TDP workflow: plan → tests → implement → refactor → architecture → validate (max 3 attempts) |

This is the recommended entry point for a new feature:

```text
/feature "a user can report another profile"
```

The Orchestrator creates the specification, coordinates the subagents through
RED/GREEN/REFACTOR, runs the quality gate and reports the final result.

## 3.2 Step-by-Step

Use individual commands when you want to control each stage explicitly:

| # | Command       | Delegates to | Stage         | What it does                                        |
| - | ------------- | ------------ | ------------- | --------------------------------------------------- |
| 1 | `/plan`       | Specification | SPECIFICATION | Creates or validates the feature specification      |
| 2 | `/tests`      | Test         | RED           | Translates acceptance criteria into failing tests   |
| 3 | `/implement`  | Implementation| GREEN         | Writes the minimum production code to pass the tests|
| 4 | `/refactor`   | Refactor      | REFACTOR      | Improves the design without changing behavior       |
| 5 | `/architecture`| Architecture| ARCHITECTURE  | Validates Clean Architecture rules                  |
| 6 | `/validate`   | Validation    | VALIDATION    | Runs the final quality gate                         |

Rules:

- Do not skip stages. A feature cannot skip `SPECIFICATION` or `RED`.
- `/implement` may only run after a valid RED state exists.
- `/validate` never modifies code; it only observes and reports.

---

# 4. Agent Catalog

Agents are the roles behind the commands. Permissions are enforced by
OpenCode, so each agent can only touch its own scope.

| Agent          | Mode      | Can edit                          | Bash | Task | Responsibility                       |
| -------------- | --------- | --------------------------------- | :--: | :--: | ------------------------------------ |
| Orchestrator   | all       | nothing                           | yes  | yes  | Coordinates the workflow, GitFlow    |
| Specification  | subagent  | `docs/specifications/**`, `docs/agent-runs/**` | no | no | Feature specifications |
| Test           | subagent  | `tests/**`, `docs/agent-runs/**`  | yes  | no   | TDD / RED                            |
| Implementation | subagent  | `src/**`, `docs/agent-runs/**`    | yes  | no   | GREEN (production code)              |
| Refactor       | subagent  | `src/**`, `docs/agent-runs/**`    | yes  | no   | Design cleanup                       |
| Architecture   | subagent  | `docs/agent-runs/**`              | yes  | no   | Architecture validation              |
| Validation     | subagent  | `docs/agent-runs/**`              | yes  | no   | Quality gate                         |
| Release        | subagent  | nothing                           | yes  | no   | GitFlow releases (develop → main)    |

Key consequences:

- The **Test** agent writes tests but never production code.
- The **Implementation** and **Refactor** agents write production code but
  never tests.
- The **Specification** agent only writes feature specifications.
- The **Architecture** and **Validation** agents only observe and report;
  they fix nothing.
- Agent run records are written to `docs/agent-runs/` for traceability.

---

# 5. Feature Specification Documents

Every feature begins with a specification. It is the source of truth for all
later stages.

## 5.1 Location and Naming

Specifications live in:

```text
docs/specifications/
```

Naming convention:

```text
<feature-id>-<short-name>.md
```

Examples:

```text
001-like-profile.md
002-create-match.md
003-unmatch-profile.md
004-block-profile.md
005-report-profile.md
```

Feature ids are sequential and unique. The short name is a brief hyphenated
description.

## 5.2 Required Structure

Every specification must contain the following sections, in order:

```text
# <Feature Name>

## Objective
What behavior is introduced and why (business capability, not implementation).

## Context
Where the feature fits in the existing system and what it depends on.

## Business Rules
Invariants that must always hold. Explicit, deterministic, independently
testable, implementation-independent.

## Acceptance Criteria
Observable behavior, written as Given/When/Then. Each meaningful business rule
must have at least one criterion. This section feeds the Test Agent.

## Constraints
The expected architectural layer and any forbidden concerns
(no persistence, no HTTP, no Application/Infrastructure dependency, etc.).

## Out of Scope
Explicitly listed behavior that is NOT part of this feature
(prevents scope expansion).

## TDD
The mandatory statement that tests come first and production code must not
begin before RED is established.
```

## 5.3 Writing Good Criteria

Acceptance criteria describe **behavior**, not implementation:

```text
Given User A and User B.

When User A performs X.

Then User A can observe Y.
```

Prefer:

```text
A user cannot like their own profile.
```

Avoid:

```text
User.Like must call validation method X.
```

## 5.4 Example

Use `docs/specifications/001-like-profile.md` as a complete reference
specification.

---

# 6. The TDP Workflow Step by Step

The workflow is described in full in
`docs/workflows/tdp-feature-workflow.md`. The essential loop:

## 6.1 RED

1. Create or update the tests required by the acceptance criteria.
2. Run them. They must fail because the behavior does not exist.
3. A compilation or infrastructure failure is NOT a valid RED.

## 6.2 GREEN

1. Implement the minimum production code to satisfy the tests.
2. Do not add speculative functionality, persistence, API endpoints or
   unrelated behavior.
3. Run the tests. They must pass.

## 6.3 REFACTOR

1. Improve naming, structure, cohesion, coupling, readability.
2. Do not change observable behavior.
3. Do not modify tests.
4. "No refactor required" is a valid result.

## 6.4 Quality Gate

Before a feature is complete:

```bash
dotnet build
dotnet test
```

Architecture tests must pass:

```bash
dotnet test tests/Matchly.Architecture.Tests/Matchly.Architecture.Tests.csproj
```

When applicable:

```bash
dotnet format --verify-no-changes
```

## 6.5 Retry Limit

- Maximum implementation attempts per feature: **3** (initial attempt counts
  as attempt 1).
- After a FAIL, the Orchestrator routes the feature back to the responsible
  agent and re-runs validation.
- After 3 failed attempts, the workflow STOPS and reports.

## 6.6 Stop Conditions

The agents stop and report instead of proceeding when:

- the failure is caused by the specification itself
- the failure is an environment problem that cannot be resolved safely
- an architecture violation is detected
- an existing test would have to be weakened to proceed

---

# 7. Completion Report

When a feature finishes, the Orchestrator reports:

1. Feature implemented.
2. Specification used.
3. Tests created or modified.
4. Production code created or modified.
5. Refactoring performed.
6. Validation commands executed.
7. Validation results.
8. Number of attempts used.
9. Remaining issues.

Never trust a completion report that claims success without executed
validation commands.

---

# 8. Quick Reference Checklist

Before starting a feature:

- [ ] Branch is `develop` and the working tree is clean.
- [ ] PostgreSQL is running (`docker compose up -d`) if needed.
- [ ] One feature at a time.

During development:

- [ ] Specification exists in `docs/specifications/<feature-id>-<short-name>.md`.
- [ ] Tests exist and were observed failing (valid RED).
- [ ] Minimum production code makes them pass (GREEN).
- [ ] Refactoring preserves behavior.
- [ ] Architecture tests pass.
- [ ] `dotnet build` and `dotnet test` pass.
- [ ] No unrelated files were modified.
- [ ] The feature is on its own branch (`feature/<feature-id>-<short-name>`).
