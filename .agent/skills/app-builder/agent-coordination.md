# Agent Coordination

> How App Builder orchestrates specialist agents.

## Agent Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   APP BUILDER (Orchestrator)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     PROJECT PLANNER                          │
│  • Task breakdown                                            │
│  • Dependency graph                                          │
│  • File structure planning                                   │
│  • Create {task-slug}.md in project root                     │
...
│              CHECKPOINT: PLAN VERIFICATION                   │
│  VERIFY: Does {task-slug}.md exist in project root?          │
│  If NO → STOP → Create plan file first                       │
│  If YES → Proceed to specialist agents                       │
...
> **CRITICAL:** Phase 1.5 is REQUIRED. No specialist agents proceed without PLAN.md verification.

