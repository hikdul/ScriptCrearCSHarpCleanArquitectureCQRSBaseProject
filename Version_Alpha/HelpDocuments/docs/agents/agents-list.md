# Agent List

| Agent         | Responsibility                        | Can edit production | Can edit tests |
| ------------- | ------------------------------------- | :-----------------: | :------------: |
| Orchestrator  | Coordinate the workflow, GitFlow      |          ❌         |       ❌       |
| Specification | Feature specifications                |          ❌         |       ❌       |
| Test          | TDD / RED                            |          ❌         |       ✅       |
| Implementation| GREEN (production code)               |          ✅         |       ❌       |
| Refactor      | Design cleanup                        |          ✅         |       ❌       |
| Architecture  | Architecture validation               |          ❌         |       ❌       |
| Validation    | Quality gate                          |          ❌         |       ❌       |
| Release       | GitFlow / release                     |          ❌         |       ❌       |

## Edit Scopes

```text
Test Agent
    READ:  everything
    WRITE: tests/**
    WRITE: docs/agent-runs/**

Implementation Agent
    READ:  everything
    WRITE: src/**
    WRITE: docs/agent-runs/**

Refactor Agent
    READ:  everything
    WRITE: src/**
    WRITE: docs/agent-runs/**

Specification Agent
    READ:  everything
    WRITE: docs/specifications/**
    WRITE: docs/agent-runs/**

Architecture Agent
    READ:  everything
    WRITE: docs/agent-runs/**

Validation Agent
    READ:  everything
    WRITE: docs/agent-runs/**

Orchestrator Agent
    READ:  everything
    WRITE: nothing

Release Agent
    READ:  everything
    WRITE: nothing
```

## Execution Capabilities

```text
Bash access: all agents except Specification.
Task delegation: only Orchestrator.
```

For the full operational reference, see `docs/guides/agent-usage.md`.
