# Documentação de Workflows do Antigravity Kit

Este documento descreve os **workflows (slash commands)** disponíveis em `.agent/workflows/` e **quando usar cada um**, com **casos de uso** e **exemplos práticos**.

---

## Visão geral

Os workflows são “modos de trabalho” acionados por comandos como `/plan`, `/debug`, `/deploy`, etc. Eles padronizam **processo + formato de saída**, reduzindo ambiguidade e melhorando previsibilidade em tarefas de engenharia.

### Mapa rápido (intenção → workflow)

| Você quer… | Use |
|---|---|
| Explorar opções antes de decidir | `/brainstorm` |
| Planejar com profundidade, sem escrever código | `/plan` |
| Criar um app do zero com fluxo guiado | `/create` |
| Evoluir um app existente (feature/ajuste) | `/enhance` |
| Investigar erro/bug de forma sistemática | `/debug` |
| Gerar/rodar testes e checar cobertura | `/test` |
| Subir/gerenciar servidor local de preview | `/preview` |
| Ver “quadro de status” do projeto/agentes | `/status` |
| Fazer deploy com checklist e rollback | `/deploy` |
| Coordenar múltiplos especialistas (3+ agentes) | `/orchestrate` |
| Projetar UI/UX com design system e guidelines | `ui-ux-pro-max` |

---

## 1) `/brainstorm` — Ideação estruturada (sem código)

**Objetivo:** explorar alternativas antes de “casar” com uma implementação.

**Quando usar (casos de uso):**
- Escolher estratégia de autenticação, cache, state management, arquitetura.
- Decidir stack/infra (ex.: Vercel vs Fly.io vs Docker).
- Modelar schema inicial ou abordagem de domínios.

**Como funciona (resumo):**
1. Entende o objetivo (problema, usuário, restrições).
2. Gera **pelo menos 3 opções** com prós/contras.
3. Compara e recomenda com justificativa.

**Saída esperada (formato):**
- Contexto
- Opção A/B/C (descrição, prós, contras, esforço)
- Recomendação + pergunta de direção

**Exemplos:**
```text
/brainstorm authentication system
/brainstorm caching strategy
/brainstorm database schema for social app
```

---

## 2) `/plan` — Planejamento (gera arquivo de plano, sem código)

**Objetivo:** criar um **plano executável** (arquivo de planejamento) sem escrever código.

**Regra crítica:** **não escrever código** — este workflow é para produzir **apenas o plano**.

**Quando usar (casos de uso):**
- Iniciar um projeto complexo com boa decomposição.
- Quebrar uma feature grande em etapas, riscos, decisões e checklist.
- Definir arquitetura e milestones antes de implementar.

**Artefato gerado:**
- Um arquivo `docs/PLAN-*.md` (nome derivado do pedido).

**Exemplos (mapeamento típico):**
- `/plan e-commerce site with cart` → `docs/PLAN-ecommerce-cart.md`
- `/plan add dark mode feature` → `docs/PLAN-dark-mode.md`

**Exemplos de uso:**
```text
/plan SaaS dashboard with analytics
/plan mobile app for fitness tracking
```

---

## 3) `/create` — Criar nova aplicação (do zero)

**Objetivo:** iniciar um processo guiado de criação de app.

**Quando usar (casos de uso):**
- Projetos greenfield (blog, e-commerce, CRM, dashboards).
- Protótipos que precisam sair do papel rápido, com stack definida.

**Fluxo (alto nível):**
1. **Análise do pedido** (e perguntas diretas se faltar informação).
2. **Planejamento** com `project-planner` (quebra de tarefas, stack, estrutura).
3. **Construção** (após “aprovação” do plano), orquestrando:
   - `database-architect` → schema
   - `backend-specialist` → API
   - `frontend-specialist` → UI
4. **Preview** (via `auto_preview.py`) e entrega de URL.

**Exemplos:**
```text
/create blog site
/create e-commerce app with product listing and cart
/create crm system with customer management
```

**Antes de começar (quando o pedido estiver genérico):**
- Tipo de aplicação?
- Funcionalidades básicas?
- Quem vai usar?

---

## 4) `/enhance` — Evoluir aplicação existente (iterativo)

**Objetivo:** adicionar/alterar features em um projeto já existente.

**Quando usar (casos de uso):**
- Implementar dark mode, painel admin, busca, responsividade.
- Ajustar fluxos existentes (perfil, checkout, telas específicas).
- Pequenas refatorações com teste e validação.

**Fluxo (alto nível):**
1. **Entender estado atual**
   - Levantar contexto com `session_manager.py info` (stack, features, estrutura).
2. **Planejar mudanças**
   - Arquivos afetados, dependências, impacto.
3. **Apresentar plano** (principalmente para mudanças grandes).
4. **Aplicar**
   - Acionar agentes relevantes, alterar, testar.
5. **Atualizar preview**

**Boas práticas / cautelas:**
- Pedir aprovação para mudanças grandes.
- Alertar conflitos (“trocar para Firebase” em projeto PostgreSQL).
- Commitar cada mudança.

**Exemplos:**
```text
/enhance add dark mode
/enhance build admin panel
/enhance add search feature
/enhance make responsive
```

---

## 5) `/debug` — Investigação sistemática de bugs

**Objetivo:** depurar com método: coletar dados → hipóteses → teste → causa raiz → correção → prevenção.

**Quando usar (casos de uso):**
- Erros 500, exceções, comportamento inesperado.
- Regressões após mudança recente.
- “Funciona na minha máquina” / bugs intermitentes.

**O que você deve fornecer (para acelerar):**
- Mensagem de erro completa (stack trace).
- Passos de reprodução.
- Esperado vs atual.
- Mudanças recentes.

**Saída esperada (relatório):**
- Sintoma
- Info coletada (arquivo/linha/erro)
- Hipóteses (ordenadas)
- Investigação (o que foi checado → resultado)
- Causa raiz
- Fix (antes/depois)
- Prevenção (teste/validações)

**Exemplos:**
```text
/debug login not working
/debug API returns 500
/debug form doesn't submit
```

---

## 6) `/test` — Gerar e executar testes

**Objetivo:** criar testes (para arquivo/feature) e/ou executar a suíte de testes.

**Quando usar (casos de uso):**
- Antes de refatorar: proteger comportamento.
- Ao corrigir bug: criar teste de regressão.
- Para elevar confiança em feature nova.
- Para checar cobertura e identificar pontos frágeis.

**Subcomandos:**
```text
/test                - Run all tests
/test [file/feature] - Generate tests for specific target
/test coverage       - Show test coverage report
/test watch          - Run tests in watch mode
```

**Como funciona para geração:**
1. Analisa código (funções/métodos, edge cases, dependências).
2. Gera casos (happy path, erros, bordas, integração quando fizer sentido).
3. Escreve no framework do projeto (Jest/Vitest/etc.), mockando dependências externas.

**Exemplos:**
```text
/test src/services/auth.service.ts
/test user registration flow
/test coverage
/test watch
```

---

## 7) `/preview` — Gerenciar servidor local (start/stop/status)

**Objetivo:** subir/parar/reiniciar e checar saúde do preview local.

**Quando usar (casos de uso):**
- Mostrar UI funcionando para validação rápida.
- Reproduzir bug visual/comportamental em ambiente local.
- Confirmar se a aplicação está “de pé” após alterações.

**Comandos:**
```text
/preview           - Show current status
/preview start     - Start server
/preview stop      - Stop server
/preview restart   - Restart
/preview check     - Health check
```

**Implementação (script):**
```bash
python .agent/scripts/auto_preview.py start [port]
python .agent/scripts/auto_preview.py stop
python .agent/scripts/auto_preview.py status
```

---

## 8) `/status` — Painel de status do projeto e agentes

**Objetivo:** dar visibilidade do estado atual do projeto (stack, features, preview, board dos agentes).

**Quando usar (casos de uso):**
- Acompanhar progresso (“o que já foi feito / falta fazer?”).
- Verificar preview (URL/health).
- Conferir estatísticas de alterações (arquivos criados/modificados).

**Inclui (tipicamente):**
- Info do projeto (nome, path, stack, features)
- Status board de agentes (rodando, concluído, pendente)
- Estatística de arquivos
- Status do preview (URL + health)

**Scripts usados:**
- `python .agent/scripts/session_manager.py status`
- `python .agent/scripts/auto_preview.py status`

---

## 9) `/deploy` — Deploy com checklist, staging/produção e rollback

**Objetivo:** padronizar deploy com **pré-checks**, execução e **relato final** (ou falha com resolução/rollback).

**Quando usar (casos de uso):**
- Publicar preview/staging para validação externa.
- Subir produção com checklist mínimo (lint, testes, audit).
- Reverter versão rapidamente.

**Subcomandos:**
```text
/deploy            - Interactive deployment wizard
/deploy check      - Run pre-deployment checks only
/deploy preview    - Deploy to preview/staging
/deploy production - Deploy to production
/deploy rollback   - Rollback to previous version
```

**Checklist pré-deploy (exemplos):**
- Qualidade (TS/ESLint/testes)
- Segurança (sem secrets hardcoded, env vars documentadas, `npm audit`)
- Performance (bundle ok, sem `console.log`, imagens otimizadas)
- Docs (README/CHANGELOG/API docs)

**Plataformas suportadas (referência):**
- Vercel (`vercel --prod`)
- Railway (`railway up`)
- Fly.io (`fly deploy`)
- Docker (`docker compose up -d`)

---

## 10) `/orchestrate` — Orquestração multiagente (mínimo 3 agentes)

**Objetivo:** resolver tarefas complexas coordenando especialistas, com protocolo e “gates” de validação.

**Regra crítica:** **orquestração = mínimo 3 agentes diferentes**.

**Quando usar (casos de uso):**
- Refactors grandes com impactos em camadas.
- Auditorias (segurança + performance + arquitetura).
- Migrações (stack/infra/banco) e mudanças transversais.
- Revisões profundas que exigem domínios diferentes.

**Protocolo obrigatório (2 fases):**
- **Fase 1 — Planning (sequencial):**
  - `project-planner` cria `docs/PLAN.md`
  - opcional: `explorer-agent` para descobrir codebase
  - **sem agentes paralelos nesta fase**
- **Checkpoint:** pedir aprovação explícita do usuário para iniciar implementação
- **Fase 2 — Implementation (pode paralelizar após aprovação)**

**Regra de ouro (context passing):**
Ao chamar qualquer subagente, incluir:
1. Pedido original do usuário (texto completo)
2. Decisões já tomadas (respostas do usuário)
3. Resumo do trabalho dos agentes anteriores
4. Estado atual do plano (ex.: `docs/PLAN.md`)

**Exit gate (antes de concluir):**
- Confirmar `invoked_agents >= 3`
- Executar ao menos um scan de segurança (ex.: `.../vulnerability-scanner/.../security_scan.py`)
- Gerar “Orchestration Report” com agentes e resultados consolidados

---

## 11) `ui-ux-pro-max` — Workflow de UI/UX com Design System

**Objetivo:** gerar recomendações de UI/UX e um **design system completo**, com persistência para reutilização por páginas (MASTER + overrides).

**Quando usar (casos de uso):**
- Definir linguagem visual para SaaS, e-commerce, landing pages, dashboards.
- Padronizar tipografia, cores, componentes e efeitos.
- Acelerar decisões de UX (animação, acessibilidade, densidade de informação).
- Guiar implementação por stack (default `html-tailwind`).

### Passo-a-passo recomendado

1. **Analisar requisitos**
   - tipo de produto, estilo desejado, indústria, stack.
2. **Gerar design system (obrigatório)**
   ```bash
   python3 .agent/.shared/ui-ux-pro-max/scripts/search.py "<produto> <indústria> <keywords>" --design-system [-p "Nome do Projeto"]
   ```
3. **Persistir design system (recomendado)**
   ```bash
   python3 .agent/.shared/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name"
   ```
   Gera:
   - `design-system/MASTER.md` (fonte global)
   - `design-system/pages/*.md` (overrides por página)

   Com override por página:
   ```bash
   python3 .agent/.shared/ui-ux-pro-max/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
   ```
4. **Pesquisas complementares por domínio (quando necessário)**
   - `style`, `chart`, `ux`, `typography`, `landing`, etc.
5. **Guidelines por stack (default `html-tailwind`)**
   ```bash
   python3 .agent/.shared/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
   ```

**Formato de saída:**
- ASCII (terminal) ou Markdown (documentação):
```bash
python3 .../search.py "fintech crypto" --design-system
python3 .../search.py "fintech crypto" --design-system -f markdown
```

---

## Extra (recomendado): `tdd-workflow` — Workflow de TDD (skill)

Embora não esteja em `.agent/workflows/`, existe a skill **tdd-workflow** que funciona como um “workflow de qualidade”.

**Quando usar:**
- Lógica complexa / regras de negócio (alto ROI).
- Bugs recorrentes (regressão).
- Interfaces críticas (pagamento, autenticação, billing).

**Loop clássico:**
1. **Red**: escrever teste que falha
2. **Green**: implementação mínima para passar
3. **Refactor**: limpar mantendo testes verdes

---

## Fluxo sugerido “fim a fim” (do zero à produção)

1. `/brainstorm` (quando houver dúvida arquitetural)
2. `/plan` (para gerar plano sólido)
3. `/create` (para construir)
4. `/preview` + `/status` (validar e acompanhar)
5. `/enhance` (iterar features)
6. `/test` (garantir qualidade)
7. `/deploy` (entregar)

`/debug` entra em qualquer ponto quando algo quebrar. `/orchestrate` é o modo “projeto grande / mudança grande”. `ui-ux-pro-max` é o acelerador de UI/UX.
