---
trigger: simple_tasks
---

# GEMINI-LITE.md - Fast Path for Small Tasks

> Use this mode for straightforward work: small bug fixes, adding a small function, small refactors.

## When to use this mode

Enable LITE when:
- Bug fixes with a small diff (< 20 changed lines)
- Add small functions/methods
- Small refactors (rename, extract method)
- Config tweaks
- Typing/lint fixes

## LITE rules (fast by default)

### 1) Do not run validation scripts by default

- Do not run `.agent/scripts/checklist.py`
- Do not run tests automatically
- Do not run linters unless the user explicitly asks
- If the user asks you to create a commit/PR, follow the commit gate rules in `.agent/rules/GEMINI.md`

### 2) Do not invoke other agents

- Solve directly without delegating
- Do not use `@git-commit-specialist` for simple tasks unless you're creating a commit/PR
- Do not escalate to `orchestrator` unless the user asks or the scope is clearly multi-domain

### 3) OOP + strong typing (non-negotiable)

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b
```

### 4) Always include a commit suggestion (no blocking)

At the end of a LITE response, output a Conventional Commits suggestion:

`Suggested commit: \`type(scope): short summary\``

- Use `fix`, `feat`, `refactor`, `docs`, `test`, or `chore`
- If scope is unclear, omit it: `fix: ...`

### 5) Be direct

- Code first, minimal explanation
- Focus on the solution, not the process

## When to escalate out of LITE

Escalate to `/strict` or `/orchestrate` when:
- Changes span multiple files (> 5 files)
- New features across modules/APIs
- Deploy/production work
- Security-related changes (auth, input validation)
- Large refactors (architectural changes)
- The user explicitly asks for strictness ("be strict", "validate everything")
