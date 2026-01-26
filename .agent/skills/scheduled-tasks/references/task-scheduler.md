# Windows Task Scheduler Reference

> CLI commands and patterns for Windows Task Scheduler.

---

## 1. schtasks.exe CLI

### Create Tasks

```powershell
# Basic daily task
schtasks /Create /TN "MyTask" /TR "python C:\scripts\myscript.py" /SC DAILY /ST 08:00

# With specific user
schtasks /Create /TN "MyTask" /TR "python C:\scripts\myscript.py" /SC DAILY /ST 08:00 /RU "DOMAIN\user" /RP "password"

# Run as SYSTEM
schtasks /Create /TN "MyTask" /TR "python C:\scripts\myscript.py" /SC DAILY /ST 08:00 /RU SYSTEM

# Every 5 minutes
schtasks /Create /TN "MyTask" /TR "python C:\scripts\myscript.py" /SC MINUTE /MO 5

# On startup
schtasks /Create /TN "MyTask" /TR "python C:\scripts\myscript.py" /SC ONSTART /RU SYSTEM

# On logon
schtasks /Create /TN "MyTask" /TR "python C:\scripts\myscript.py" /SC ONLOGON
```

### Schedule Types (/SC)

| Value | Description |
|-------|-------------|
| MINUTE | Every N minutes |
| HOURLY | Every N hours |
| DAILY | Every N days |
| WEEKLY | Every N weeks |
| MONTHLY | Specific days of month |
| ONCE | One time only |
| ONSTART | On system startup |
| ONLOGON | On user logon |
| ONIDLE | When system idle |
| ONEVENT | On specific event |

### Common Parameters

| Parameter | Description |
|-----------|-------------|
| /TN | Task name (path with backslashes for folders) |
| /TR | Task run (command to execute) |
| /SC | Schedule type |
| /ST | Start time (HH:MM) |
| /SD | Start date (MM/DD/YYYY) |
| /MO | Modifier (interval for MINUTE/HOURLY) |
| /D | Days (MON,TUE,WED... or 1-31 for monthly) |
| /M | Months (JAN,FEB...) |
| /RU | Run as user |
| /RP | Run as password |
| /RL | Run level (HIGHEST for admin) |
| /F | Force create (overwrite existing) |

---

## 2. Manage Tasks

```powershell
# List all tasks
schtasks /Query

# List specific task
schtasks /Query /TN "MyTask" /V /FO LIST

# Run task immediately
schtasks /Run /TN "MyTask"

# End running task
schtasks /End /TN "MyTask"

# Delete task
schtasks /Delete /TN "MyTask" /F

# Enable/Disable
schtasks /Change /TN "MyTask" /ENABLE
schtasks /Change /TN "MyTask" /DISABLE
```

---

## 3. Task Folder Organization

```powershell
# Create task in folder (folder auto-created)
schtasks /Create /TN "MyCompany\ETL\DailyImport" /TR "..." /SC DAILY /ST 06:00

# Task path structure:
# Task Scheduler Library
# └── MyCompany
#     └── ETL
#         └── DailyImport
```

---

## 4. Event-Triggered Tasks

```powershell
# Trigger on specific Windows Event
schtasks /Create /TN "OnServiceCrash" /TR "python C:\scripts\alert.py" /SC ONEVENT /EC System /MO "*[System[EventID=7034]]"

# Components:
# /EC - Event Channel (System, Application, Security)
# /MO - XPath query for event filter
```

### Common Event Queries

| Event | XPath Query |
|-------|-------------|
| Service crash | `*[System[EventID=7034]]` |
| Logon | `*[System[EventID=4624]]` |
| Disk error | `*[System[EventID=7 or EventID=11]]` |

---

## 5. Python Script Integration

### Wrapper Script Pattern

```powershell
# run_python_task.bat
@echo off
cd /d C:\scripts
C:\Python311\python.exe myscript.py >> C:\logs\myscript_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log 2>&1
exit /b %errorlevel%
```

### Direct Python Call

```powershell
# Task command:
C:\Python311\python.exe C:\scripts\myscript.py

# Start in:
C:\scripts
```

### pythonw.exe for No Console

```powershell
# No console window:
C:\Python311\pythonw.exe C:\scripts\myscript.pyw
```

---

## 6. Advanced Settings (XML)

### Export/Import Tasks

```powershell
# Export
schtasks /Query /TN "MyTask" /XML > MyTask.xml

# Import
schtasks /Create /TN "MyTask" /XML MyTask.xml /F
```

### Key XML Settings

```xml
<Settings>
  <!-- Run even if not logged on -->
  <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
  
  <!-- Stop if runs too long -->
  <ExecutionTimeLimit>PT4H</ExecutionTimeLimit>
  
  <!-- Restart on failure -->
  <RestartOnFailure>
    <Interval>PT5M</Interval>
    <Count>3</Count>
  </RestartOnFailure>
  
  <!-- Allow multiple instances -->
  <MultipleInstancesPolicy>Parallel</MultipleInstancesPolicy>
</Settings>
```

---

## 7. Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Task doesn't run | Check "History" tab, verify paths |
| Access denied | Check user has "Log on as batch job" |
| Can't find Python | Use full path to python.exe |
| Network drive not found | Use UNC paths, not mapped drives |
| Task runs but no output | Check working directory (Start In) |

### Enable History

```powershell
# Via Event Viewer:
# Applications and Services Logs > Microsoft > Windows > TaskScheduler > Operational
# Right-click > Enable Log
```

### Check Last Run Result

| Code | Meaning |
|------|---------|
| 0 (0x0) | Success |
| 1 (0x1) | Generic error |
| 2 (0x2) | File not found |
| 267011 | Task not run (missed) |
| 267014 | Task terminated |

---

> **Remember:** Task Scheduler is reliable but silent. Always log and monitor your scheduled tasks.
