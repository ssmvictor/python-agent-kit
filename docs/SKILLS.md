# Documentação de Skills (`.agent/skills`)

Esta documentação descreve o **conteúdo da pasta `.agent/skills/`**, explicando **para que serve cada skill**, **quando usar** e **onde ficam os arquivos relevantes** (docs, scripts, templates).

> **Nota:** cada skill é um “pacote” de conhecimento/rotina (em Markdown) que o sistema usa como **progressive disclosure**: você lê/aplica **apenas o que for relevante** (regra de leitura seletiva).

---

## Estrutura da pasta

Em geral, cada skill segue este padrão:

- `.agent/skills/<skill>/SKILL.md` → documento principal (objetivo, regras, mapa de conteúdo, checklists)
- `.agent/skills/<skill>/*.md` → referências específicas (opcional)
- `.agent/skills/<skill>/scripts/*` → utilitários executáveis (opcional)
- `.agent/skills/app-builder/templates/*` → templates de projetos (quando aplicável)

A pasta também contém um guia geral: `.agent/skills/doc.md`.

---

## Índice

- [`api-patterns`](#api-patterns)
- [`app-builder`](#app-builder)
- [`architecture`](#architecture)
- [`behavioral-modes`](#behavioral-modes)
- [`brainstorming`](#brainstorming)
- [`clean-code`](#clean-code)
- [`code-review-checklist`](#code-review-checklist)
- [`commit-critic`](#commit-critic)
- [`data-processing`](#data-processing)
- [`database-connectors`](#database-connectors)
- [`database-design`](#database-design)
- [`deployment-procedures`](#deployment-procedures)
- [`documentation-templates`](#documentation-templates)
- [`enterprise-automation`](#enterprise-automation)
- [`erp-integration-patterns`](#erp-integration-patterns)
- [`file-integration`](#file-integration)
- [`frontend-design`](#frontend-design)
- [`intelligent-routing`](#intelligent-routing)
- [`lint-and-validate`](#lint-and-validate)
- [`mcp-builder`](#mcp-builder)
- [`office-integration`](#office-integration)
- [`parallel-agents`](#parallel-agents)
- [`performance-profiling`](#performance-profiling)
- [`plan-writing`](#plan-writing)
- [`powershell-windows`](#powershell-windows)
- [`python-patterns`](#python-patterns)
- [`red-team-tactics`](#red-team-tactics)
- [`scheduled-tasks`](#scheduled-tasks)
- [`server-management`](#server-management)
- [`systematic-debugging`](#systematic-debugging)
- [`tailwind-patterns`](#tailwind-patterns)
- [`tdd-workflow`](#tdd-workflow)
- [`testing-patterns`](#testing-patterns)
- [`vulnerability-scanner`](#vulnerability-scanner)
- [`webapp-testing`](#webapp-testing)

---

## Referência rápida

| Skill | Categoria | Tier | Scripts |
|---|---|---|---|
| `api-patterns` | APIs | `pro` | `api_validator.py` |
| `app-builder` | Construção de apps | `pro` | — |
| `architecture` | Arquitetura | `standard` | — |
| `behavioral-modes` | Orquestração e modos | `lite` | — |
| `brainstorming` | Descoberta de requisitos | `—` | — |
| `clean-code` | Qualidade de código | `lite` | — |
| `code-review-checklist` | Qualidade de código | `lite` | — |
| `commit-critic` | Qualidade de código | `standard` | `commit_validator.py`, `pr_analyzer.py` |
| `data-processing` | Dados | `standard` | `data_quality_checker.py`, `schema_validator.py` |
| `database-connectors` | Dados | `standard` | `connection_tester.py` |
| `database-design` | Dados | `standard` | `schema_validator.py` |
| `deployment-procedures` | Operações/Deploy | `lite` | — |
| `documentation-templates` | Documentação | `lite` | — |
| `enterprise-automation` | Automação corporativa | `standard` | `automation_validator.py` |
| `erp-integration-patterns` | Integrações | `standard` | — |
| `file-integration` | Integrações | `standard` | — |
| `frontend-design` | Frontend/UX | `standard` | `accessibility_checker.py`, `ux_audit.py` |
| `intelligent-routing` | Orquestração e modos | `lite` | — |
| `lint-and-validate` | Qualidade de código | `standard` | `lint_runner.py`, `type_coverage.py` |
| `mcp-builder` | Integrações | `lite` | — |
| `office-integration` | Automação corporativa | `standard` | `document_generator.py` |
| `parallel-agents` | Orquestração e modos | `lite` | — |
| `performance-profiling` | Qualidade/Performance | `standard` | `lighthouse_audit.py` |
| `plan-writing` | Planejamento | `lite` | — |
| `powershell-windows` | Operações/Windows | `lite` | — |
| `python-patterns` | Python | `lite` | — |
| `red-team-tactics` | Segurança | `lite` | — |
| `scheduled-tasks` | Operações/Windows | `standard` | — |
| `server-management` | Operações/Deploy | `lite` | — |
| `systematic-debugging` | Debug | `lite` | — |
| `tailwind-patterns` | Frontend/UX | `lite` | — |
| `tdd-workflow` | Testes | `lite` | — |
| `testing-patterns` | Testes | `standard` | `test_runner.py` |
| `vulnerability-scanner` | Segurança | `standard` | `security_scan.py` |
| `webapp-testing` | Testes | `standard` | `playwright_runner.py` |

---

## api-patterns

**Categoria:** APIs  
**Tier:** `pro`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep`

**Objetivo:** Desenhar contratos de API consistentes (REST/GraphQL/tRPC) e decidir qual abordagem usar por caso.

### Quando usar
- Desenhar contratos de API consistentes (REST/GraphQL/tRPC) e decidir qual abordagem usar por caso.
- Definir padrões de resposta (erros, paginação, envelopes), versionamento e documentação.
- Revisar uma API existente contra checklist e anti‑patterns; validar conformidade via script.

### Arquivos principais
- **Skill**: `.agent/skills/api-patterns/SKILL.md`
- **Docs de referência**: `api-style.md`, `auth.md`, `documentation.md`, `graphql.md`, `rate-limiting.md`, `response.md`, `rest.md`, `security-testing.md`, `trpc.md`, `versioning.md`
- **Scripts**: `scripts/api_validator.py`

### Exemplo de uso (prompt)
```text
Use a skill `api-patterns` para: desenhar uma API (com paginação, versionamento e erros padronizados) e revisar anti-patterns.
```

---

## app-builder

**Categoria:** Construção de apps  
**Tier:** `pro`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Scaffold de aplicações (web/mobile/desktop/CLI) a partir de requisitos em linguagem natural.

### Quando usar
- Scaffold de aplicações (web/mobile/desktop/CLI) a partir de requisitos em linguagem natural.
- Escolha de stack e templates (Next.js, Nuxt, FastAPI, React Native, etc.) com coordenação de agentes.
- Implementação iterativa de features com separação frontend/backend/db e checkpoints.

### Arquivos principais
- **Skill**: `.agent/skills/app-builder/SKILL.md`
- **Templates (app-builder)**: `astro-static`, `chrome-extension`, `cli-tool`, `electron-desktop`, `express-api`, `flutter-app`, `monorepo-turborepo`, `nextjs-fullstack`, `nextjs-saas`, `nextjs-static`, `nuxt-app`, `python-fastapi`, `react-native-app`
- **Docs de referência**: `agent-coordination.md`, `feature-building.md`, `project-detection.md`, `scaffolding.md`, `tech-stack.md`

### Exemplo de uso (prompt)
```text
Use a skill `app-builder` para: criar um app do zero, escolher stack, sugerir template e detalhar a estrutura de pastas.
```

---

## architecture

**Categoria:** Arquitetura  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep`

**Objetivo:** Tomar decisões arquiteturais com análise de requisitos, trade‑offs e riscos (ADR).

### Quando usar
- Tomar decisões arquiteturais com análise de requisitos, trade‑offs e riscos (ADR).
- Comparar padrões (monólito vs serviços, sync vs async, filas, cache) com critérios claros.
- Revisar desenho de sistema e sugerir melhorias de modularidade, escalabilidade e observabilidade.

### Arquivos principais
- **Skill**: `.agent/skills/architecture/SKILL.md`
- **Docs de referência**: `decisions.md`, `patterns.md`, `performance.md`, `reliability.md`, `security.md`

### Exemplo de uso (prompt)
```text
Use a skill `architecture` para: decidir arquitetura, registrar trade-offs e produzir um ADR curto.
```

---

## behavioral-modes

**Categoria:** Orquestração e modos  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Selecionar o “modo” de atuação adequado (brainstorm, implementar, depurar, revisar, ensinar, entregar).

### Quando usar
- Selecionar o “modo” de atuação adequado (brainstorm, implementar, depurar, revisar, ensinar, entregar).
- Padronizar expectativa de saída por tipo de tarefa (plano, patch, review, release).
- Evitar misturar modos (ex.: planejar vs codar) quando isso prejudica a qualidade.

### Arquivos principais
- **Skill**: `.agent/skills/behavioral-modes/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `behavioral-modes` para: escolher o modo correto e produzir a saída no formato esperado.
```

---

## brainstorming

**Categoria:** Descoberta de requisitos  
**Tier:** `—`  
**Ferramentas permitidas (frontmatter):** `—`

**Objetivo:** Clarificar requisitos ambíguos via perguntas socráticas e alternativas bem estruturadas.

### Quando usar
- Clarificar requisitos ambíguos via perguntas socráticas e alternativas bem estruturadas.
- Levantar hipóteses e opções quando o problema ainda não está bem definido.
- Reportar progresso e decisões de forma transparente durante exploração.

### Arquivos principais
- **Skill**: `.agent/skills/brainstorming/SKILL.md`
- **Docs de referência**: `dynamic-questioning.md`

### Exemplo de uso (prompt)
```text
Use a skill `brainstorming` para: fazer perguntas de decisão (com defaults), explorar opções e convergir.
```

---

## clean-code

**Categoria:** Qualidade de código  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Aplicar padrões pragmáticos de código limpo (SRP/DRY/legibilidade) sem over‑engineering.

### Quando usar
- Aplicar padrões pragmáticos de código limpo (SRP/DRY/legibilidade) sem over‑engineering.
- Definir convenções de nomes, estrutura e limites de complexidade.
- Guiar refactors pequenos e seguros com foco em manutenção.

### Arquivos principais
- **Skill**: `.agent/skills/clean-code/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `clean-code` para: refatorar mantendo simplicidade e legibilidade (sem abstrações desnecessárias).
```

---

## code-review-checklist

**Categoria:** Qualidade de código  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Revisar PRs com checklist de qualidade, segurança, testes e manutenção.

### Quando usar
- Revisar PRs com checklist de qualidade, segurança, testes e manutenção.
- Padronizar comentários de review (o que bloquear vs sugestão).
- Detectar smells e riscos (injeção, validação, edge cases, performance).

### Arquivos principais
- **Skill**: `.agent/skills/code-review-checklist/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `code-review-checklist` para: revisar um PR e apontar problemas críticos vs melhorias.
```

---

## commit-critic

**Categoria:** Qualidade de código  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Validar commits/PRs com Conventional Commits e boas práticas (escopo, mensagem, breaking changes).

### Quando usar
- Validar commits/PRs com Conventional Commits e boas práticas (escopo, mensagem, breaking changes).
- Checar sinais de risco (segredos, arquivos grandes, mudanças perigosas) e gerar relatório.
- Padronizar histórico de commits para release notes e automações.

### Arquivos principais
- **Skill**: `.agent/skills/commit-critic/SKILL.md`
- **Scripts**: `scripts/commit_validator.py`, `scripts/pr_analyzer.py`

### Exemplo de uso (prompt)
```text
Use a skill `commit-critic` para: auditar commits/PR e sugerir melhorias de mensagem/escopo/segurança.
```

---

## data-processing

**Categoria:** Dados  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Construir pipelines ETL/ELT em Python (pandas/polars) com validação e tipagem forte.

### Quando usar
- Construir pipelines ETL/ELT em Python (pandas/polars) com validação e tipagem forte.
- Checar qualidade de dados (schema, nulos, ranges, outliers) com scripts auxiliares.
- Definir contratos de dados e estratégias de transformação idempotentes.

### Arquivos principais
- **Skill**: `.agent/skills/data-processing/SKILL.md`
- **Docs de referência**: `data-validation.md`, `etl-patterns.md`, `pandas.md`, `polars.md`
- **Scripts**: `scripts/data_quality_checker.py`, `scripts/schema_validator.py`

### Exemplo de uso (prompt)
```text
Use a skill `data-processing` para: validar um DataFrame e propor um pipeline ETL com checks e tipagem.
```

---

## database-connectors

**Categoria:** Dados  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Implementar conectividade robusta a bancos (pooling, retry, timeouts) em Python.

### Quando usar
- Implementar conectividade robusta a bancos (pooling, retry, timeouts) em Python.
- Testar conexão e credenciais de forma reprodutível (script de teste).
- Padronizar drivers (pyodbc/cx_Oracle etc.) e lidar com encoding/timezones.

### Arquivos principais
- **Skill**: `.agent/skills/database-connectors/SKILL.md`
- **Docs de referência**: `cx-oracle.md`, `pooling.md`, `pyodbc.md`, `retry.md`
- **Scripts**: `scripts/connection_tester.py`

### Exemplo de uso (prompt)
```text
Use a skill `database-connectors` para: implementar pool + retry e criar um teste de conexão para Oracle/ODBC.
```

---

## database-design

**Categoria:** Dados  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep`

**Objetivo:** Modelar schema, chaves, constraints e estratégia de índices para desempenho e integridade.

### Quando usar
- Modelar schema, chaves, constraints e estratégia de índices para desempenho e integridade.
- Decidir entre ORM vs SQL manual, normalização vs desnormalização por caso.
- Validar schema/propostas com script e checklist de anti‑patterns.

### Arquivos principais
- **Skill**: `.agent/skills/database-design/SKILL.md`
- **Docs de referência**: `indexing.md`, `orm-selection.md`, `schema-design.md`
- **Scripts**: `scripts/schema_validator.py`

### Exemplo de uso (prompt)
```text
Use a skill `database-design` para: revisar um schema e sugerir índices/constraints e anti-patterns.
```

---

## deployment-procedures

**Categoria:** Operações/Deploy  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Executar deploy on‑prem (Windows Server/IIS/Services) com segurança e rollback.

### Quando usar
- Executar deploy on‑prem (Windows Server/IIS/Services) com segurança e rollback.
- Padronizar checklist de pré/pós‑deploy e estratégia de configuração (env, secrets).
- Reduzir downtime com passos repetíveis e validação.

### Arquivos principais
- **Skill**: `.agent/skills/deployment-procedures/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `deployment-procedures` para: montar um runbook de deploy/rollback em Windows Server/IIS.
```

---

## documentation-templates

**Categoria:** Documentação  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Gerar READMEs, guias de setup, docs de API e padrões de documentação.

### Quando usar
- Gerar READMEs, guias de setup, docs de API e padrões de documentação.
- Padronizar estrutura de docs para projetos (pastas, títulos, seções).
- Criar templates reutilizáveis para features, ADRs, runbooks e troubleshooting.

### Arquivos principais
- **Skill**: `.agent/skills/documentation-templates/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `documentation-templates` para: criar um README e um template de ADR para o repositório.
```

---

## enterprise-automation

**Categoria:** Automação corporativa  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Automatizar tarefas corporativas em Windows (pywin32/COM, Selenium, agendadores).

### Quando usar
- Automatizar tarefas corporativas em Windows (pywin32/COM, Selenium, agendadores).
- Validar automações e regras de robustez (retries, logs, idempotência).
- Integrar automações com sistemas legados e rotinas de backoffice.

### Arquivos principais
- **Skill**: `.agent/skills/enterprise-automation/SKILL.md`
- **Docs de referência**: `com-automation.md`, `selenium.md`, `task-scheduling.md`
- **Scripts**: `scripts/automation_validator.py`

### Exemplo de uso (prompt)
```text
Use a skill `enterprise-automation` para: automatizar uma rotina Windows com logs, retries e execução agendada.
```

---

## erp-integration-patterns

**Categoria:** Integrações  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep`

**Objetivo:** Projetar integrações com ERPs (sincronização, mapeamento de chaves, idempotência).

### Quando usar
- Projetar integrações com ERPs (sincronização, mapeamento de chaves, idempotência).
- Definir estratégias de fila/reprocessamento, reconciliação e auditoria de dados.
- Tratar limites de API (rate limiting), erros funcionais e consistência eventual.

### Arquivos principais
- **Skill**: `.agent/skills/erp-integration-patterns/SKILL.md`
- **Docs de referência**: `idempotency.md`, `sync-strategies.md`

### Exemplo de uso (prompt)
```text
Use a skill `erp-integration-patterns` para: desenhar sincronização idempotente entre sistemas e plano de reprocesso.
```

---

## file-integration

**Categoria:** Integrações  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep`

**Objetivo:** Integrações via arquivos (CSV/XML/JSON) em ambientes on‑prem (UNC shares, watchers).

### Quando usar
- Integrações via arquivos (CSV/XML/JSON) em ambientes on‑prem (UNC shares, watchers).
- Padronizar naming, atomic writes, locking e reprocessamento seguro.
- Mitigar problemas de concorrência, permissões e formatos inconsistentes.

### Arquivos principais
- **Skill**: `.agent/skills/file-integration/SKILL.md`
- **Docs de referência**: `file-watching.md`, `network-shares.md`, `reprocessing.md`

### Exemplo de uso (prompt)
```text
Use a skill `file-integration` para: implementar um file watcher seguro (atomic write/lock/retry) em share UNC.
```

---

## frontend-design

**Categoria:** Frontend/UX  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Definir guidelines de UI/UX, acessibilidade (a11y) e consistência visual.

### Quando usar
- Definir guidelines de UI/UX, acessibilidade (a11y) e consistência visual.
- Auditar páginas/componentes com scripts (a11y checker e UX audit).
- Padronizar componentes, estados (loading/empty/error) e responsividade.

### Arquivos principais
- **Skill**: `.agent/skills/frontend-design/SKILL.md`
- **Docs de referência**: `accessibility.md`, `design-systems.md`, `ui-patterns.md`
- **Scripts**: `scripts/accessibility_checker.py`, `scripts/ux_audit.py`

### Exemplo de uso (prompt)
```text
Use a skill `frontend-design` para: revisar UI com foco em acessibilidade e estados (loading/empty/error).
```

---

## intelligent-routing

**Categoria:** Orquestração e modos  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Fazer triagem: decidir rapidamente qual skill/workflow aplicar para resolver a tarefa.

### Quando usar
- Fazer triagem: decidir rapidamente qual skill/workflow aplicar para resolver a tarefa.
- Classificar requests por risco/impacto e escolher nível de rigor (lite/standard/pro).
- Evitar custo desnecessário: leitura seletiva e foco no essencial.

### Arquivos principais
- **Skill**: `.agent/skills/intelligent-routing/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `intelligent-routing` para: sugerir qual skill/workflow aplicar e por quê, antes de executar.
```

---

## lint-and-validate

**Categoria:** Qualidade de código  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Glob, Grep, Bash`

**Objetivo:** Aplicar ciclo de qualidade: lint, typecheck e validações antes de considerar “done”.

### Quando usar
- Aplicar ciclo de qualidade: lint, typecheck e validações antes de considerar “done”.
- Rodar scripts de lint e cobertura de tipos (type coverage) e interpretar relatórios.
- Padronizar correções e reduzir regressões por automação.

### Arquivos principais
- **Skill**: `.agent/skills/lint-and-validate/SKILL.md`
- **Scripts**: `scripts/lint_runner.py`, `scripts/type_coverage.py`

### Exemplo de uso (prompt)
```text
Use a skill `lint-and-validate` para: rodar lint/typecheck, interpretar erros e corrigir até ficar verde.
```

---

## mcp-builder

**Categoria:** Integrações  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep`

**Objetivo:** Projetar e implementar servidores MCP (Model Context Protocol) com bom design de ferramentas.

### Quando usar
- Projetar e implementar servidores MCP (Model Context Protocol) com bom design de ferramentas.
- Definir schemas de entrada/saída, recursos e padrões de segurança/observabilidade.
- Organizar arquitetura do servidor e escolher transporte adequado.

### Arquivos principais
- **Skill**: `.agent/skills/mcp-builder/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `mcp-builder` para: desenhar tools/resources de um servidor MCP com schemas claros e seguros.
```

---

## office-integration

**Categoria:** Automação corporativa  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Automatizar geração/manipulação de documentos Office/PDF (Excel/Word) com OOP.

### Quando usar
- Automatizar geração/manipulação de documentos Office/PDF (Excel/Word) com OOP.
- Gerar relatórios e artefatos (templates, merge de dados) via script utilitário.
- Padronizar pipelines de documentos e validação de saída.

### Arquivos principais
- **Skill**: `.agent/skills/office-integration/SKILL.md`
- **Docs de referência**: `excel.md`, `pdf.md`, `word.md`
- **Scripts**: `scripts/document_generator.py`

### Exemplo de uso (prompt)
```text
Use a skill `office-integration` para: gerar um relatório Excel/PDF a partir de dados com layout padronizado.
```

---

## parallel-agents

**Categoria:** Orquestração e modos  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Dividir trabalho em tarefas independentes e rodar em paralelo (quando seguro).

### Quando usar
- Dividir trabalho em tarefas independentes e rodar em paralelo (quando seguro).
- Definir interface entre sub-tarefas (contratos, handoff, aggregation).
- Evitar condições de corrida: checkpoints e integração final cuidadosa.

### Arquivos principais
- **Skill**: `.agent/skills/parallel-agents/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `parallel-agents` para: decompor tarefas paralelizáveis e definir como juntar resultados.
```

---

## performance-profiling

**Categoria:** Qualidade/Performance  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Medir e otimizar performance (backend/frontend) com metodologia (baseline → mudança → re‑medição).

### Quando usar
- Medir e otimizar performance (backend/frontend) com metodologia (baseline → mudança → re‑medição).
- Rodar auditoria Lighthouse via script e transformar achados em backlog.
- Detectar gargalos, desperdícios e regressões de performance.

### Arquivos principais
- **Skill**: `.agent/skills/performance-profiling/SKILL.md`
- **Docs de referência**: `profiling.md`
- **Scripts**: `scripts/lighthouse_audit.py`

### Exemplo de uso (prompt)
```text
Use a skill `performance-profiling` para: rodar Lighthouse, interpretar métricas e propor otimizações priorizadas.
```

---

## plan-writing

**Categoria:** Planejamento  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Produzir planos claros com etapas, dependências, riscos e critérios de verificação.

### Quando usar
- Produzir planos claros com etapas, dependências, riscos e critérios de verificação.
- Gerar checklists de aceitação e “definition of done” por feature.
- Reduzir ambiguidade antes de implementar mudanças grandes.

### Arquivos principais
- **Skill**: `.agent/skills/plan-writing/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `plan-writing` para: criar um plano de execução com milestones e critérios de verificação.
```

---

## powershell-windows

**Categoria:** Operações/Windows  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Escrever scripts PowerShell robustos (quoting, pipelines, erros, exit codes).

### Quando usar
- Escrever scripts PowerShell robustos (quoting, pipelines, erros, exit codes).
- Evitar armadilhas comuns (operadores, encoding, permissões) em Windows.
- Automatizar tarefas de infra/ops com boas práticas.

### Arquivos principais
- **Skill**: `.agent/skills/powershell-windows/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `powershell-windows` para: corrigir/produzir um script PowerShell resiliente para Windows.
```

---

## python-patterns

**Categoria:** Python  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Escolher padrões e frameworks Python (sync/async, FastAPI, CLI, packaging) conforme requisitos.

### Quando usar
- Escolher padrões e frameworks Python (sync/async, FastAPI, CLI, packaging) conforme requisitos.
- Padronizar tipagem (mypy), estrutura de projeto e práticas de teste.
- Tomar decisões de performance e arquitetura em Python.

### Arquivos principais
- **Skill**: `.agent/skills/python-patterns/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `python-patterns` para: decidir arquitetura/estrutura de um pacote Python com tipagem e testes.
```

---

## red-team-tactics

**Categoria:** Segurança  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Modelar ameaças e testar postura defensiva com base em MITRE ATT&CK.

### Quando usar
- Modelar ameaças e testar postura defensiva com base em MITRE ATT&CK.
- Planejar exercícios de segurança (simulados) e gerar relatórios técnicos/mitigações.
- Identificar superfícies de ataque e priorizar hardening.

### Arquivos principais
- **Skill**: `.agent/skills/red-team-tactics/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `red-team-tactics` para: fazer threat modeling e propor testes defensivos (sem exploração real).
```

---

## scheduled-tasks

**Categoria:** Operações/Windows  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Agendar rotinas em Windows (Task Scheduler) e/ou via bibliotecas de scheduling em Python.

### Quando usar
- Agendar rotinas em Windows (Task Scheduler) e/ou via bibliotecas de scheduling em Python.
- Definir estratégia de execução confiável (logs, retries, alertas).
- Documentar e versionar jobs, incluindo janela de execução e dependências.

### Arquivos principais
- **Skill**: `.agent/skills/scheduled-tasks/SKILL.md`
- **Docs de referência**: `python-scheduling.md`, `task-scheduler.md`

### Exemplo de uso (prompt)
```text
Use a skill `scheduled-tasks` para: criar um job confiável no Task Scheduler com logging e retry.
```

---

## server-management

**Categoria:** Operações/Deploy  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Gerenciar serviços/processos, monitoramento e estratégia de logs em servidores.

### Quando usar
- Gerenciar serviços/processos, monitoramento e estratégia de logs em servidores.
- Definir rotinas de health check, restart e capacity planning básico.
- Estabelecer padrões operacionais (runbooks).

### Arquivos principais
- **Skill**: `.agent/skills/server-management/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `server-management` para: desenhar um runbook de operação (health checks, logs, restarts).
```

---

## systematic-debugging

**Categoria:** Debug  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Aplicar depuração em 4 fases com evidência: reproduzir, isolar, corrigir, prevenir.

### Quando usar
- Aplicar depuração em 4 fases com evidência: reproduzir, isolar, corrigir, prevenir.
- Evitar “chutes”: hipóteses ordenadas + experimentos controlados.
- Transformar incidentes em testes e guardrails.

### Arquivos principais
- **Skill**: `.agent/skills/systematic-debugging/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `systematic-debugging` para: investigar um bug com hipóteses testáveis e causa raiz.
```

---

## tailwind-patterns

**Categoria:** Frontend/UX  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Aplicar padrões modernos do Tailwind CSS v4 (CSS-first config, container queries).

### Quando usar
- Aplicar padrões modernos do Tailwind CSS v4 (CSS-first config, container queries).
- Padronizar design tokens, layouts responsivos e componentes utilitários.
- Evitar anti‑patterns de CSS e manter consistência.

### Arquivos principais
- **Skill**: `.agent/skills/tailwind-patterns/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `tailwind-patterns` para: padronizar classes/utilitários e layout responsivo em Tailwind v4.
```

---

## tdd-workflow

**Categoria:** Testes  
**Tier:** `lite`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit`

**Objetivo:** Guiar desenvolvimento por testes (RED → GREEN → REFACTOR).

### Quando usar
- Guiar desenvolvimento por testes (RED → GREEN → REFACTOR).
- Construir suíte de regressão durante correções de bug e novas features.
- Manter design simples com feedback rápido.

### Arquivos principais
- **Skill**: `.agent/skills/tdd-workflow/SKILL.md`

### Exemplo de uso (prompt)
```text
Use a skill `tdd-workflow` para: implementar uma feature seguindo RED/GREEN/REFACTOR com testes.
```

---

## testing-patterns

**Categoria:** Testes  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Definir estratégia de testes (unit/integration/e2e), mocks e fixtures.

### Quando usar
- Definir estratégia de testes (unit/integration/e2e), mocks e fixtures.
- Rodar e automatizar execução de testes via script e melhorar feedback.
- Padronizar cobertura, naming e organização de testes.

### Arquivos principais
- **Skill**: `.agent/skills/testing-patterns/SKILL.md`
- **Docs de referência**: `integration.md`, `unit.md`
- **Scripts**: `scripts/test_runner.py`

### Exemplo de uso (prompt)
```text
Use a skill `testing-patterns` para: criar estratégia de testes e gerar/rodar testes para um módulo.
```

---

## vulnerability-scanner

**Categoria:** Segurança  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Fazer varredura avançada de vulnerabilidades (OWASP, supply chain, configuração).

### Quando usar
- Fazer varredura avançada de vulnerabilidades (OWASP, supply chain, configuração).
- Rodar o script de security scan e priorizar findings por risco/impacto.
- Gerar recomendações de mitigação e hardening.

### Arquivos principais
- **Skill**: `.agent/skills/vulnerability-scanner/SKILL.md`
- **Docs de referência**: `owasp-top10.md`
- **Scripts**: `scripts/security_scan.py`

### Exemplo de uso (prompt)
```text
Use a skill `vulnerability-scanner` para: rodar um scan e gerar um relatório de correções priorizadas.
```

---

## webapp-testing

**Categoria:** Testes  
**Tier:** `standard`  
**Ferramentas permitidas (frontmatter):** `Read, Write, Edit, Glob, Grep, Bash`

**Objetivo:** Testar aplicações web (E2E) com Playwright, smoke tests e auditorias profundas.

### Quando usar
- Testar aplicações web (E2E) com Playwright, smoke tests e auditorias profundas.
- Rodar runner Playwright via script e integrar em CI.
- Validar fluxos críticos (login/checkout/forms) e prevenir regressões.

### Arquivos principais
- **Skill**: `.agent/skills/webapp-testing/SKILL.md`
- **Docs de referência**: `playwright.md`
- **Scripts**: `scripts/playwright_runner.py`

### Exemplo de uso (prompt)
```text
Use a skill `webapp-testing` para: criar/rodar testes E2E Playwright para fluxos críticos.
```
