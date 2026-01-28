# Documentação de Agents (`.agent/agents`)

Esta documentação descreve os **agents** definidos em `.agent/agents/`. Cada agent é um perfil especializado (com ferramentas permitidas e skills recomendadas) para executar uma classe de tarefas com consistência.

## Como ler esta pasta

- Cada arquivo `*.md` é um agent (com frontmatter YAML contendo `name`, `description`, `tools`, `skills`, etc.).
- **Workflows** (ex.: `/create`, `/debug`, `/deploy`) normalmente invocam **agents**; e agents, por sua vez, consultam **skills** para executar o trabalho com regras/checklists.

## Convenções importantes

### Frontmatter (o que significa)

- `name`: identificador do agent.
- `description`: resumo do papel do agent (muitas vezes inclui palavras-chave de ativação).
- `tools`: ferramentas habilitadas (ex.: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`, `Agent`).
- `skills`: skills que o agent tende a carregar/usar ao executar.

### Template de contexto recomendado (para invocar um agent)

Use este “pacote” para reduzir perguntas e acelerar execução:

```text
OBJETIVO:
- (o que você quer no final)

CONTEXTO:
- repo/pasta relevante:
- stack (Python/Node/etc):
- OS/ambiente:

RESTRIÇÕES:
- padrões obrigatórios (tipagem/mypy, lint, etc):
- compatibilidade (versões):

CRITÉRIO DE ACEITE:
- (como validar que ficou pronto)

ARQUIVOS/PONTOS DE ENTRADA:
- (paths ou nomes)

ERRO/LOG (se for debug):
- (stack trace, passos de reprodução)
```

## Catálogo de agents

| Agente | Arquivo | Categoria | Gatilhos | Skills | Ferramentas |
| --- | --- | --- | --- | --- | --- |
| `automation-specialist` | `.agent/agents/automation-specialist.md` | Engenharia (App, Dados, Automação) | — | `enterprise-automation`, `python-patterns`, `clean-code`, `powershell-windows`, `scheduled-tasks` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `backend-specialist` | `.agent/agents/backend-specialist.md` | Engenharia (App, Dados, Automação) | `backend`, `server`, `api`, `endpoint`, `database`, `auth` | `clean-code`, `python-patterns`, `api-patterns`, `database-design`, `mcp-builder`, `lint-and-validate`, `powershell-windows` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `code-archaeologist` | `.agent/agents/code-archaeologist.md` | Orquestração & Descoberta | `legacy`, `refactor`, `undocumented`, `old code`, `monolith`, `spaghetti` | `clean-code`, `architecture`, `systematic-debugging`, `documentation-templates`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `data-engineer` | `.agent/agents/data-engineer.md` | Engenharia (App, Dados, Automação) | — | `data-processing`, `database-connectors`, `clean-code`, `python-patterns`, `lint-and-validate` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `database-architect` | `.agent/agents/database-architect.md` | Engenharia (App, Dados, Automação) | `database`, `schema`, `migration`, `sql`, `performance`, `index` | `database-design`, `clean-code`, `architecture`, `performance-profiling`, `lint-and-validate` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `database-connector` | `.agent/agents/database-connector.md` | Engenharia (App, Dados, Automação) | — | `database-connectors`, `database-design`, `python-patterns`, `clean-code` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `debugger` | `.agent/agents/debugger.md` | Qualidade, Testes & Debug | `debug`, `bug`, `error`, `traceback`, `crash`, `broken` | `systematic-debugging`, `clean-code`, `testing-patterns`, `lint-and-validate`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `devops-engineer` | `.agent/agents/devops-engineer.md` | DevOps & Operações | `deploy`, `server`, `ci/cd`, `docker`, `production`, `ops` | `deployment-procedures`, `server-management`, `scheduled-tasks`, `powershell-windows`, `vulnerability-scanner`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `documentation-writer` | `.agent/agents/documentation-writer.md` | Documentação | — | `documentation-templates`, `clean-code`, `architecture` | `Read`, `Write`, `Edit` |
| `explorer-agent` | `.agent/agents/explorer-agent.md` | Orquestração & Descoberta | — | `intelligent-routing`, `architecture`, `clean-code`, `documentation-templates` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `frontend-specialist` | `.agent/agents/frontend-specialist.md` | Engenharia (App, Dados, Automação) | `frontend`, `react`, `next`, `ui`, `component`, `tailwind` | `frontend-design`, `tailwind-patterns`, `performance-profiling`, `webapp-testing`, `lint-and-validate` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `git-commit-specialist` | `.agent/agents/git-commit-specialist.md` | Qualidade, Testes & Debug | — | `commit-critic`, `clean-code`, `documentation-templates` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `office-integrator` | `.agent/agents/office-integrator.md` | Engenharia (App, Dados, Automação) | — | `office-integration`, `clean-code`, `python-patterns` | `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `orchestrator` | `.agent/agents/orchestrator.md` | Orquestração & Descoberta | — | `clean-code`, `parallel-agents`, `behavioral-modes`, `plan-writing`, `brainstorming`, `architecture`, `lint-and-validate`, `powershell-windows`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`, `Agent` |
| `penetration-tester` | `.agent/agents/penetration-tester.md` | Segurança | `pentest`, `penetration`, `exploit`, `red team`, `vulnerability`, `security testing` | `red-team-tactics`, `vulnerability-scanner`, `api-patterns`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `performance-optimizer` | `.agent/agents/performance-optimizer.md` | DevOps & Operações | `performance`, `slow`, `optimize`, `bundle`, `cwv`, `lighthouse` | `performance-profiling`, `frontend-design`, `clean-code`, `lint-and-validate` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `product-manager` | `.agent/agents/product-manager.md` | Produto & Planejamento | `requirements`, `user story`, `acceptance criteria`, `scope`, `mvp`, `stakeholders` | `brainstorming`, `plan-writing`, `documentation-templates` | `Read`, `Write`, `Edit` |
| `product-owner` | `.agent/agents/product-owner.md` | Produto & Planejamento | `priorities`, `backlog`, `roadmap`, `stakeholder`, `trade-offs`, `delivery` | `brainstorming`, `plan-writing`, `documentation-templates` | `Read`, `Write`, `Edit` |
| `project-planner` | `.agent/agents/project-planner.md` | Produto & Planejamento | — | `clean-code`, `app-builder`, `plan-writing`, `brainstorming` | `Read`, `Grep`, `Glob`, `Bash` |
| `qa-automation-engineer` | `.agent/agents/qa-automation-engineer.md` | Qualidade, Testes & Debug | — | `webapp-testing`, `testing-patterns`, `clean-code`, `lint-and-validate`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `security-auditor` | `.agent/agents/security-auditor.md` | Segurança | — | `vulnerability-scanner`, `red-team-tactics`, `api-patterns`, `clean-code`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |
| `test-engineer` | `.agent/agents/test-engineer.md` | Qualidade, Testes & Debug | — | `testing-patterns`, `tdd-workflow`, `clean-code`, `lint-and-validate`, `python-patterns` | `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write` |

## Agents por categoria (com quando usar e exemplo de prompt)

### Orquestração & Descoberta

#### `code-archaeologist`
- **Arquivo**: `.agent/agents/code-archaeologist.md`
- **Descrição**: Expert in legacy code, refactoring, and understanding undocumented systems. Use for reverse-engineering, modernization, and risk mitigation.
- **Gatilhos (keywords)**: `legacy`, `refactor`, `undocumented`, `old code`, `monolith`, `spaghetti`
- **Skills carregadas**: `clean-code`, `architecture`, `systematic-debugging`, `documentation-templates`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Entender **código legado** ou sem documentação (mapa de módulos, fluxos, side-effects).
  - Planejar **refatoração segura** (estrangular, modularizar, reduzir acoplamento).
  - Diagnosticar dívidas técnicas e riscos (hotspots, dependências cíclicas, pontos frágeis).

**Exemplo de prompt**:
```text
Use o agent `code-archaeologist` para: Entender **código legado** ou sem documentação (mapa de módulos, fluxos, side-effects). Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `explorer-agent`
- **Arquivo**: `.agent/agents/explorer-agent.md`
- **Descrição**: Advanced codebase discovery, deep architectural analysis, and proactive research. Use when starting a new task in unfamiliar codebases or complex repos.
- **Skills carregadas**: `intelligent-routing`, `architecture`, `clean-code`, `documentation-templates`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Fazer **descoberta de codebase**: localizar arquivos relevantes, entender arquitetura e fluxos.
  - Levantar dependências, pontos de extensão e áreas de risco antes de mudanças grandes.
  - Produzir um “mapa” rápido do projeto para apoiar planejamento/implementação.

**Exemplo de prompt**:
```text
Use o agent `explorer-agent` para: Fazer **descoberta de codebase**: localizar arquivos relevantes, entender arquitetura e fluxos. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `orchestrator`
- **Arquivo**: `.agent/agents/orchestrator.md`
- **Descrição**: Multi-agent coordination and task orchestration. Use when a task requires multiple agents or cross-cutting changes.
- **Skills carregadas**: `clean-code`, `parallel-agents`, `behavioral-modes`, `plan-writing`, `brainstorming`, `architecture`, `lint-and-validate`, `powershell-windows`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Write`, `Edit`, `Agent`
- **Use quando**:
  - Coordenar múltiplos agentes e consolidar resultados (planejamento + execução + verificação).
  - Definir checkpoints (aprovação do usuário) e garantir que scripts/validações sejam executados.
  - Gerenciar handoffs (contexto, decisões, outputs) para evitar retrabalho.

**Exemplo de prompt**:
```text
Use o agent `orchestrator` para: Coordenar múltiplos agentes e consolidar resultados (planejamento + execução + verificação). Entregue passos claros, checklists e o que precisar alterar no repo.
```

### Produto & Planejamento

#### `product-manager`
- **Arquivo**: `.agent/agents/product-manager.md`
- **Descrição**: Expert in product requirements, user stories, and acceptance criteria. Use for defining scope, MVP, and product planning.
- **Gatilhos (keywords)**: `requirements`, `user story`, `acceptance criteria`, `scope`, `mvp`, `stakeholders`
- **Skills carregadas**: `brainstorming`, `plan-writing`, `documentation-templates`
- **Ferramentas permitidas**: `Read`, `Write`, `Edit`
- **Use quando**:
  - Converter pedidos vagos em requisitos claros, user stories e critérios de aceitação.
  - Definir escopo, MVP, prioridades e riscos (impacto vs esforço).
  - Alinhar linguagem técnica ↔ negócio para orientar execução.

**Exemplo de prompt**:
```text
Use o agent `product-manager` para: Converter pedidos vagos em requisitos claros, user stories e critérios de aceitação. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `product-owner`
- **Arquivo**: `.agent/agents/product-owner.md`
- **Descrição**: Strategic facilitator bridging business needs and technical execution. Expert in prioritization, roadmap planning, and stakeholder alignment.
- **Gatilhos (keywords)**: `priorities`, `backlog`, `roadmap`, `stakeholder`, `trade-offs`, `delivery`
- **Skills carregadas**: `brainstorming`, `plan-writing`, `documentation-templates`
- **Ferramentas permitidas**: `Read`, `Write`, `Edit`
- **Use quando**:
  - Facilitar decisões e priorização com stakeholders (backlog, roadmap, trade-offs).
  - Definir “definition of done” e critérios de aceite por feature.
  - Manter consistência do produto com visão e restrições reais.

**Exemplo de prompt**:
```text
Use o agent `product-owner` para: Facilitar decisões e priorização com stakeholders (backlog, roadmap, trade-offs). Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `project-planner`
- **Arquivo**: `.agent/agents/project-planner.md`
- **Descrição**: Smart project planning agent. Breaks down user requests into tasks, plans file structure, and ensures execution order is clear. Use when starting new projects or planning major features.
- **Skills carregadas**: `clean-code`, `app-builder`, `plan-writing`, `brainstorming`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`
- **Use quando**:
  - Quebrar o trabalho em tarefas, dependências e etapas, gerando **arquivos de plano**.
  - Planejamento de features grandes (sem escrever código no modo plano).
  - Organizar naming/estrutura de planos e critérios de verificação.

**Exemplo de prompt**:
```text
Use o agent `project-planner` para: Quebrar o trabalho em tarefas, dependências e etapas, gerando **arquivos de plano**. Entregue passos claros, checklists e o que precisar alterar no repo.
```

### Engenharia (App, Dados, Automação)

#### `automation-specialist`
- **Arquivo**: `.agent/agents/automation-specialist.md`
- **Descrição**: Windows automation expert. pywin32, COM objects, Selenium for enterprise apps, scripting for legacy systems. Specializes in business process automation, legacy system integration, and desktop automation.
- **Skills carregadas**: `enterprise-automation`, `python-patterns`, `clean-code`, `powershell-windows`, `scheduled-tasks`
- **Ferramentas permitidas**: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`
- **Use quando**:
  - Automação em **Windows** (apps desktop/legados) com foco em robustez (retries, logs, idempotência).
  - Integrações por **COM/Office/pywin32** e/ou automação web (ex.: Selenium) quando fizer sentido.
  - Criação de rotinas agendadas e execução não-interativa (Task Scheduler).

**Exemplo de prompt**:
```text
Use o agent `automation-specialist` para: Automação em **Windows** (apps desktop/legados) com foco em robustez (retries, logs, idempotência). Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `backend-specialist`
- **Arquivo**: `.agent/agents/backend-specialist.md`
- **Descrição**: Expert Python backend architect for APIs, integrations, and enterprise systems.
- **Gatilhos (keywords)**: `backend`, `server`, `api`, `endpoint`, `database`, `auth`
- **Skills carregadas**: `clean-code`, `python-patterns`, `api-patterns`, `database-design`, `mcp-builder`, `lint-and-validate`, `powershell-windows`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Projetar/implementar **APIs** (REST) e regras de negócio no backend.
  - Integrações com serviços externos/ERPs e padronização de contratos (erros, paginação, versionamento).
  - Autenticação/autorização e hardening básico (validação, rate limit, logs).

**Exemplo de prompt**:
```text
Use o agent `backend-specialist` para: Projetar/implementar **APIs** (REST) e regras de negócio no backend. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `data-engineer`
- **Arquivo**: `.agent/agents/data-engineer.md`
- **Descrição**: Python data engineering specialist. ETL pipelines, pandas/polars processing, data validation, and enterprise data integrations.
- **Skills carregadas**: `data-processing`, `database-connectors`, `clean-code`, `python-patterns`, `lint-and-validate`
- **Ferramentas permitidas**: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`
- **Use quando**:
  - Construir pipelines **ETL/ELT** (pandas/polars) com validações e contratos de dados.
  - Checagem de qualidade (schema, nulos, ranges) e padronização de transformações idempotentes.
  - Preparar dados para relatórios/analytics e integração com bancos/arquivos.

**Exemplo de prompt**:
```text
Use o agent `data-engineer` para: Construir pipelines **ETL/ELT** (pandas/polars) com validações e contratos de dados. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `database-architect`
- **Arquivo**: `.agent/agents/database-architect.md`
- **Descrição**: Expert database architect for schema design, query optimization, migrations, and performance tuning.
- **Gatilhos (keywords)**: `database`, `schema`, `migration`, `sql`, `performance`, `index`
- **Skills carregadas**: `database-design`, `clean-code`, `architecture`, `performance-profiling`, `lint-and-validate`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Modelagem de **schema**, constraints, chaves e índices.
  - Planejar migrações e revisar performance de consultas (estratégia de índices e anti-patterns).
  - Definir padrões de acesso (ORM vs SQL) e governança de mudanças no banco.

**Exemplo de prompt**:
```text
Use o agent `database-architect` para: Modelagem de **schema**, constraints, chaves e índices. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `database-connector`
- **Arquivo**: `.agent/agents/database-connector.md`
- **Descrição**: Database connectivity specialist. pyodbc, cx_Oracle, pymssql, connection pooling, retry logic, and enterprise database access patterns. Use for enterprise database integration with proper typing.
- **Skills carregadas**: `database-connectors`, `database-design`, `python-patterns`, `clean-code`
- **Ferramentas permitidas**: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`
- **Use quando**:
  - Implementar conectividade robusta a bancos (ex.: **pyodbc/cx_Oracle**) com pooling/retry/timeouts.
  - Padronizar strings de conexão e segurança (segredos, variáveis de ambiente).
  - Garantir queries parametrizadas e uso correto de context managers.

**Exemplo de prompt**:
```text
Use o agent `database-connector` para: Implementar conectividade robusta a bancos (ex.: **pyodbc/cx_Oracle**) com pooling/retry/timeouts. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `frontend-specialist`
- **Arquivo**: `.agent/agents/frontend-specialist.md`
- **Descrição**: Senior Frontend Architect who builds maintainable React/Next.js systems with performance, accessibility, and clean UI design.
- **Gatilhos (keywords)**: `frontend`, `react`, `next`, `ui`, `component`, `tailwind`
- **Skills carregadas**: `frontend-design`, `tailwind-patterns`, `performance-profiling`, `webapp-testing`, `lint-and-validate`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Construção de UI em **React/Next.js** com foco em manutenibilidade e performance.
  - Design de componentes, estados (loading/empty/error), acessibilidade e responsividade.
  - Otimizações de bundle e melhores práticas de UX para produção.

**Exemplo de prompt**:
```text
Use o agent `frontend-specialist` para: Construção de UI em **React/Next.js** com foco em manutenibilidade e performance. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `office-integrator`
- **Arquivo**: `.agent/agents/office-integrator.md`
- **Descrição**: Office document automation specialist. Excel, Word, PDF generation and manipulation. Use for enterprise reporting and document workflows.
- **Skills carregadas**: `office-integration`, `clean-code`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`
- **Use quando**:
  - Geração/manipulação de **Excel/Word/PDF** para relatórios e artefatos corporativos.
  - Automação de templates, merge de dados e validação de layout.
  - Padronizar pipeline de documentos com classes e testes simples.

**Exemplo de prompt**:
```text
Use o agent `office-integrator` para: Geração/manipulação de **Excel/Word/PDF** para relatórios e artefatos corporativos. Entregue passos claros, checklists e o que precisar alterar no repo.
```

### Qualidade, Testes & Debug

#### `debugger`
- **Arquivo**: `.agent/agents/debugger.md`
- **Descrição**: Expert in systematic debugging, root cause analysis, and crash investigation.
- **Gatilhos (keywords)**: `debug`, `bug`, `error`, `traceback`, `crash`, `broken`
- **Skills carregadas**: `systematic-debugging`, `clean-code`, `testing-patterns`, `lint-and-validate`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Investigar bugs com método (reproduzir → isolar → causa raiz → correção → prevenção).
  - Analisar stack traces, logs e regressões após mudanças recentes.
  - Produzir fix + teste de regressão (quando aplicável).

**Exemplo de prompt**:
```text
Use o agent `debugger` para: Investigar bugs com método (reproduzir → isolar → causa raiz → correção → prevenção). Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `git-commit-specialist`
- **Arquivo**: `.agent/agents/git-commit-specialist.md`
- **Descrição**: Especialista em commits e PRs seguindo Conventional Commits. Valida, critica e sugere melhorias no histórico do repositório.
- **Skills carregadas**: `commit-critic`, `clean-code`, `documentation-templates`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Validar commits e PRs com **Conventional Commits** (escopo, breaking changes, mensagens).
  - Auditar PR para sinais de risco (mudanças perigosas, arquivos grandes, padrões ruins).
  - Sugerir melhoria de histórico para release notes e automações.

**Exemplo de prompt**:
```text
Use o agent `git-commit-specialist` para: Validar commits e PRs com **Conventional Commits** (escopo, breaking changes, mensagens). Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `qa-automation-engineer`
- **Arquivo**: `.agent/agents/qa-automation-engineer.md`
- **Descrição**: Specialist in test automation infrastructure and E2E testing. Focuses on Playwright, CI integration, and reducing flakiness.
- **Skills carregadas**: `webapp-testing`, `testing-patterns`, `clean-code`, `lint-and-validate`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Infra de testes automatizados (E2E) com Playwright e pipelines de execução.
  - Desenhar smoke tests, fixtures, mocks e estratégia de confiabilidade (flakiness).
  - Integração de testes em CI e relatórios de falhas.

**Exemplo de prompt**:
```text
Use o agent `qa-automation-engineer` para: Infra de testes automatizados (E2E) com Playwright e pipelines de execução. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `test-engineer`
- **Arquivo**: `.agent/agents/test-engineer.md`
- **Descrição**: Expert in testing, TDD, and test automation. Use for writing tests, improving coverage, and test strategy.
- **Skills carregadas**: `testing-patterns`, `tdd-workflow`, `clean-code`, `lint-and-validate`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Escrever testes (unit/integration) e aplicar TDD quando apropriado.
  - Aumentar cobertura e criar testes de regressão para bugs.
  - Padronizar estratégia de testes e organização do suite.

**Exemplo de prompt**:
```text
Use o agent `test-engineer` para: Escrever testes (unit/integration) e aplicar TDD quando apropriado. Entregue passos claros, checklists e o que precisar alterar no repo.
```

### DevOps & Operações

#### `devops-engineer`
- **Arquivo**: `.agent/agents/devops-engineer.md`
- **Descrição**: Expert in deployment, server management, CI/CD, and production operations. CRITICAL: ensures safe deployment with rollback plans.
- **Gatilhos (keywords)**: `deploy`, `server`, `ci/cd`, `docker`, `production`, `ops`
- **Skills carregadas**: `deployment-procedures`, `server-management`, `scheduled-tasks`, `powershell-windows`, `vulnerability-scanner`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Definir/operar **deploy**, CI/CD, ambientes (staging/prod) e rollback.
  - Gerenciar runtime (processos, health checks, logs, observabilidade).
  - Automatizar build/release e reduzir risco operacional com checklists.

**Exemplo de prompt**:
```text
Use o agent `devops-engineer` para: Definir/operar **deploy**, CI/CD, ambientes (staging/prod) e rollback. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `performance-optimizer`
- **Arquivo**: `.agent/agents/performance-optimizer.md`
- **Descrição**: Expert in performance optimization, profiling, Core Web Vitals, and bundle optimization. Use for making apps fast.
- **Gatilhos (keywords)**: `performance`, `slow`, `optimize`, `bundle`, `cwv`, `lighthouse`
- **Skills carregadas**: `performance-profiling`, `frontend-design`, `clean-code`, `lint-and-validate`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Otimização de performance (profiling, gargalos, regressões) e métricas web (Core Web Vitals).
  - Revisão de bundle (tree-shaking, split, lazy) e performance de renderização.
  - Criar backlog de melhorias priorizadas por impacto.

**Exemplo de prompt**:
```text
Use o agent `performance-optimizer` para: Otimização de performance (profiling, gargalos, regressões) e métricas web (Core Web Vitals). Entregue passos claros, checklists e o que precisar alterar no repo.
```

### Segurança

#### `penetration-tester`
- **Arquivo**: `.agent/agents/penetration-tester.md`
- **Descrição**: Expert in offensive security, penetration testing, red team operations, and vulnerability exploitation. Use only for authorized testing.
- **Gatilhos (keywords)**: `pentest`, `penetration`, `exploit`, `red team`, `vulnerability`, `security testing`
- **Skills carregadas**: `red-team-tactics`, `vulnerability-scanner`, `api-patterns`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Avaliar segurança de forma **ofensiva** em ambientes autorizados (pentest/red team), reportando riscos e evidências.
  - Priorizar vetores comuns (OWASP, auth/session, input validation, SSRF/IDOR) com ética e escopo definido.
  - Gerar recomendações de mitigação e reteste após correções.

**Exemplo de prompt**:
```text
Use o agent `penetration-tester` para: Avaliar segurança de forma **ofensiva** em ambientes autorizados (pentest/red team), reportando riscos e evidências. Entregue passos claros, checklists e o que precisar alterar no repo.
```

#### `security-auditor`
- **Arquivo**: `.agent/agents/security-auditor.md`
- **Descrição**: Elite cybersecurity expert. Think like an attacker, defend like an expert. OWASP Top 10, secure coding, configuration hardening, and incident response.
- **Skills carregadas**: `vulnerability-scanner`, `red-team-tactics`, `api-patterns`, `clean-code`, `python-patterns`
- **Ferramentas permitidas**: `Read`, `Grep`, `Glob`, `Bash`, `Edit`, `Write`
- **Use quando**:
  - Auditoria defensiva (OWASP, configuração, supply chain) e hardening.
  - Revisão de código para vulnerabilidades comuns e melhorias de postura de segurança.
  - Gerar relatório priorizado com correções recomendadas e validações.

**Exemplo de prompt**:
```text
Use o agent `security-auditor` para: Auditoria defensiva (OWASP, configuração, supply chain) e hardening. Entregue passos claros, checklists e o que precisar alterar no repo.
```

### Documentação

#### `documentation-writer`
- **Arquivo**: `.agent/agents/documentation-writer.md`
- **Descrição**: Expert in technical documentation. Use ONLY when user explicitly requests documentation.
- **Skills carregadas**: `documentation-templates`, `clean-code`, `architecture`
- **Ferramentas permitidas**: `Read`, `Write`, `Edit`
- **Use quando**:
  - Produzir documentação técnica (README, runbook, ADR, guias) **quando explicitamente solicitado**.
  - Padronizar estrutura e linguagem de docs para o repositório.
  - Gerar instruções de setup, troubleshooting e operação.

**Exemplo de prompt**:
```text
Use o agent `documentation-writer` para: Produzir documentação técnica (README, runbook, ADR, guias) **quando explicitamente solicitado**. Entregue passos claros, checklists e o que precisar alterar no repo.
```

## Mapeamento prático: workflow → agents típicos

| Workflow | Agents mais comuns | Observação |
|---|---|---|
| `/plan` | `project-planner`, `product-manager`, `product-owner` | Planejamento (idealmente sem escrever código). |
| `/create` | `orchestrator`, `project-planner`, `database-architect`, `backend-specialist`, `frontend-specialist` | Criação de app com coordenação e checkpoints. |
| `/enhance` | `orchestrator`, `explorer-agent`, `backend-specialist`, `frontend-specialist` | Feature em projeto existente; começa com discovery. |
| `/debug` | `debugger`, `code-archaeologist`, (`backend-specialist`/`frontend-specialist`) | Depuração com causa raiz + prevenção. |
| `/test` | `test-engineer`, `qa-automation-engineer` | Estratégia e automação de testes. |
| `/deploy` | `devops-engineer`, `security-auditor` | Deploy + checks + rollback; segurança quando necessário. |
| (docs) | `documentation-writer` | Só use quando você pedir docs explicitamente. |

## Notas e limites

- Parte do conteúdo interno de alguns agents pode estar abreviado (ex.: trechos com `...`). Esta documentação prioriza o que é **observável no frontmatter** (nome, descrição, tools, skills) e um resumo prático de uso.
- Se você quiser, eu posso gerar uma versão **100% fiel ao conteúdo interno**, extraindo e resumindo seções específicas de cada arquivo (ex.: regras, checklists e exemplos) — basta você pedir que eu “faça um resumo por agent com base no texto completo”.
