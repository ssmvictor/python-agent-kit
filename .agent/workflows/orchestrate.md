---
description: Coordinate multiple specialist agents for multi-domain/high-stakes work. Strict by design.
---

# /orchestrate — Multi-Agent (Strict)

$ARGUMENTS

---

## When to use

- Multi-domain changes (backend + DB + security + UI)
- Large refactors / migrations
- Incident response / deep debugging
- “I need high confidence” work

---

## Orchestration rules

1. **Minimum specialists:** involve **≥ 3** domain agents (pick from: backend, frontend, database, security, devops, debugger, code-archaeologist).
2. **Clear handoffs:** each specialist must return:
   - findings
   - concrete recommendations
   - risks/edge cases
3. **Validation is mandatory:** run at least:
   - `python .agent/skills/vulnerability-scanner/scripts/security_scan.py .`
   - `python .agent/skills/lint-and-validate/scripts/lint_runner.py .`
   - plus tests when code changed:
     - `python .agent/skills/testing-patterns/scripts/test_runner.py .`

If execution isn’t possible, output the exact commands and what “success” looks like.

---

## Workflow

1. **Problem brief**
   - restate goal, constraints, acceptance criteria

2. **Specialist passes**
   - Security pass
   - Architecture/backend pass
   - DB/schema pass (if applicable)
   - Frontend/UX pass (if applicable)
   - DevOps/deploy pass (if applicable)

3. **Synthesis**
   - merge recommendations into a single plan
   - identify conflicts and choose a direction

4. **Verification plan**
   - list commands to run
   - define exit criteria

---

## Output format

```markdown
## 🧠 Orchestration Report

### Goal
...

### Specialists engaged
- @security-auditor: ...
- @backend-specialist: ...
- @database-architect: ...

### Findings (by domain)
...

### Unified plan
1. ...
2. ...

### Verification
- `python .agent/skills/vulnerability-scanner/scripts/security_scan.py .`
- `python .agent/skills/lint-and-validate/scripts/lint_runner.py .`
- `python .agent/skills/testing-patterns/scripts/test_runner.py .`

### Exit criteria
- ...
```

