# Antigravity Kit

> 🚀 Kit de expansão de capacidades para IA Agents - Foco Enterprise

Sistema modular de **agents**, **skills** e **workflows** para desenvolvimento Python on-premise.

---

## ⚡ Quick Start

```bash
# Validar integridade do kit
python .agent/scripts/kit_integrity_checker.py .agent

# Ver checklist de verificação
python .agent/scripts/checklist.py .
```

---

## 📦 Estrutura

```
.agent/
├── agents/       # 22 Specialist Agents
├── skills/       # 35 Domain Skills
├── workflows/    # 11 Slash Commands
├── scripts/      # 5 Master Scripts
└── rules/        # Global Rules
```

---

## 🎯 Foco Enterprise

| Área | Tecnologias |
|------|-------------|
| **Backend** | Python, FastAPI, APIs, integrações |
| **Database** | Oracle, ODBC, connection pooling |
| **Automação** | pywin32, COM, Selenium, Office |
| **ETL** | pandas, polars, pipelines |
| **Integração** | ERP sync, idempotência, retry patterns |

---

## 🤖 Agents Principais

| Agent | Foco |
|-------|------|
| `backend-specialist` | APIs Python, integrações |
| `database-connector` | Oracle, ODBC |
| `data-engineer` | ETL, pandas/polars |
| `automation-specialist` | Windows, COM |
| `office-integrator` | Excel, Word, PDF |
| `debugger` | Root cause analysis |
| `project-planner` | Task breakdown |
| `git-commit-specialist` | Conventional commits |

---

## 🧩 Skills Core

- `python-patterns` - Padrões Python modernos
- `api-patterns` - REST, GraphQL, contratos
- `database-connectors` - cx_Oracle, pyodbc
- `erp-integration-patterns` - Sync, idempotência
- `enterprise-automation` - Windows automation
- `office-integration` - Excel, Word, PDF

---

## 📋 Workflows

| Comando | Descrição |
|---------|-----------|
| `/plan` | Criar plano de implementação |
| `/create` | Criar nova aplicação |
| `/debug` | Modo debug sistemático |
| `/test` | Gerar e executar testes |
| `/deploy` | Deploy com checklist |

---

## 📖 Documentação

- [ARCHITECTURE.md](.agent/ARCHITECTURE.md) - Visão completa do kit
- [GEMINI.md](.agent/rules/GEMINI.md) - Regras globais da IA

---

## ✅ Validação

```bash
# Verificar referências quebradas
python .agent/scripts/kit_integrity_checker.py .agent

# Checklist completo
python .agent/scripts/checklist.py .
```

---

## 📜 License

MIT
