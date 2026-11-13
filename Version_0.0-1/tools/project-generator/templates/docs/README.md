# Documentation

This directory holds the project's durable engineering documentation.

| Path | Purpose |
| --- | --- |
| `architecture/` | Layer rules, CQRS, repository/unit-of-work, controllers and testing strategy. |
| `workflows/` | Mandatory development workflows, including the TDP feature workflow and close sequence. |
| `guides/` | Operational guides. Start with `agent-usage.md`. |
| `agents/` | Agent catalog. The executable agent definitions live in `.opencode/agents/`. |
| `specifications/` | Feature source of truth. Start with `000-spec-example.md`. |
| `agent-runs/` | Optional per-run evidence written by agents. |

## Which document wins

When two documents disagree, use this order:

```text
AGENTS.md
    ↓
docs/specifications/<feature>.md
    ↓
docs/workflows/tdp-feature-workflow.md
    ↓
docs/architecture/
    ↓
docs/guides/
```

Code and executable tests are the final authority when prose and behavior
disagree. Never weaken a test or an architecture rule to match prose.

## Specifications

`docs/specifications/` is the only place where product behavior is defined.
The `000-spec-example.md` document is a format reference. Feature
specifications start at `001` and are numbered sequentially.

## Agent runs

`docs/agent-runs/` is optional. When an agent records a run, it keeps the
evidence (commands, test counts, files changed) rather than a narrative.
