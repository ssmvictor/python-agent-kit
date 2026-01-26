---
name: deployment-procedures
description: On-premise deployment principles. Windows Server, IIS, Windows Services, safe deployment workflows, rollback strategies.
tier: lite
allowed-tools: Read, Glob, Grep, Bash
---

# Deployment Procedures (On-Premise)

> Deployment principles for on-premise Windows environments.
> **Learn to THINK, not memorize scripts.**

---

## ⚠️ How to Use This Skill

This skill teaches **deployment principles** for on-premise Windows environments.

- Every deployment is unique
- Understand the WHY behind each step
- Adapt procedures to your infrastructure

---

## 1. On-Premise Platform Selection

### Decision Tree

```
What are you deploying?
│
├── Python Script / Automation
│   └── Windows Task Scheduler + Python
│
├── Python Web App (FastAPI/Django)
│   ├── IIS + wfastcgi
│   ├── Windows Service (NSSM)
│   └── PM2 on Windows
│
├── Background Worker / Daemon
│   └── Windows Service (NSSM / pywin32)
│
└── Scheduled ETL / Reports
    └── Task Scheduler + Python
```

### Platform Comparison

| Platform | Best For | Complexity |
|----------|----------|------------|
| **Task Scheduler** | Scheduled scripts | Low |
| **Windows Service** | Always-on daemons | Medium |
| **IIS + wfastcgi** | Web apps, APIs | Medium |
| **PM2 on Windows** | Node.js/Python apps | Low |
| **NSSM** | Any EXE as service | Low |

---

## 2. Pre-Deployment Principles

### The 4 Verification Categories

| Category | What to Check |
|----------|--------------|
| **Code Quality** | Tests passing, linting clean |
| **Build** | Production build works |
| **Environment** | Config files, paths, permissions |
| **Safety** | Backup done, rollback plan ready |

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Dependencies installed on target
- [ ] Config files verified (paths, credentials)
- [ ] Target folder permissions checked
- [ ] Firewall rules configured (if needed)
- [ ] Backup of current version done
- [ ] Rollback plan documented

---

## 3. Deployment Workflow Principles

### The 5-Phase Process

```
1. PREPARE
   └── Verify code, config, target server

2. BACKUP
   └── Copy current version to backup folder

3. DEPLOY
   └── Copy files, restart services

4. VERIFY
   └── Health check, logs, test key flows

5. CONFIRM or ROLLBACK
   └── All good? Document. Issues? Rollback.
```

### Phase Principles

| Phase | Principle |
|-------|-----------|
| **Prepare** | Never deploy untested code |
| **Backup** | Can't rollback without backup |
| **Deploy** | Watch it happen, check logs |
| **Verify** | Test critical paths immediately |
| **Confirm** | Have rollback trigger ready |

---

## 4. Windows Service Deployment

### Using NSSM (Non-Sucking Service Manager)

| Step | Command/Action |
|------|----------------|
| Install NSSM | Download from nssm.cc |
| Create service | `nssm install ServiceName` |
| Configure | Set path to python.exe and script |
| Start | `nssm start ServiceName` |
| Logs | Configure stdout/stderr redirection |

### Service Best Practices

| Aspect | Recommendation |
|--------|----------------|
| **User** | Dedicated service account |
| **Logging** | Redirect to log files |
| **Recovery** | Configure restart on failure |
| **Dependencies** | Set service dependencies |

---

## 5. IIS + Python Deployment

### wfastcgi Configuration

| Step | Action |
|------|--------|
| Install | `pip install wfastcgi` |
| Enable | `wfastcgi-enable` (as admin) |
| Configure | web.config with handler mapping |
| App Pool | Create dedicated app pool |

### IIS Best Practices

| Aspect | Recommendation |
|--------|----------------|
| **App Pool** | Separate pool per application |
| **Identity** | ApplicationPoolIdentity or dedicated user |
| **Recycling** | Configure based on app needs |
| **Timeout** | Set appropriate request timeout |

---

## 6. Post-Deployment Verification

### What to Verify

| Check | Why |
|-------|-----|
| **Service running** | Process is active |
| **Log files** | No new errors |
| **Key user flows** | Critical features work |
| **Performance** | Response times acceptable |

### Verification Window

- **First 5 minutes**: Active monitoring
- **15 minutes**: Confirm stable
- **1 hour**: Final verification
- **Next day**: Review logs

---

## 7. Rollback Principles

### When to Rollback

| Symptom | Action |
|---------|--------|
| Service won't start | Rollback immediately |
| Critical errors in logs | Rollback |
| Performance degraded >50% | Consider rollback |
| Minor issues | Fix forward if quick |

### Rollback Strategy

| Deployment Type | Rollback Method |
|-----------------|-----------------|
| **File-based** | Restore from backup folder |
| **Windows Service** | Stop, replace files, start |
| **IIS App** | Swap app folders, recycle pool |
| **Task Scheduler** | Update task to old script path |

### Rollback Principles

1. **Speed over perfection**: Rollback first, debug later
2. **Don't compound errors**: One rollback, not multiple changes
3. **Communicate**: Tell team what happened
4. **Post-mortem**: Understand why after stable

---

## 8. Network Share Deployment

### UNC Path Deployment

| Step | Action |
|------|--------|
| Source | Build on dev machine |
| Target | Copy to `\\server\apps\myapp` |
| Permissions | Verify service account access |
| Shortcuts | Update any shortcuts/tasks |

### Best Practices

- Use robocopy for reliable file copy
- Maintain version folders for rollback
- Verify target permissions before deploy

---

## 9. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Deploy on Friday | Deploy early in week |
| Rush deployment | Follow the process |
| Skip backup | Always backup first |
| Deploy without testing | Test in staging/dev first |
| Walk away after deploy | Monitor for 15+ min |
| Multiple changes at once | One change at a time |
| Use mapped drives in services | Use UNC paths |

---

## 10. Decision Checklist

Before deploying:

- [ ] **Backup of current version?**
- [ ] **Rollback plan documented?**
- [ ] **Target server accessible?**
- [ ] **Permissions verified?**
- [ ] **Config files correct?**
- [ ] **Team notified?**
- [ ] **Time to monitor after?**

---

## 11. Best Practices

1. **Small, frequent deploys** over big releases
2. **Version your deployments** (use folders with dates/versions)
3. **Automate** with PowerShell scripts
4. **Document** every deployment
5. **Log everything** for debugging
6. **Test rollback** before you need it

---

> **Remember:** Every deployment is a risk. Minimize risk through preparation, not speed.
