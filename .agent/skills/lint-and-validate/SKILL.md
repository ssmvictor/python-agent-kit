---
name: lint-and-validate
description: Automatic quality control, linting, and static analysis procedures. Use after every code modification to ensure syntax correctness and project standards. Triggers onKeywords: lint, format, check, validate, types, static analysis.
tier: standard
allowed-tools: Read, Glob, Grep, Bash
---

# Lint and Validate Skill

> Terminology follows [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

> **Requirement:** Run appropriate validation tools after EVERY code change. Do not finish a task until the code is error-free.
...
## The Quality Loop
1. **Write/Edit Code**
2. **Run Audit:** `npm run lint && npx tsc --noEmit`
3. **Analyze Report:** Check the "FINAL AUDIT REPORT" section.
4. **Fix & Repeat:** Submitting code with "FINAL AUDIT" failures MUST NOT be done.

## Error Handling
...
---
**Rule:** No code SHOULD be committed or reported as "done" without passing these checks.


---

## Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `scripts/lint_runner.py` | Unified lint check | `python scripts/lint_runner.py <project_path>` |
| `scripts/type_coverage.py` | Type coverage analysis | `python scripts/type_coverage.py <project_path>` |

