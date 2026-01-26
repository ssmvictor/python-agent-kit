# Antigravity Kit Architecture

> Comprehensive AI Agent Capability Expansion Toolkit

---

## 📋 Overview

Antigravity Kit is a modular system consisting of:

- **22 Specialist Agents** - Role-based AI personas
- **35 Skills** - Domain-specific knowledge modules (on-premise focused)
- **11 Workflows** - Slash command procedures
- **5 Master Scripts** - Validation and automation

---

## 🏗️ Directory Structure

```plaintext
.agent/
├── ARCHITECTURE.md          # This file
├── agents/                  # 19 Specialist Agents
├── skills/                  # 30 Skills
├── workflows/               # 11 Slash Commands
├── rules/                   # Global Rules
└── scripts/                 # 4 Master Scripts
```

---

## 🧩 Agents (22)

Specialist AI personas for different domains.

| Agent | Focus | Skills Used |
| ----- | ----- | ----------- |
| `orchestrator` | Multi-agent coordination | parallel-agents, behavioral-modes |
| `project-planner` | Discovery, task planning | brainstorming, plan-writing, architecture |
| `frontend-specialist` | Web UI/UX | frontend-design, tailwind-patterns |
| `backend-specialist` | API, business logic | api-patterns, python-patterns, database-design |
| `database-architect` | Schema, SQL | database-design |
| `devops-engineer` | On-premise deployment | deployment-procedures, scheduled-tasks |
| `security-auditor` | Security compliance | vulnerability-scanner, red-team-tactics |
| `penetration-tester` | Offensive security | red-team-tactics |
| `test-engineer` | Testing strategies | testing-patterns, tdd-workflow, webapp-testing |
| `debugger` | Root cause analysis | systematic-debugging |
| `performance-optimizer` | Speed, Web Vitals | performance-profiling |
| `documentation-writer` | Manuals, docs | documentation-templates |
| `product-manager` | Requirements, user stories | plan-writing, brainstorming |
| `product-owner` | Strategy, backlog, MVP | plan-writing, brainstorming |
| `qa-automation-engineer` | E2E testing, CI pipelines | webapp-testing, testing-patterns |
| `code-archaeologist` | Legacy code, refactoring | clean-code, code-review-checklist |
| `git-commit-specialist` | Git commits, PRs | commit-critic |
| `explorer-agent` | Codebase analysis | - |
| `data-engineer` | Data pipelines, pandas/polars | data-processing |
| `automation-specialist` | Windows automation, COM | enterprise-automation |
| `office-integrator` | Excel, Word, PDF generation | office-integration |
| `database-connector` | Database connectivity, pooling | database-connectors |

---

## 🧩 Skills (35)

Modular knowledge domains that agents can load on-demand based on task context.

### Frontend & UI

| Skill | Description |
| ----- | ----------- |
| `tailwind-patterns` | Tailwind CSS v4 utilities |
| `frontend-design` | UI/UX patterns, design systems |

### Backend & API

| Skill | Description |
| ----- | ----------- |
| `api-patterns` | REST, GraphQL, tRPC |
| `python-patterns` | Python standards, FastAPI |

### Database

| Skill | Description |
| ----- | ----------- |
| `database-design` | Schema design, optimization |
| `database-connectors` | pyodbc, cx_Oracle, connection pooling |


### On-Premise & Infrastructure

| Skill | Description |
| ----- | ----------- |
| `deployment-procedures` | On-premise deployment, Windows Server, IIS |
| `server-management` | Infrastructure management |
| `scheduled-tasks` | Windows Task Scheduler, Python scheduling |
| `file-integration` | UNC paths, network shares, file watchers |
| `enterprise-automation` | pywin32, COM, Selenium enterprise |
| `data-processing` | pandas, polars, ETL pipelines |
| `office-integration` | Excel, Word, PDF automation |
| `erp-integration-patterns` | ERP integrations, sync, idempotency |

### Testing & Quality

| Skill | Description |
| ----- | ----------- |
| `testing-patterns` | Testing strategies |
| `webapp-testing` | E2E, Playwright |
| `tdd-workflow` | Test-driven development |
| `code-review-checklist` | Code review standards |
| `lint-and-validate` | Linting, validation |

### Security

| Skill | Description |
| ----- | ----------- |
| `vulnerability-scanner` | Security auditing, OWASP |
| `red-team-tactics` | Offensive security |

### Architecture & Planning

| Skill | Description |
| ----- | ----------- |
| `app-builder` | Full-stack app scaffolding |
| `architecture` | System design patterns |
| `plan-writing` | Task planning, breakdown |
| `brainstorming` | Socratic questioning |


### Shell/CLI

| Skill | Description |
| ----- | ----------- |
| `powershell-windows` | Windows PowerShell |

### Other

| Skill | Description |
| ----- | ----------- |
| `clean-code` | Coding standards (Global) |
| `behavioral-modes` | Agent personas |
| `parallel-agents` | Multi-agent patterns |
| `mcp-builder` | Model Context Protocol |
| `documentation-templates` | Doc formats |
| `performance-profiling` | Web Vitals, optimization |
| `systematic-debugging` | Troubleshooting |
| `intelligent-routing` | Agent auto-selection |
| `commit-critic` | Git commit standards |

---

## 🔄 Workflows (11)

Slash command procedures. Invoke with `/command`.

| Command | Description |
| ------- | ----------- |
| `/brainstorm` | Socratic discovery |
| `/create` | Create new features |
| `/debug` | Debug issues |
| `/deploy` | Deploy application |
| `/enhance` | Improve existing code |
| `/orchestrate` | Multi-agent coordination |
| `/plan` | Task breakdown |
| `/preview` | Preview changes |
| `/status` | Check project status |
| `/test` | Run tests |
| `/ui-ux-pro-max` | Design with 50 styles |

---

## 🎯 Skill Loading Protocol

```plaintext
User Request → Skill Description Match → Load SKILL.md
                                            ↓
                                    Read references/
                                            ↓
                                    Read scripts/
```

### Skill Structure

```plaintext
skill-name/
├── SKILL.md           # (Required) Metadata & instructions
├── scripts/           # (Optional) Python/Bash scripts
├── references/        # (Optional) Templates, docs
└── assets/            # (Optional) Images, logos
```

### Skill Maturity Tiers

Skills are classified by maturity level based on their depth and structure:

| Tier | Criteria | Count |
|------|----------|-------|
| **Pro** | SKILL.md + references/ + scripts/ + assets (10+ files) | 3 |
| **Standard** | SKILL.md + references/ OR scripts/ (2-9 files) | 15 |
| **Lite** | SKILL.md only (1 file) | 16 |

#### 🏆 Pro Skills (3)

| Skill | Files |
|-------|-------|
| `app-builder` | 20 |
| `api-patterns` | 12 |
| `frontend-design` | 10 |

#### 📦 Standard Skills (15)

| Skill | Files | Skill | Files |
|-------|-------|-------|-------|
| `database-design` | 8 | `architecture` | 6 |
| `data-processing` | 6 | `database-connectors` | 5 |
| `enterprise-automation` | 5 | `office-integration` | 5 |
| `file-integration` | 3 | `scheduled-tasks` | 3 |
| `commit-critic` | 3 | `lint-and-validate` | 3 |
| `vulnerability-scanner` | 3 | `brainstorming` | 2 |
| `performance-profiling` | 2 | `testing-patterns` | 2 |
| `webapp-testing` | 2 | | |

#### 📄 Lite Skills (16)

`behavioral-modes`, `clean-code`, `code-review-checklist`, `deployment-procedures`, `documentation-templates`, `intelligent-routing`, `mcp-builder`, `parallel-agents`, `plan-writing`, `powershell-windows`, `python-patterns`, `red-team-tactics`, `server-management`, `systematic-debugging`, `tailwind-patterns`, `tdd-workflow`

**Audit script:** `python .agent/scripts/skill_tier_audit.py`

---

## 📝 Scripts (5)

Master validation scripts that orchestrate skill-level scripts.

### Master Scripts

| Script | Purpose | When to Use |
| ------ | ------- | ----------- |
| `checklist.py` | Priority-based validation (Core checks) | Development, pre-commit |
| `verify_all.py` | Comprehensive verification (All checks) | Pre-deployment, releases |
| `auto_preview.py` | Auto preview server management | Local development |
| `session_manager.py` | Session state management | Agent coordination |
| `kit_integrity_checker.py` | Validates agent/skill references | Pre-commit, CI |

### Usage

```bash
# Quick validation during development
python .agent/scripts/checklist.py .

# Full verification before deployment
python .agent/scripts/verify_all.py . --url http://localhost:3000
```

### What They Check

**checklist.py** (Core checks):

- Security (vulnerabilities, secrets)
- Code Quality (lint, types)
- Schema Validation
- Test Suite
- UX Audit
- SEO Check

**verify_all.py** (Full suite):

- Everything in checklist.py PLUS:
- Lighthouse (Core Web Vitals)
- Playwright E2E
- Bundle Analysis
- Mobile Audit
- i18n Check

For details, see [scripts/README.md](scripts/README.md)

---

## 📊 Statistics

| Metric | Value |
| ------ | ----- |
| **Total Agents** | 22 |
| **Total Skills** | 34 |
| **Total Workflows** | 11 |
| **Total Scripts** | 4 (master) + skill scripts |
| **Coverage** | Web, backend, security, testing, on-premise, data, automation |

---

## 🔗 Quick Reference

| Need | Agent | Skills |
| ---- | ----- | ------ |
| Web App | `frontend-specialist` | frontend-design, tailwind-patterns |
| API | `backend-specialist` | api-patterns, python-patterns |
| Database | `database-architect` | database-design |
| Security | `security-auditor` | vulnerability-scanner |
| Testing | `test-engineer` | testing-patterns, webapp-testing |
| Debug | `debugger` | systematic-debugging |
| Plan | `project-planner` | brainstorming, plan-writing |
| Git | `git-commit-specialist` | commit-critic |
