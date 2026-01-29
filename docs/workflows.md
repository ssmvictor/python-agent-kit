# Antigravity Kit Workflow Reference

This document describes the available workflows (slash commands) in `.agent/workflows/`, when to use each one, and practical examples.

---

## Overview

Workflows are "ways of working" triggered by commands like `/test`, `/deploy`, `/strict`, etc. They standardize process and output format, reducing ambiguity and improving predictability for engineering tasks.

> Philosophy: fast by default. Workflows are reserved for high-confidence validation, deployment, and multi-agent orchestration.

### Quick map (intent -> workflow)

| You want... | Use |
|---|---|
| Run tests, generate coverage, triage failures | `/test` |
| Deploy with a checklist and rollback plan | `/deploy` |
| Enterprise bar validation: security + lint + tests | `/strict` |
| Coordinate multiple specialists (3+ agents) | `/orchestrate` |

---

## 1) `/test` - Tests (Generate + Run + Triage)

**Goal:** run tests consistently (Python/Node), optionally generate tests for changed code, and triage failures quickly.

**When to use:**
- Before refactoring: protect behavior.
- When fixing a bug: add a regression test.
- To increase confidence in a new feature.
- To check coverage and identify weak spots.

**Actions (via arguments):**
- `run` (default): runs the test suite
- `coverage`: runs with coverage report
- `generate`: creates tests for the described change, then runs
- `e2e`: runs Playwright (for web apps)

**Commands executed:**
```bash
# Run suite
python .agent/skills/testing-patterns/scripts/test_runner.py .

# Coverage
python .agent/skills/testing-patterns/scripts/test_runner.py . --coverage

# E2E (web)
python .agent/skills/webapp-testing/scripts/playwright_runner.py .
```

**Examples:**
```text
/test
/test coverage
/test generate for user authentication
/test e2e
```

---

## 2) `/deploy` - Production Deployment (Strict)

**Goal:** deploy safely with pre-checks, execution steps, and a rollback plan.

**When to use:**
- Publish staging for external validation.
- Deploy to production with a minimum checklist (lint, tests, audit).
- Roll back quickly.

**Required information (ask if missing):**
1. Target environment: **staging** or **production**
2. Deployment surface: Vercel / Netlify / Fly.io / Docker / Other
3. A URL to validate (staging/prod) or a local preview URL (for perf/e2e)

**Pre-flight (required):**
1. Summarize what is being deployed (commits, changes, risk areas)
2. Run validations:
   - `python .agent/scripts/checklist.py .`
   - If you have a URL: `python .agent/scripts/checklist.py . --url <URL>`
3. Stop conditions: if Security/Lint fails, do not proceed

**Supported platforms:**
- **Vercel**: `vercel --prod`
- **Netlify**: `netlify deploy --prod`
- **Fly.io**: `fly deploy`
- **Docker**: `docker compose pull && docker compose up -d`

**Examples:**
```text
/deploy staging to Vercel
/deploy production
/deploy production --url https://app.example.com
```

---

## 3) `/strict` - Enterprise Bar (Opt-in)

**Goal:** strict validation with predictable output: security + lint + tests, plus remediation guidance.

**When to use:**
- When the user explicitly requests strict/enterprise/production-grade.
- Before critical merges.
- To ensure the enterprise bar on an important change.

**This workflow is opt-in.** Do not apply it unless the user invokes `/strict` or explicitly asks for strictness.

**Procedure:**
1. Summarize the change (scope, risk areas, affected modules)
2. Run the kit checklist:
   - `python .agent/scripts/checklist.py .`
   - If you have a URL: `python .agent/scripts/checklist.py . --url <URL>`
3. Interpret results (priority order):
   1. Security
   2. Lint / type checks
   3. Schema validation (if applicable)
   4. Tests
   5. UX / accessibility (if applicable)
4. Remediate: fix critical blockers first (Security/Lint)
5. Exit criteria:
   - `checklist.py` returns success
   - Provide a "How to verify" section with exact commands

**Examples:**
```text
/strict
/strict for authentication module
/strict --url https://staging.example.com
```

---

## 4) `/orchestrate` - Multi-Agent (Strict)

**Goal:** coordinate specialists for multi-domain or high-confidence work.

**When to use:**
- Multi-domain changes (backend + DB + security + UI).
- Large refactors / migrations.
- Incident response / deep debugging.
- When the user needs "high confidence".

**Orchestration rules:**
1. Minimum specialists: involve >= 3 domain agents (backend, frontend, database, security, devops, debugger, code-archaeologist)
2. Clear handoffs: each specialist returns:
   - findings
   - concrete recommendations
   - risks/edge cases
3. Validation is required: execute at least:
   - `python .agent/skills/vulnerability-scanner/scripts/security_scan.py .`
   - `python .agent/skills/lint-and-validate/scripts/lint_runner.py .`
   - `python .agent/skills/testing-patterns/scripts/test_runner.py .` (when code changes)

**Workflow:**
1. Problem brief: goal, constraints, acceptance criteria
2. Specialist passes: security, architecture/backend, DB/schema, frontend/UX, devOps/deploy (as applicable)
3. Synthesis: merge recommendations into a single plan, identify conflicts
4. Verification plan: list commands and define exit criteria

**Examples:**
```text
/orchestrate refactor authentication system
/orchestrate migrate from Firebase to PostgreSQL
/orchestrate security audit for payment module
```

---

## Removed workflows (migrated to normal mode)

The following workflows were removed and their functionality moved into the normal agent mode:

| Workflow | Alternative |
|---|---|
| `/brainstorm` | Ask direct questions in normal mode; the agent will explore options naturally. |
| `/plan` | Use `/orchestrate` with a planning focus, or ask for a plan in normal mode. |
| `/create` | Use normal mode to create apps; escalate to `/orchestrate` if complex. |
| `/enhance` | Use normal mode to evolve apps; the agent will infer current state. |
| `/debug` | Use normal mode; describe the error and the agent will investigate systematically. |
| `/preview` | Use normal mode; ask to start the preview server. |
| `/status` | Use normal mode; ask for project status. |
| `/ui-ux-pro-max` | Use normal mode for UI/UX work; the agent will apply design rules. |

---

## Philosophy

> Fast by default, strict when needed.

- Normal mode: for most tasks (build, debug, plan, enhance). Fast, direct, low ceremony.
- Workflows (`/test`, `/deploy`, `/strict`, `/orchestrate`): for validation, deployment, and high-confidence orchestration.

Pick the workflow based on risk and complexity, not habit.
