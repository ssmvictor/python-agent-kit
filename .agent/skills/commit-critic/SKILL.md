---
name: commit-critic
description: Critica de commits e PRs seguindo Conventional Commits e boas praticas de seguranca.
tier: standard
allowed-tools: Read, Glob, Grep
---

# Commit Critic

Skill para revisar e criticar **commits** e **Pull Requests** antes de serem realizados.

## Quando Usar

- Antes de fazer qualquer commit
- Ao revisar Pull Requests
- Para garantir padronizacao do projeto

---

## Checklist de Commits

### 1. Formato Conventional Commits

```
<tipo>(<escopo>): <descricao>

[corpo opcional]

[rodape opcional]
```

| Tipo       | Uso                                  |
| ---------- | ------------------------------------ |
| `feat`     | Nova funcionalidade                  |
| `fix`      | Correcao de bug                      |
| `docs`     | Documentacao                         |
| `style`    | Formatacao (sem mudanca de codigo)   |
| `refactor` | Refatoracao                          |
| `perf`     | Performance                          |
| `test`     | Testes                               |
| `chore`    | Tarefas de manutencao                |
| `build`    | Mudancas no build/dependencias       |
| `ci`       | Configuracao de CI/CD                |

### 2. Breaking Changes

```bash
# Notacao com "!"
feat(api)!: alterar formato de resposta

# Ou no rodape
feat(api): alterar formato de resposta

BREAKING CHANGE: campo `data` agora retorna array
```

### 3. Regras de Validacao

- [ ] Tipo correto para a mudanca
- [ ] Escopo indica area afetada
- [ ] Descricao clara e concisa
- [ ] Sem pontuacao final
- [ ] Breaking changes sinalizados

> **Nota:** Acentos sao permitidos em PT-BR. Projetos podem definir regra propria.

---

## Checklist de PRs

### 1. Titulo da PR

```
<tipo>(<escopo>): <descricao>
```

- [ ] Segue formato Conventional Commits
- [ ] Descreve o objetivo principal
- [ ] Sem WIP ou rascunho no titulo final

### 2. Descricao da PR

- [ ] Contexto: Por que essa mudanca?
- [ ] O que foi feito: Lista de alteracoes
- [ ] Screenshots: Se houver mudancas visuais
- [ ] Linked issues: `Closes #123` ou `Fixes #456`

### 3. Commits da PR

| Estrategia | Quando usar |
| ---------- | ----------- |
| **Squash** | Muitos commits pequenos, historico limpo |
| **Merge**  | Commits significativos, manter historico |
| **Rebase** | Branch atualizada, commits lineares |

- [ ] Commits individuais fazem sentido?
- [ ] Precisa de squash antes do merge?

### 4. Breaking Changes em PRs

- [ ] Label `breaking-change` aplicada
- [ ] Documentacao atualizada
- [ ] Migration guide se necessario

---

## Seguranca

```markdown
🔴 BLOCKING se detectar:
- Chaves de API hardcoded
- Senhas no codigo
- Arquivos .env versionados
- Secrets expostos
- Tokens em URLs
```

- [ ] Nenhuma informacao sensivel exposta
- [ ] Variaveis de ambiente usadas para secrets
- [ ] `.gitignore` atualizado

---

## Formato de Critica

### Para Commits

```markdown
## 🔍 Analise do Commit

**Mensagem:** `<mensagem>`

### ✅ Aprovado | ⚠️ Ajustes | 🔴 Bloqueado

**Problemas:**
1. [Descricao]

**Sugestao:**
`<tipo>(<escopo>): <descricao corrigida>`

**Checklist:**
- [x] Formato correto
- [x] Seguranca OK
```

### Para PRs

```markdown
## 🔍 Analise da PR

**Titulo:** `<titulo>`
**Commits:** X commits

### ✅ Aprovado | ⚠️ Ajustes | 🔴 Bloqueado

**Titulo:**
- [x] Formato Conventional Commits

**Descricao:**
- [ ] Contexto presente
- [ ] Linked issues

**Commits:**
- [ ] Historico limpo
- [ ] Sugestao: Squash antes do merge

**Seguranca:**
- [x] Sem secrets expostos

**Sugestao de Titulo:**
`<tipo>(<escopo>): <titulo corrigido>`
```

---

## Exemplos

### Bons Commits
```
feat(auth): implementar login com Google
fix(api): corrigir timeout na requisicao
docs(readme): adicionar instrucoes de instalacao
feat(db)!: alterar schema de usuarios
```

### Commits Ruins
```
Adicionando nova feature          // Falta tipo
fix: bug                          // Descricao vaga
feat(ui): adicionar modal.        // Pontuacao final
fix(auth): nova feature           // Tipo errado
```

### Bons Titulos de PR
```
feat(payment): implementar checkout com Stripe
fix(auth): resolver vazamento de sessao
refactor(api): migrar para REST v2
```

---

## Scripts Disponiveis

| Script | Uso |
| ------ | --- |
| `commit_validator.py` | Valida formato de commits |
| `pr_analyzer.py` | Analisa Pull Requests |

```bash
# Validar ultimo commit
python .agent/skills/commit-critic/scripts/commit_validator.py

# Analisar PR
python .agent/skills/commit-critic/scripts/pr_analyzer.py --pr 123
```
