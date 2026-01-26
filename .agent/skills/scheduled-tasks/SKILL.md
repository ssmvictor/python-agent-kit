---
name: scheduled-tasks
description: Task scheduling principles for Windows on-premise. Windows Task Scheduler, Python scheduling libs, daemon patterns.
tier: standard
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Scheduled Tasks (On-Premise)

> Scheduling principles for Windows on-premise environments.
> **Learn to THINK, not memorize commands.**

---

## ⚠️ How to Use This Skill

This skill teaches **scheduling decision-making** for on-premise Windows.

- Choose the right tool for your scheduling need
- Understand trade-offs between approaches
- Design for reliability and recovery

---

## 1. Scheduling Decision Tree

### Which Tool to Use?

```
What are you scheduling?
│
├── One-time or recurring script
│   ├── Runs as specific user → Windows Task Scheduler
│   └── Needs system-level access → Task Scheduler (SYSTEM)
│
├── Python app that must stay running
│   ├── Web API/Service → Windows Service (NSSM)
│   └── Background worker → Windows Service
│
├── In-process scheduling (app manages own schedule)
│   ├── Simple intervals → schedule library
│   ├── Complex schedules → APScheduler
│   └── Distributed tasks → Celery Beat
│
└── Event-driven (file arrives, log entry)
    └── Event-triggered Task Scheduler
```

### Comparison Table

| Tool | Best For | Persistence | Complexity |
|------|----------|-------------|------------|
| **Task Scheduler** | System-level, scripts | OS-managed | Low |
| **schedule** lib | Simple in-process | App-managed | Very Low |
| **APScheduler** | Complex schedules | Configurable | Medium |
| **Windows Service** | Always-on daemons | OS-managed | Medium |
| **Celery Beat** | Distributed workers | Redis/RabbitMQ | High |

---

## 2. Windows Task Scheduler Principles

### When to Use

| Scenario | Use Task Scheduler |
|----------|-------------------|
| Daily/weekly scripts | ✅ Yes |
| On-startup tasks | ✅ Yes |
| Run as different user | ✅ Yes |
| Event-triggered | ✅ Yes |
| Sub-minute scheduling | ❌ No (use in-process) |
| Complex dependencies | ❌ No (use workflow tool) |

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Trigger** | When to run (time, event, startup) |
| **Action** | What to run (script, program) |
| **Conditions** | Prerequisites (network, idle, power) |
| **Settings** | Behavior (retry, timeout, multiple instances) |

### Best Practices

1. **Use full paths** for scripts and interpreters
2. **Set working directory** (Start In)
3. **Configure "Run whether user is logged on"** for unattended
4. **Store credentials** for network access
5. **Enable history** for troubleshooting
6. **Set appropriate timeout** to prevent stuck tasks

For CLI commands: [references/task-scheduler.md](references/task-scheduler.md)

---

## 3. Python Scheduling Libraries

### In-Process Scheduling

| Library | Best For |
|---------|----------|
| **schedule** | Simple, readable intervals |
| **APScheduler** | Advanced, persistent jobs |
| **threading.Timer** | One-time delays |

### When to Use Each

```
Need simple intervals (every 5 min)?
└── schedule

Need cron-like expressions?
└── APScheduler

Need job persistence across restarts?
└── APScheduler with JobStore

Need distributed workers?
└── Celery Beat
```

### Key Considerations

| Factor | Consideration |
|--------|---------------|
| **Process lifetime** | In-process = dies with app |
| **Missed jobs** | APScheduler can "catch up" |
| **Persistence** | APScheduler supports SQLite/SQLAlchemy |
| **Timezone** | Always specify explicitly |

For implementation patterns: [references/python-scheduling.md](references/python-scheduling.md)

---

## 4. Reliability Patterns

### Idempotency

```
Design jobs to be safe to run multiple times:
├── Check if work already done
├── Use transactions where possible
├── Log state before/after
└── Handle partial completion
```

### Error Handling

| Strategy | Implementation |
|----------|----------------|
| **Retry** | Task Scheduler: configure in Settings |
| **Logging** | Always log start, end, errors |
| **Alerting** | Send email/notification on failure |
| **Dead letter** | Move failed items for manual review |

### Recovery

```
After restart/crash:
├── Task Scheduler: automatic (OS-managed)
├── schedule: jobs lost (no persistence)
├── APScheduler: can recover (with JobStore)
└── Windows Service: auto-restart configurable
```

---

## 5. Logging Best Practices

### Log Structure

| Element | Purpose |
|---------|---------|
| **Timestamp** | When it happened |
| **Job ID** | Which run |
| **Status** | Started/Completed/Failed |
| **Duration** | How long it took |
| **Details** | What was processed |

### Log Location

| Context | Recommended Location |
|---------|---------------------|
| Task Scheduler | `C:\Logs\TaskName\` |
| Windows Service | Windows Event Log + file |
| Python app | `logging` module to file |

---

## 6. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Rely on user being logged in | Use "Run whether user logged on" |
| Use relative paths | Use absolute paths |
| Ignore exit codes | Check and log exit codes |
| Schedule at exact same time | Stagger similar tasks |
| Skip logging | Log everything |
| Assume success | Verify and alert on failure |
| Use mapped drives | Use UNC paths |

---

## 7. Decision Checklist

Before implementing scheduled task:

- [ ] **Right tool for the schedule?** (Task Scheduler vs in-process)
- [ ] **Full paths configured?**
- [ ] **Working directory set?**
- [ ] **Run credentials correct?**
- [ ] **Logging configured?**
- [ ] **Error handling in place?**
- [ ] **Retry strategy defined?**
- [ ] **Alerting on failure?**

---

## Reference Files

- [references/task-scheduler.md](references/task-scheduler.md) - Windows Task Scheduler CLI and patterns
- [references/python-scheduling.md](references/python-scheduling.md) - Python scheduling libraries

---

> **Remember:** Scheduled tasks are "fire and forget" - invest in logging and alerting, or you won't know when they fail.
