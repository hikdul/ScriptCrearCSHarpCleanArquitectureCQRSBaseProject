
implementation-agent.md, refactor-agent.md, architecture-agent.md, validation-agent.md y finalmente release-agent.md.


| Agente         | Responsabilidad | Puede modificar producción | Puede modificar tests |
| -------------- | --------------- | -------------------------: | --------------------: |
| Orchestrator   | Coordinar       |                          ❌ |                     ❌ |
| Specification  | Especificación  |                          ❌ |                     ❌ |
| Test           | TDD / RED       |                          ❌ |                     ✅ |
| Implementation | GREEN           |                          ✅ |                     ❌ |
| Refactor       | Diseño          |                          ✅ |                     ❌ |
| Architecture   | Arquitectura    |                          ❌ |                     ❌ |
| Validation     | Validación      |                          ❌ |                     ❌ |
| Release        | GitFlow/release |                         ❌* |                     ❌ |

Test Agent
    READ:  todo
    WRITE: tests/**
    WRITE: docs/agent-runs/**

Implementation Agent
    READ:  todo
    WRITE: src/**
    WRITE: docs/agent-runs/**

Architecture Agent
    READ:  todo
    WRITE: docs/agent-runs/**

Validation Agent
    READ:  todo
    WRITE: docs/agent-runs/**
