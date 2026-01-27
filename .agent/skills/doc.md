# Antigravity Skills

> **Guide to creating and using Skills in the Antigravity Kit**

---

## 📋 Introduction

Antigravity Skills enable **Progressive Disclosure** - specialized knowledge packages that remain dormant until needed. Skills are only loaded into the agent's context when your request matches the skill's description, preventing "tool bloat" and keeping responses focused.

---

## 📁 Structure

Skills are folder-based packages located in `.agent/skills/`:

```
.agent/skills/
├── clean-code/
│   └── SKILL.md          # Lite: Single instruction file
├── vulnerability-scanner/
│   ├── SKILL.md          # Standard: Instructions + scripts
│   ├── checklists.md     # Reference file
│   └── scripts/
│       └── security_scan.py
└── app-builder/
    ├── SKILL.md          # Pro: Full package
    ├── templates/
    └── scripts/
```

### Skill Tiers

| Tier | Description | Components |
|------|-------------|------------|
| **Lite** | Instructions only | `SKILL.md` |
| **Standard** | Instructions + automation | `SKILL.md` + `scripts/` |
| **Pro** | Full package | `SKILL.md` + `scripts/` + `templates/` |

---

## 📝 SKILL.md Format

Every skill requires a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: skill-name
description: Brief description. Used for auto-routing.
tier: lite | standard | pro
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Skill Title

Content and instructions...
```

---

## 🔍 Example 1: Lite Skill (clean-code)

**Path:** `.agent/skills/clean-code/SKILL.md`

```markdown
---
name: clean-code
description: Pragmatic coding standards - concise, direct, no over-engineering
tier: lite
allowed-tools: Read, Write, Edit
---

# Clean Code Standards

## Core Principles

| Principle | Rule |
|-----------|------|
| **SRP** | Single Responsibility - each function does ONE thing |
| **DRY** | Don't Repeat Yourself - extract duplicates |
| **KISS** | Keep It Simple - simplest solution that works |

## Naming Rules

| Element | Convention |
|---------|------------|
| **Functions** | Verb + noun: `getUserById()` |
| **Booleans** | Question form: `isActive`, `hasPermission` |
```

---

## � Example 2: Standard Skill (vulnerability-scanner)

**Path:** `.agent/skills/vulnerability-scanner/`

```
vulnerability-scanner/
├── SKILL.md
├── checklists.md
└── scripts/
    └── security_scan.py
```

**SKILL.md:**

```markdown
---
name: vulnerability-scanner
description: OWASP 2025, Supply Chain Security, attack surface mapping
tier: standard
allowed-tools: Read, Glob, Grep, Bash
---

# Vulnerability Scanner

## Runtime Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `scripts/security_scan.py` | Automated security validation | `python scripts/security_scan.py <path>` |

## Reference Files

| File | Purpose |
|------|---------|
| `checklists.md` | OWASP Top 10, Auth, API checklists |
```

---

## ⚡ How Skills Are Used

1. **Agent receives request** → "Review this code for security issues"
2. **Router matches description** → `vulnerability-scanner` matches "security"
3. **Skill loads** → Instructions and tools become available
4. **Agent executes** → Follows skill instructions, runs scripts if needed

**Prompt:** `scan this project for security vulnerabilities`

The agent automatically identifies `vulnerability-scanner`, loads the skill, and runs `security_scan.py`.

---

## 📋 Skill Validation

Run the tier audit to verify all skills have valid tiers:

```bash
python .agent/scripts/skill_tier_audit.py
```

Expected output:
```
✅ All skills have tier defined!
  Total Skills: 35
  Pro:          3
  Standard:     16
  Lite:         16
```

---

## 🎯 Summary

| Skill Type | When to Use |
|------------|-------------|
| **Lite** | Simple rules and guidelines |
| **Standard** | Rules + automated validation scripts |
| **Pro** | Complete packages with templates and generators |

> **Remember:** Skills transform a general-purpose AI into a specialist for your project. Define once, apply automatically.