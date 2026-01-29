# Antigravity Kit Architecture

> Comprehensive AI Agent Capability Expansion Toolkit

---

## Overview

Antigravity Kit is a modular system consisting of:

- Specialist agents - role-based AI personas
- Skills - domain-specific knowledge modules (on-premise focused)
- Workflows - slash command procedures (see `docs/workflows.md`)
- Scripts - validation and automation helpers (see `.agent/scripts`)

---

## Directory structure

```plaintext
.agent/
├── ARCHITECTURE.md          # This file
├── agents/                  # Specialist agents
├── skills/                  # Skills
├── workflows/               # Workflows (slash commands)
├── rules/                   # Global rules
└── scripts/                 # Core scripts
```

---

## Agents

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

## Skills

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

## Workflows

Slash command procedures in `.agent/workflows/`. Invoke with `/command`.

| Command | Description |
| ------- | ----------- |
| `/test` | Run tests consistently |
| `/deploy` | Deploy with checklist and rollback planning |
| `/strict` | Enterprise bar validation (security + lint + tests) |
| `/orchestrate` | Multi-agent coordination |

See `docs/workflows.md` for details and examples.

---

## Skill loading protocol

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

### Skill maturity tiers

Skills are classified by maturity level based on their depth and structure:

| Tier | Criteria |
|------|----------|
| **Pro** | SKILL.md + references/ + scripts/ + assets (10+ files) |
| **Standard** | SKILL.md + references/ OR scripts/ (2-9 files) |
| **Lite** | SKILL.md only (1 file) |

To list skills by tier (and validate that every skill defines a tier), run:

`python .agent/scripts/skill_tier_audit.py`

---

## Scripts

Master validation scripts that orchestrate skill-level scripts.

### Core scripts

| Script | Purpose | When to Use |
| ------ | ------- | ----------- |
| `kit_integrity_checker.py` | Validates agent/skill references + frontmatter | Pre-commit, CI |
| `checklist.py` | Priority-based validation (Core checks) | Development, pre-commit |
| `verify_all.py` | Comprehensive verification (All checks) | Pre-deployment, releases |
| `auto_preview.py` | Auto preview server management | Local development |
| `session_manager.py` | Session state management | Agent coordination |
| `skill_tier_audit.py` | Lists skills by tier | Maintenance |

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

If a URL is provided, it also runs:

- Lighthouse (Core Web Vitals)
- Playwright E2E

**verify_all.py** (Full suite):

- Everything in checklist.py PLUS:
- Accessibility Check
- Type Coverage

For details, see the script docstrings in `.agent/scripts`.

---

## Statistics

| Metric | Value |
| ------ | ----- |
| **Total Agents** | 22 |
| **Total Skills** | 35 |
| **Total Workflows** | 4 |
| **Total Scripts** | 6 (core) + skill scripts |
| **Coverage** | Web, backend, security, testing, on-premise, data, automation |

---

## Quick reference

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
