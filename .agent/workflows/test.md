---
description: Test workflow: run, generate, or improve tests. Uses kit scripts to keep it language/framework agnostic.
---

# /test — Tests (Generate + Run + Triage)

$ARGUMENTS

---

## Intent

- Run tests consistently (Python/Node)
- Generate missing tests for changed code
- Triage failures quickly
- Optionally check coverage / E2E

---

## Decide the action (from $ARGUMENTS)

- `run` (default): run test suite
- `coverage`: run with coverage
- `generate`: create tests for the described change, then run
- `e2e`: run Playwright (web apps)

If ambiguous, assume **run**.

---

## Commands (kit standard)

### Run suite
- `python .agent/skills/testing-patterns/scripts/test_runner.py .`

### Coverage
- `python .agent/skills/testing-patterns/scripts/test_runner.py . --coverage`

### E2E (web)
- `python .agent/skills/webapp-testing/scripts/playwright_runner.py .`

> If the project uses a specific runner (pytest/jest/vitest), the script will detect and use it.

---

## Failure triage (required when red)

1. Identify the **first failing test** and reproduce in isolation
2. Categorize:
   - flaky / timing
   - data dependency
   - breaking change (API/schema)
   - environment/config
3. Fix with minimal change
4. Re-run the same command until green

---

## Output format

```markdown
## 🧪 Test Report

### Action
run | coverage | generate | e2e

### Commands
- ...

### Results
- Passed: ...
- Failed: ...
- Notes: ...

### Fixes applied (if any)
- ...

### Verification
- Re-ran: `...`
```

