---
description: Opt-in strictness: run kit validations + produce a remediation plan. Use for “enterprise bar” changes.
---

# /strict — Enterprise Bar (Opt‑in)

$ARGUMENTS

---

## Intent

Use this workflow when you want **predictability and rigor**: security + lint + (optional) schema + tests, with a clear remediation report.

This workflow is **opt‑in**. Do not apply it unless the user explicitly calls `/strict` or asks for “rigor/enterprise/production‑grade”.

---

## Inputs

- **Target:** what changed / what you want validated (`$ARGUMENTS`)
- **Optional URL:** if you have a running preview/staging URL, include it in the arguments (used for perf checks).

---

## Procedure

1. **Summarize the change**
   - One paragraph: scope, risk areas, affected modules.

2. **Run the kit checklist**
   - Core checks:
     - `python .agent/scripts/checklist.py .`
   - If a URL is provided:
     - `python .agent/scripts/checklist.py . --url <URL>`

3. **Interpret results (priority order)**
   1) Security
   2) Lint / type checks
   3) Schema validation (if applicable)
   4) Tests
   5) UX / accessibility (if applicable)

4. **Remediate**
   - Fix **Critical** blockers first (Security/Lint).
   - Re-run checklist after each meaningful fix.

5. **Exit criteria**
   - ✅ `checklist.py` returns success
   - ✅ Provide a short “Verification” section with the exact commands run

---

## Output format

```markdown
## ✅ Strict Report

### Scope
...

### Checks executed
- ...

### Findings
| Priority | Check | Status | Notes | Fix |
|---|---|---|---|---|

### Verification
- `python .agent/scripts/checklist.py .`
- `python .agent/scripts/checklist.py . --url ...` (if used)

### Next steps
- ...
```

