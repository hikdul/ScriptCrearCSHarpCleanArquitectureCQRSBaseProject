# Agents

The executable agent definitions live in `.opencode/agents/`. They are
OpenCode subagents with scoped permissions; the documentation in this
directory is the human-readable catalog, not a second copy of the prompts.

| File | Contents |
| --- | --- |
| `agents-list.md` | Agent responsibilities, edit scopes and delegation capabilities. |

The full operational reference is
[`../guides/agent-usage.md`](../guides/agent-usage.md).

## Why there is no per-agent copy here

Duplicating the full prompt of every agent in two places creates drift: one
copy gets updated, the other keeps an older workflow. The OpenCode files are
the ones that actually run, so they are the single source of truth. This
directory records only the catalog and the collaboration contract.

## Adding an agent

1. Add the definition to `.opencode/agents/<name>.md`.
2. Add a row to `agents-list.md`.
3. Update the command and permission table in `../guides/agent-usage.md`.
4. If the agent is product-specific, add its path to
   `tools/project-generator/config/opencode-exclude.txt` in the generator
   repository so future generated projects do not inherit it.
