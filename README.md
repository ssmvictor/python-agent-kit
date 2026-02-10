# Antigravity Kit

> Enterprise-focused capability expansion kit for AI agents

A modular system of agents, skills, workflows, and validation scripts for on-premise Python development.
Compatible with **Antigravity/Claude Code** (native) and **OpenCode** (via `--target opencode`).

---

## Quick install (npm)

```bash
# Antigravity / Claude Code (default)
npx @ssmvictor/python-agent-kit init

# OpenCode
npx @ssmvictor/python-agent-kit init --target opencode

# Both platforms at once
npx @ssmvictor/python-agent-kit init --target both
```

This installs the `.agent` folder (and optionally `.opencode/` + `AGENTS.md`) into your current project.

---

## Quick start (after install)

```bash
# Validate kit integrity
python .agent/scripts/kit_integrity_checker.py .agent

# Full checklist (STRICT-style validation)
python .agent/scripts/checklist.py . --profile strict
```

---

## Installation

### Option 0: npm CLI (recommended)

```bash
# Current project (Antigravity / Claude Code)
npx @ssmvictor/python-agent-kit init

# Current project (OpenCode)
npx @ssmvictor/python-agent-kit init --target opencode

# Custom path
npx @ssmvictor/python-agent-kit init --path ./my-project
```

You can also install globally:

```bash
npm install -g @ssmvictor/python-agent-kit
python-agent-kit init
python-agent-kit init --target opencode
```

### Option 1: Local (per project)

Copy the `.agent` folder to your project root:

```bash
your-project/
├── .agent/      # ← paste here
├── src/
└── ...
```

### Option 2: Global (all projects)

Copy the contents of `.agent` to your user's Antigravity directory:

| OS | Path |
|---|---|
| **Windows** | `C:\Users\<USERNAME>\.gemini\antigravity\` |
| **Linux/macOS** | `~/.gemini/antigravity/` |

### Dependencies (profiles)

The kit now has 3 dependency profiles:

| Profile | File | Use when |
|---|---|---|
| **CORE** | `.agent/scripts/requirements-core.txt` | Default/LITE usage with minimum footprint |
| **STRICT** | `.agent/scripts/requirements-strict.txt` | Running enterprise checks (`/strict`, security, typed validation) |
| **EXTRAS** | `.agent/scripts/requirements-extras.txt` | Optional capabilities per skill (templating, search, data, task orchestration) |

Install commands:

```bash
# CORE (default)
pip install -r .agent/scripts/requirements-core.txt

# STRICT (includes CORE)
pip install -r .agent/scripts/requirements-strict.txt

# EXTRAS (includes CORE)
pip install -r .agent/scripts/requirements-extras.txt
```

Backward compatibility:

- `.agent/scripts/requirements.txt` now points to CORE (`-r requirements-core.txt`)

`rich` remains the only mandatory baseline dependency. The kit fails fast with install instructions if Rich is missing. `print()` is only allowed for machine-readable `--json` output paths.

### npm CLI commands

| Command | Purpose |
|---|---|
| `python-agent-kit init` | Install `.agent` into a project |
| `python-agent-kit update` | Replace existing installation with latest templates |
| `python-agent-kit status` | Check installation status (detects both `.agent` and `.opencode`) |

Common options:

```bash
python-agent-kit init --force
python-agent-kit init --path ./my-project
python-agent-kit init --branch main
python-agent-kit init --quiet
python-agent-kit init --dry-run
python-agent-kit init --target opencode
python-agent-kit init --target both
```

### Target platforms (`--target`)

| Target | Installs | Use with |
|---|---|---|
| `antigravity` (default) | `.agent/` | Antigravity, Claude Code |
| `opencode` | `.opencode/` + `AGENTS.md` | OpenCode |
| `both` | `.agent/` + `.opencode/` + `AGENTS.md` | Multiple editors |

When using `--target opencode` or `--target both`, the CLI automatically:

1. Downloads the `.agent/` source of truth from the repository
2. Transforms agent frontmatter (CSV tools → YAML map, adds `mode: subagent`)
3. Converts workflows to OpenCode commands (`.opencode/commands/`)
4. Adapts skills (keeps `name` + `description`, already compatible)
5. Copies scripts and rules with internal path references updated
6. Generates an `AGENTS.md` root file with project-level instructions

---

## Operating modes

The kit supports two operating modes:

- **LITE** (default): fast and direct; no automatic validators; ends with a suggested commit message.
- **STRICT** (opt-in via `/strict`): runs validations and includes a "How to verify" section.

See `docs/USAGE.md`.

---

## Structure

### Antigravity (`.agent/`) — source of truth

```text
.agent/
├── agents/     # Specialist agents
├── skills/     # Domain skills
├── workflows/  # Slash command procedures
├── scripts/    # Validation + automation scripts
└── rules/      # Global rules
```

### OpenCode (`.opencode/`) — auto-generated via `--target opencode`

```text
.opencode/
├── agents/     # Specialist agents (mode: subagent, tools as YAML map)
├── commands/   # Slash commands (converted from workflows)
├── skills/     # Domain skills (name + description frontmatter)
├── scripts/    # Validation + automation scripts
└── rules/      # Global rules
AGENTS.md       # Project-level instructions (root file)
```

> `.opencode/` is **never** the source of truth. Always edit `.agent/` and re-run
> `python-agent-kit init --target opencode` to regenerate.

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
- `database-connectors` - oracledb, pyodbc
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
