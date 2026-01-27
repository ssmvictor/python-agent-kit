---
name: clean-code
description: Pragmatic coding standards - concise, direct, no over-engineering, no unnecessary comments
tier: lite
allowed-tools: Read, Write, Edit
version: 2.0
priority: CRITICAL
---

# Clean Code - Pragmatic AI Coding Standards

> Terminology follows [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

> **CRITICAL SKILL** - Be **concise, direct, and solution-focused**.

---
...
## Before Editing ANY File (THINK FIRST!)

**Before changing a file, ask yourself:**
...
> **Rule:** You MUST edit the file + all dependent files in the SAME task.
> **Rule:** You MUST NOT leave broken imports or missing updates.

---

## Summary
...
---

## Self-Check Before Completing

**Before saying "task complete", you MUST verify:**

| Check | Question |
|-------|----------|
| ✅ **Goal met?** | Did I do exactly what user asked? |
| ✅ **Files edited?** | Did I modify all necessary files? |
| ✅ **Code works?** | Did I test/verify the change? |
| ✅ **No errors?** | Lint and TypeScript pass? |
| ✅ **Nothing forgotten?** | Any edge cases missed? |

> **Rule:** If ANY check fails, you MUST fix it before completing.

---

## Verification Scripts

> **Requirement:** Each agent runs ONLY their own skill's scripts after completing work.

### Agent → Script Mapping
...
---

### Script Output Handling (READ → SUMMARIZE → ASK)

**When running a validation script, you MUST:**

1. **Run the script** and capture ALL output.
2. **Parse the output** - identify errors, warnings, and passes.
3. **Summarize to user** in this format:

```markdown
## Script Results: [script_name.py]
...
```

4. **Wait for user confirmation** before fixing.
5. **After fixing** → Re-run script to confirm.

> **VIOLATION:** Running script and ignoring output = FAILED task.
> **VIOLATION:** Auto-fixing without asking is MUST NOT be done.
> **Rule:** You MUST always READ output → SUMMARIZE → ASK → then fix.


