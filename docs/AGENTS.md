# Agent Documentation (`.agent/agents`)

This document describes the agents defined in `.agent/agents/`. Each agent is a specialized profile (with allowed tools and recommended skills) meant to execute a class of tasks consistently.

## How to read this folder

- Each `*.md` file is an agent definition (with YAML frontmatter containing `name`, `description`, `tools`, `skills`, etc.).
- Workflows (for example, `/deploy`, `/strict`, `/orchestrate`) may invoke agents; agents may load skills as needed.

## Important conventions

### Frontmatter fields

- `name`: agent identifier.
- `description`: what the agent does (often includes activation keywords).
- `tools`: allowed tools (for example: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Agent`).
- `skills`: skills the agent tends to load/use.

### Recommended context template (when invoking an agent)

Use this package to reduce questions and speed up execution:

```text
GOAL:
- (what you want at the end)

CONTEXT:
- relevant repo/folder:
- stack (Python/Node/etc):
- OS/environment:

CONSTRAINTS:
- required standards (typing/mypy, lint, etc):
- compatibility (versions):

ACCEPTANCE CRITERIA:
- (how to validate it is done)

FILES/ENTRY POINTS:
- (paths or names)

ERROR/LOG (for debugging):
- (stack trace, reproduction steps)
```

## Agent catalog

| Agent | File | Category | Triggers | Skills | Tools |
| --- | --- | --- | --- | --- | --- |
| `automation-specialist` | `.agent/agents/automation-specialist.md` | Engineering (Apps, Data, Automation) | - | `enterprise-automation`, `python-patterns`, `clean-code`, `powershell-windows`, `scheduled-tasks` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `backend-specialist` | `.agent/agents/backend-specialist.md` | Engineering (Apps, Data, Automation) | `backend`, `server`, `api`, `endpoint`, `database`, `auth` | `clean-code`, `python-patterns`, `api-patterns`, `database-design`, `mcp-builder`, `lint-and-validate`, `powershell-windows` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `code-archaeologist` | `.agent/agents/code-archaeologist.md` | Orchestration & Discovery | `legacy`, `refactor`, `undocumented`, `old code`, `monolith`, `spaghetti` | `clean-code`, `architecture`, `systematic-debugging`, `documentation-templates`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `data-engineer` | `.agent/agents/data-engineer.md` | Engineering (Apps, Data, Automation) | - | `data-processing`, `database-connectors`, `clean-code`, `python-patterns`, `lint-and-validate` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `database-architect` | `.agent/agents/database-architect.md` | Engineering (Apps, Data, Automation) | `database`, `schema`, `migration`, `sql`, `performance`, `index` | `database-design`, `clean-code`, `architecture`, `performance-profiling`, `lint-and-validate` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `database-connector` | `.agent/agents/database-connector.md` | Engineering (Apps, Data, Automation) | - | `database-connectors`, `database-design`, `python-patterns`, `clean-code` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `debugger` | `.agent/agents/debugger.md` | Quality, Testing & Debug | `debug`, `bug`, `error`, `traceback`, `crash`, `broken` | `systematic-debugging`, `clean-code`, `testing-patterns`, `lint-and-validate`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `devops-engineer` | `.agent/agents/devops-engineer.md` | DevOps & Operations | `deploy`, `server`, `ci/cd`, `docker`, `production`, `ops` | `deployment-procedures`, `server-management`, `scheduled-tasks`, `powershell-windows`, `vulnerability-scanner`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `documentation-writer` | `.agent/agents/documentation-writer.md` | Documentation | - | `documentation-templates`, `clean-code`, `architecture` | `Read`, `Write`, `Edit` |
| `explorer-agent` | `.agent/agents/explorer-agent.md` | Orchestration & Discovery | - | `intelligent-routing`, `architecture`, `clean-code`, `documentation-templates` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `frontend-specialist` | `.agent/agents/frontend-specialist.md` | Engineering (Apps, Data, Automation) | `frontend`, `react`, `next`, `ui`, `component`, `tailwind` | `frontend-design`, `tailwind-patterns`, `performance-profiling`, `webapp-testing`, `lint-and-validate` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `git-commit-specialist` | `.agent/agents/git-commit-specialist.md` | Quality, Testing & Debug | - | `commit-critic`, `clean-code`, `documentation-templates` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `office-integrator` | `.agent/agents/office-integrator.md` | Engineering (Apps, Data, Automation) | - | `office-integration`, `clean-code`, `python-patterns` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `orchestrator` | `.agent/agents/orchestrator.md` | Orchestration & Discovery | - | `clean-code`, `parallel-agents`, `behavioral-modes`, `plan-writing`, `brainstorming`, `architecture`, `lint-and-validate`, `powershell-windows`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`, `Agent` |
| `penetration-tester` | `.agent/agents/penetration-tester.md` | Security | `pentest`, `penetration`, `exploit`, `red team`, `vulnerability`, `security testing` | `red-team-tactics`, `vulnerability-scanner`, `api-patterns`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `performance-optimizer` | `.agent/agents/performance-optimizer.md` | DevOps & Operations | `performance`, `slow`, `optimize`, `bundle`, `cwv`, `lighthouse` | `performance-profiling`, `frontend-design`, `clean-code`, `lint-and-validate` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `product-manager` | `.agent/agents/product-manager.md` | Product & Planning | `requirements`, `user story`, `acceptance criteria`, `scope`, `mvp`, `stakeholders` | `brainstorming`, `plan-writing`, `documentation-templates` | `Read`, `Write`, `Edit` |
| `product-owner` | `.agent/agents/product-owner.md` | Product & Planning | `priorities`, `backlog`, `roadmap`, `stakeholder`, `trade-offs`, `delivery` | `brainstorming`, `plan-writing`, `documentation-templates` | `Read`, `Write`, `Edit` |
| `project-planner` | `.agent/agents/project-planner.md` | Product & Planning | - | `clean-code`, `app-builder`, `plan-writing`, `brainstorming` | `Read`, `Grep`, `Glob`, `Bash` |
| `qa-automation-engineer` | `.agent/agents/qa-automation-engineer.md` | Quality, Testing & Debug | - | `webapp-testing`, `testing-patterns`, `clean-code`, `lint-and-validate`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `security-auditor` | `.agent/agents/security-auditor.md` | Security | - | `vulnerability-scanner`, `red-team-tactics`, `api-patterns`, `clean-code`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `test-engineer` | `.agent/agents/test-engineer.md` | Quality, Testing & Debug | - | `testing-patterns`, `tdd-workflow`, `clean-code`, `lint-and-validate`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |

## Practical mapping: workflow -> typical agents

| Workflow | Typical agents | Notes |
|---|---|---|
| `/test` | `test-engineer`, `qa-automation-engineer` | Test strategy, execution, triage. |
| `/deploy` | `devops-engineer`, `security-auditor` | Deployment checklist + safety/rollback; security when relevant. |
| `/strict` | `orchestrator` (as needed), `security-auditor`, `test-engineer` | Enterprise-bar validation and remediation. |
| `/orchestrate` | `orchestrator` + domain agents | Multi-domain changes, high confidence. |

## Notes

- Some agent files may include abbreviated sections (for example, `...`). This document focuses on what is visible in frontmatter and a pragmatic overview.
- If you want an exact, per-agent summary based on the full text of each file, generate it by reading and summarizing `.agent/agents/*.md`.
