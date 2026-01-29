# Antigravity Kit Usage Guide

How to use the kit effectively with any LLM (including GPT).

---

## Operating modes

The kit has two operating modes:

| Mode | What it is | When to use | Overhead |
|---|---|---|---|
| **LITE** (default) | Fast, direct, low ceremony | Small fixes, small refactors | Low |
| **STRICT** | Validated, enterprise bar | Multi-file/risky work, pre-merge, production | High |

---

## LITE mode (default)

### Characteristics

- No automatic validation scripts (no checklist/tests/linters unless asked)
- No specialist agent invocations
- OOP + strong typing is always required
- Always end with a Conventional Commits suggestion (no blocking)

### When to use

- Small bug fix (< 20 lines changed)
- Add a small function/method
- Small refactor (rename, extract method)
- Config tweaks

### Output convention

End the answer with:

`Suggested commit: \`type(scope): short summary\``

Examples:

- `Suggested commit: \`fix(auth): handle missing token\``
- `Suggested commit: \`docs: clarify LITE vs STRICT\``

---

## STRICT mode

### Characteristics

- Runs the kit checklist and other validators when relevant
- May invoke specialist agents
- Provides an explicit "How to verify" section with exact commands

### How to activate

- `/strict`
- "be strict"
- "validate everything"
- "run the checks"

### Typical validations

```bash
# Full checklist (aggregates multiple validators)
python .agent/scripts/checklist.py .

# Security scan (can be run standalone)
python .agent/skills/vulnerability-scanner/scripts/security_scan.py .

# Commit message validation
python .agent/skills/commit-critic/scripts/commit_validator.py --message "feat: add X"

# PR analysis
python .agent/skills/commit-critic/scripts/pr_analyzer.py --base main
```

---

## Quick decision flow

```text
User request
  |
  v
Is it small and low-risk?
  |            |
 yes          no
  |            |
  v            v
 LITE        STRICT (or /orchestrate)
```

---

## References

- `.agent/rules/GEMINI.md`
- `.agent/rules/GEMINI-LITE.md`
- `docs/workflows.md`
