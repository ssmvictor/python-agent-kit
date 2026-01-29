# Skill Documentation (`.agent/skills`)

This document describes the contents of `.agent/skills/`: what each skill is for, when to use it, and where the relevant files live (docs, scripts, templates).

Each skill is a self-contained package that supports progressive disclosure: load/read only what is relevant to the current task.

---

## Folder structure

In general, each skill follows this pattern:

- `.agent/skills/<skill>/SKILL.md` -> primary document (goal, rules, checklists)
- `.agent/skills/<skill>/*.md` -> additional references (optional)
- `.agent/skills/<skill>/scripts/*` -> executable utilities (optional)
- `.agent/skills/app-builder/templates/*` -> project templates (when applicable)

There is also a general guide: `.agent/skills/doc.md`.

---

## Quick reference

| Skill | Category | Tier | Scripts |
|---|---|---|---|
| `api-patterns` | APIs | `pro` | `api_validator.py` |
| `app-builder` | App building | `pro` | - |
| `architecture` | Architecture | `standard` | - |
| `behavioral-modes` | Orchestration & modes | `lite` | - |
| `brainstorming` | Requirements discovery | `lite` | - |
| `clean-code` | Code quality | `lite` | - |
| `code-review-checklist` | Code quality | `lite` | - |
| `commit-critic` | Code quality | `standard` | `commit_validator.py`, `pr_analyzer.py` |
| `data-processing` | Data | `standard` | `data_quality_checker.py`, `schema_validator.py` |
| `database-connectors` | Data | `standard` | `connection_tester.py` |
| `database-design` | Data | `standard` | `schema_validator.py` |
| `deployment-procedures` | Ops/Deployment | `lite` | - |
| `documentation-templates` | Documentation | `lite` | - |
| `enterprise-automation` | Enterprise automation | `standard` | `automation_validator.py` |
| `erp-integration-patterns` | Integrations | `standard` | - |
| `file-integration` | Integrations | `standard` | - |
| `frontend-design` | Frontend/UX | `pro` | `accessibility_checker.py`, `ux_audit.py` |
| `intelligent-routing` | Orchestration & modes | `lite` | - |
| `lint-and-validate` | Code quality | `standard` | `lint_runner.py`, `type_coverage.py` |
| `mcp-builder` | Integrations | `lite` | - |
| `office-integration` | Enterprise automation | `standard` | `document_generator.py` |
| `parallel-agents` | Orchestration & modes | `lite` | - |
| `performance-profiling` | Quality/Performance | `standard` | `lighthouse_audit.py` |
| `plan-writing` | Planning | `lite` | - |
| `powershell-windows` | Ops/Windows | `lite` | - |
| `python-patterns` | Python | `lite` | - |
| `red-team-tactics` | Security | `lite` | - |
| `scheduled-tasks` | Ops/Windows | `standard` | - |
| `server-management` | Ops/Deployment | `lite` | - |
| `systematic-debugging` | Debug | `lite` | - |
| `tailwind-patterns` | Frontend/UX | `lite` | - |
| `tdd-workflow` | Testing | `lite` | - |
| `testing-patterns` | Testing | `standard` | `test_runner.py` |
| `vulnerability-scanner` | Security | `standard` | `security_scan.py` |
| `webapp-testing` | Testing | `standard` | `playwright_runner.py` |

---

## How to use a skill

1. Start from `.agent/skills/<skill>/SKILL.md`.
2. Only read deeper references/scripts when they are relevant to the task.
3. If a skill includes scripts, prefer running them with an explicit project path. Example:

```bash
python .agent/skills/vulnerability-scanner/scripts/security_scan.py .
```

---

## Maintenance

To audit tiers (and ensure every skill defines a tier), run:

```bash
python .agent/scripts/skill_tier_audit.py
```
