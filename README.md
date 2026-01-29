# Antigravity Kit

> Enterprise-focused capability expansion kit for AI agents

A modular system of agents, skills, workflows, and validation scripts for on-premise Python development.

---

## Quick start

```bash
# Validate kit integrity
python .agent/scripts/kit_integrity_checker.py .agent

# Full checklist (STRICT-style validation)
python .agent/scripts/checklist.py .
```

---

## Operating modes

The kit supports two operating modes:

- **LITE** (default): fast and direct; no automatic validators; ends with a suggested commit message.
- **STRICT** (opt-in via `/strict`): runs validations and includes a "How to verify" section.

See `docs/USAGE.md`.

---

## Structure

```text
.agent/
├── agents/     # Specialist agents
├── skills/     # Domain skills
├── workflows/  # Slash command procedures
├── scripts/    # Validation + automation scripts
└── rules/      # Global rules
```

---

## Enterprise focus

| Area | Technologies |
|---|---|
| **Backend** | Python, FastAPI, APIs, integrations |
| **Database** | Oracle, ODBC, connection pooling |
| **Automation** | pywin32, COM, Selenium, Office |
| **ETL** | pandas, polars, pipelines |
| **Integration** | ERP sync, idempotency, retry patterns |

---

## Key agents

| Agent | Focus |
|---|---|
| `backend-specialist` | Python APIs, integrations |
| `database-connector` | Oracle, ODBC |
| `data-engineer` | ETL, pandas/polars |
| `automation-specialist` | Windows, COM |
| `office-integrator` | Excel, Word, PDF |
| `debugger` | Root cause analysis |
| `project-planner` | Task breakdown |
| `git-commit-specialist` | Conventional commits |

---

## Core skills

- `python-patterns` - Modern Python patterns
- `api-patterns` - REST, GraphQL, contracts
- `database-connectors` - cx_Oracle, pyodbc
- `erp-integration-patterns` - Sync, idempotency
- `enterprise-automation` - Windows automation
- `office-integration` - Excel, Word, PDF

---

## Workflows

| Command | Purpose |
|---|---|
| `/test` | Run tests consistently (and help triage failures) |
| `/deploy` | Production deployment checklist + rollback planning |
| `/strict` | Enterprise bar: security + lint + tests |
| `/orchestrate` | Multi-agent coordination for multi-domain changes |

---

## Documentation

- `docs/USAGE.md` - Operating modes (LITE/STRICT)
- `docs/workflows.md` - Workflow reference
- `docs/AGENTS.md` - Agent catalog
- `docs/SKILLS.md` - Skill catalog
- `.agent/ARCHITECTURE.md` - Architecture overview
- `.agent/rules/GEMINI.md` - Always-on rules

---

## License

MIT
