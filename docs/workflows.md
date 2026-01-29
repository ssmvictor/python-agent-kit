# Documentação de Workflows do Antigravity Kit

Este documento descreve os **workflows (slash commands)** disponíveis em `.agent/workflows/` e **quando usar cada um**, com **casos de uso** e **exemplos práticos**.

---

## Visão geral

Os workflows são "modos de trabalho" acionados por comandos como `/test`, `/deploy`, `/strict`, etc. Eles padronizam **processo + formato de saída**, reduzindo ambiguidade e melhorando previsibilidade em tarefas de engenharia.

> **Filosofia:** Fast by default. Os workflows restantes são focados em validação, deploy e orquestração de alta confiança. Para tarefas simples (criar, debugar, planejar), use o modo normal do agente.

### Mapa rápido (intenção → workflow)

| Você quer… | Use |
|---|---|
| Rodar testes, gerar cobertura, triar falhas | `/test` |
| Fazer deploy com checklist e rollback | `/deploy` |
| Validação rigorosa: security + lint + tests (enterprise bar) | `/strict` |
| Coordenar múltiplos especialistas (3+ agentes) | `/orchestrate` |

---

## 1) `/test` — Tests (Generate + Run + Triage)

**Objetivo:** rodar testes consistentemente (Python/Node), gerar testes para código modificado, triar falhas rapidamente.

**Quando usar (casos de uso):**
- Antes de refatorar: proteger comportamento.
- Ao corrigir bug: criar teste de regressão.
- Para elevar confiança em feature nova.
- Para checar cobertura e identificar pontos frágeis.

**Ações (via argumentos):**
- `run` (padrão): executa a suíte de testes
- `coverage`: roda com relatório de cobertura
- `generate`: cria testes para a mudança descrita, depois executa
- `e2e`: roda Playwright (para web apps)

**Comandos executados:**
```bash
# Run suite
python .agent/skills/testing-patterns/scripts/test_runner.py .

# Coverage
python .agent/skills/testing-patterns/scripts/test_runner.py . --coverage

# E2E (web)
python .agent/skills/webapp-testing/scripts/playwright_runner.py .
```

**Exemplos:**
```text
/test
/test coverage
/test generate for user authentication
/test e2e
```

---

## 2) `/deploy` — Production Deployment (Strict)

**Objetivo:** fazer deploy de forma segura com **pré-checks**, execução e **plano de rollback**.

**Quando usar (casos de uso):**
- Publicar staging para validação externa.
- Subir produção com checklist mínimo (lint, testes, audit).
- Reverter versão rapidamente.

**Informações necessárias (perguntar se faltar):**
1. Target environment: **staging** ou **production**
2. Deployment surface: Vercel / Netlify / Fly.io / Docker / Outro
3. Uma **URL** para validar (staging/prod) ou preview local (para perf/e2e)

**Pre-flight (obrigatório):**
1. Resumir o que está sendo deployado (commits, changes, risk areas)
2. Rodar validações:
   - `python .agent/scripts/checklist.py .`
   - Se tiver URL: `python .agent/scripts/checklist.py . --url <URL>`
3. Stop conditions: se Security/Lint falhar, **não prossiga**

**Plataformas suportadas:**
- **Vercel**: `vercel --prod`
- **Netlify**: `netlify deploy --prod`
- **Fly.io**: `fly deploy`
- **Docker**: `docker compose pull && docker compose up -d`

**Exemplos:**
```text
/deploy staging to Vercel
/deploy production
/deploy production --url https://app.example.com
```

---

## 3) `/strict` — Enterprise Bar (Opt-in)

**Objetivo:** validação rigorosa com **predictability**: security + lint + tests, com relatório de remediação.

**Quando usar (casos de uso):**
- Quando o usuário pedir explicitamente "rigor/enterprise/production-grade".
- Antes de merges críticos.
- Para garantir barra enterprise em mudanças importantes.

**Este workflow é opt-in.** Não aplique a menos que o usuário chame `/strict` ou peça rigor.

**Procedure:**
1. **Summarize the change** — escopo, risk areas, módulos afetados
2. **Run the kit checklist:**
   - `python .agent/scripts/checklist.py .`
   - Se tiver URL: `python .agent/scripts/checklist.py . --url <URL>`
3. **Interpret results** (ordem de prioridade):
   1. Security
   2. Lint / type checks
   3. Schema validation (se aplicável)
   4. Tests
   5. UX / accessibility (se aplicável)
4. **Remediate** — corrija Critical blockers primeiro (Security/Lint)
5. **Exit criteria:**
   - ✅ `checklist.py` retorna sucesso
   - ✅ Forneça seção "Verification" com comandos exatos

**Exemplos:**
```text
/strict
/strict for authentication module
/strict --url https://staging.example.com
```

---

## 4) `/orchestrate` — Multi-Agent (Strict)

**Objetivo:** coordenar especialistas para trabalhos multi-domínio ou de alta confiança.

**Quando usar (casos de uso):**
- Mudanças multi-domínio (backend + DB + security + UI).
- Refactors grandes / migrações.
- Incident response / deep debugging.
- Quando o usuário precisa de "high confidence".

**Regras de orquestração:**
1. **Mínimo de especialistas:** envolva **≥ 3** agentes de domínio (backend, frontend, database, security, devops, debugger, code-archaeologist)
2. **Handoffs claros:** cada especialista deve retornar:
   - findings
   - recomendações concretas
   - riscos/edge cases
3. **Validação é obrigatória:** execute pelo menos:
   - `python .agent/skills/vulnerability-scanner/scripts/security_scan.py .`
   - `python .agent/skills/lint-and-validate/scripts/lint_runner.py .`
   - `python .agent/skills/testing-patterns/scripts/test_runner.py .` (quando código mudar)

**Workflow:**
1. **Problem brief** — goal, constraints, acceptance criteria
2. **Specialist passes** — security, architecture/backend, DB/schema, frontend/UX, devOps/deploy (conforme aplicável)
3. **Synthesis** — merge recommendations em plano único, identifique conflitos
4. **Verification plan** — liste comandos e defina exit criteria

**Exemplos:**
```text
/orchestrate refactor authentication system
/orchestrate migrate from Firebase to PostgreSQL
/orchestrate security audit for payment module
```

---

## Workflows Removidos (Migrados para Modo Normal)

Os seguintes workflows foram **removidos** e suas funcionalidades migradas para o modo normal do agente:

| Workflow | Alternativa |
|---|---|
| `/brainstorm` | Faça perguntas diretas no modo normal. O agente explorará opções naturalmente. |
| `/plan` | Use `/orchestrate` com foco em planejamento, ou peça um plano no modo normal. |
| `/create` | Use o modo normal para criar apps. Escalone para `/orchestrate` se for complexo. |
| `/enhance` | Use o modo normal para evoluir apps. O agente detectará o estado atual automaticamente. |
| `/debug` | Use o modo normal. Descreva o erro e o agente investigará sistematicamente. |
| `/preview` | Use o modo normal. Peça para iniciar o servidor de preview. |
| `/status` | Use o modo normal. Peça o status do projeto. |
| `/ui-ux-pro-max` | Use o modo normal para trabalhos de UI/UX. O agente aplicará as regras de design. |

---

## Resumo da Filosofia

> **Fast by default, strict when needed.**

- **Modo normal:** Para 80% das tarefas (criar, debugar, planejar, evoluir). Rápido, direto, sem cerimônia.
- **Workflows (`/test`, `/deploy`, `/strict`, `/orchestrate`):** Para validação, deploy e orquestração de alta confiança. Rigoroso, previsível, com checklists.

Escolha o workflow baseado no **risco e complexidade**, não no hábito.
