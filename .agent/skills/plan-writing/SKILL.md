---
name: plan-writing
description: Structured task planning with clear breakdowns, dependencies, and verification criteria. Use when implementing features, refactoring, or any multi-step work.
tier: lite
allowed-tools: Read, Glob, Grep
---

# Plan Writing

> Terminology follows [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

> Source: obra/superpowers

## Overview
...
## Planning Principles (NOT Templates!)

> **Requirement:** NO fixed templates. Each plan is UNIQUE to the task.

### Principle 1: Keep It SHORT
...
### Principle 4: Scripts Are Project-Specific

> **Constraint:** You MUST NOT copy-paste script commands. Choose based on project type.


| Project Type | Relevant Scripts |
|--------------|------------------|
| Frontend/React | `ux_audit.py`, `accessibility_checker.py` |
| Backend/API | `api_validator.py`, `security_scan.py` |
| Mobile | `mobile_audit.py` |
| Database | `schema_validator.py` |
| Full-stack | Mix of above based on what you touched |

**Wrong:** Adding all scripts to every plan
**Right:** Only scripts relevant to THIS task

---

### Principle 5: Verification is Simple

| ❌ Wrong | ✅ Right |
|----------|----------|
| "Verify the component works correctly" | "Run `npm run dev`, click button, see toast" |
| "Test the API" | "curl localhost:3000/api/users returns 200" |
| "Check styles" | "Open browser, verify dark mode toggle works" |

---

## Plan Structure (Flexible, Not Fixed!)

```
# [Task Name]

## Goal
One sentence: What are we building/fixing?

## Tasks
- [ ] Task 1: [Specific action] → Verify: [How to check]
- [ ] Task 2: [Specific action] → Verify: [How to check]
- [ ] Task 3: [Specific action] → Verify: [How to check]

## Done When
- [ ] [Main success criteria]
```

> **That's it.** No phases, no sub-sections unless truly needed.
> Keep it minimal. Add complexity only when required.

## Notes
[Any important considerations]
```

---

## Best Practices (Quick Reference)

1. **Start with goal** - What are we building/fixing?
2. **Max 10 tasks** - If more, break into multiple plans
3. **Each task verifiable** - Clear "done" criteria
4. **Project-specific** - No copy-paste templates
5. **Update as you go** - Mark `[x]` when complete

---

## When to Use

- New project from scratch
- Adding a feature
- Fixing a bug (if complex)
- Refactoring multiple files
