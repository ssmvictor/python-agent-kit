---
description: Production deployment workflow. Uses kit validations before release and produces a deploy + rollback runbook.
---

# /deploy — Production Deployment (Strict)

$ARGUMENTS

---

## Intent

Ship a change safely: **pre-flight checks → deploy steps → post-deploy verification → rollback plan**.

This workflow assumes **high stakes**. If details are missing, ask only what’s necessary to proceed.

---

## Required info (ask only if missing)

1) Target environment: **staging** or **production**
2) Deployment surface: Vercel / Netlify / Fly.io / Docker / Other
3) A **URL** to validate (staging/prod) OR a local preview URL (for perf/e2e)

---

## Pre-flight (must)

1. **Summarize what’s going out**
   - commit(s)/branch, key changes, risk areas, migrations, flags.

2. **Run validations**
   - Always:
     - `python .agent/scripts/checklist.py .`
   - If you have a URL:
     - `python .agent/scripts/checklist.py . --url <URL>`

3. **Stop conditions**
   - If Security/Lint fails: **do not proceed**. Remediate and re-run.

---

## Deployment plan (produce exact commands)

Generate a runbook for the chosen platform. Examples:

- **Vercel**
  - `vercel --prod` (or via Git integration)
- **Netlify**
  - `netlify deploy --prod`
- **Fly.io**
  - `fly deploy`
- **Docker**
  - `docker compose pull && docker compose up -d`

Include:
- env vars required
- any migration steps
- cache/asset invalidation (if relevant)

---

## Post-deploy verification

1. Smoke tests (critical paths)
2. Error monitoring checks (logs, Sentry, etc.)
3. If URL provided, performance sanity:
   - `python .agent/scripts/checklist.py . --url <URL>`

---

## Rollback plan (must)

Provide a rollback path for the chosen platform, including:
- how to revert migrations (or forward-fix strategy)
- how to redeploy last known good version
- how to confirm rollback success

---

## Output format

```markdown
## 🚀 Deploy Runbook

### Target
- Env: ...
- Platform: ...
- URL: ...

### Pre-flight
- [ ] `python .agent/scripts/checklist.py .`
- [ ] `python .agent/scripts/checklist.py . --url ...` (if available)

### Deploy steps
1. ...
2. ...

### Verification
- ...

### Rollback
- ...
```

