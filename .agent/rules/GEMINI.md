---
trigger: always_on
---

# GEMINI.md - Antigravity Kit (Minimal Always-On)

> Goal: keep the default experience fast and low-friction.
> Strict/enterprise behavior is opt-in via workflows like `/strict`, `/test`, `/deploy`, `/orchestrate`.

## Operating modes

- Default is LITE: solve directly, keep overhead near-zero, and do not run validators unless asked.
- STRICT is opt-in: use `/strict` (or an explicit request like "be strict" / "validate everything") when you need full validation.
- For simple tasks, end the answer with a Conventional Commits suggestion (no blocking).
- Reference: `docs/USAGE.md` and `.agent/rules/GEMINI-LITE.md`.

## Always-On Rules (small, enforceable)

1. **Progressive disclosure (no bloat):** Only load/read agents/skills when they are clearly relevant. Do not "preload everything".
2. **Fast by default:** Start with the shortest path to a correct result. Avoid long ceremonies for small requests.
3. **Clarify only when necessary:** Ask <= 2 questions. Otherwise state assumptions and proceed.
4. **Respect explicit user control:** If the user invokes `@agent` or a `/workflow`, follow it exactly.
5. **High-risk operations:** For destructive actions (data loss, credential changes, prod deploy), pause and confirm. Prefer `/deploy` for releases.
6. **Truthfulness & scope:** Don't claim you ran commands you didn't run. If execution isn't possible, provide exact commands and expected outputs.
7. **Deliver working increments:** Prefer small diffs, runnable steps, and a clear "how to verify" section.
8. **Use kit checks only when warranted:** Run/require `.agent/scripts/checklist.py` and other validators only in strict workflows or when the user asks.
9. **Artifacts over prose:** For complex work, produce a concrete plan/checklist. Avoid vague generalities.
10. **Security hygiene:** Never print secrets. Flag obvious secret leaks and recommend rotation.
11. **Git commit gate:** Before creating a commit (`git commit`) or a Pull Request:
    - Invoke `@git-commit-specialist` to analyze staged changes.
    - Run `python .agent/skills/commit-critic/scripts/commit_validator.py` for commits.
    - Run `python .agent/skills/commit-critic/scripts/pr_analyzer.py` for PRs.
    - Do not proceed if validation returns a BLOCKED status.
    - **Exempt (no gate needed):** `git status`, `git diff`, `git log`, `git push`, `git pull`, `git fetch`, `git branch`, `git checkout`, `git stash`, and other read/navigation commands.
12. **OOP + strong typing mandate:** All generated code MUST use:
    - **Python:** classes (dataclasses/Pydantic preferred), type hints on all functions/methods, and `from __future__ import annotations`.
    - **TypeScript:** `strict: true`, interfaces/types for all data structures, and no `any`.
    - **Other typed languages:** equivalent OOP + typing patterns.
    - **Exceptions:** HTML/CSS/JSON/config files are exempt (not programming languages).

## When to escalate into workflows

- **Multiple domains / higher stakes** -> `/orchestrate`
- **Tests / coverage / CI failures** -> `/test`
- **Deployment / release / production** -> `/deploy`
- **You want "enterprise bar"** on any change -> `/strict`
