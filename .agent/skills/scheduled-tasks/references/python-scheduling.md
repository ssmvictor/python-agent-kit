# Python Scheduling Libraries Reference

> Patterns for in-process scheduling in Python.

---

## 1. schedule Library

### Installation

```bash
pip install schedule
```

### Basic Usage

```python
import schedule
import time

def job():
    print("Running job...")

# Every N units
schedule.every(10).minutes.do(job)
schedule.every(2).hours.do(job)
schedule.every().day.at("08:00").do(job)

# Specific days
schedule.every().monday.at("09:00").do(job)
schedule.every().wednesday.at("13:15").do(job)

# Run loop
while True:
    schedule.run_pending()
    time.sleep(60)
```

### With Arguments

```python
def process_file(filename):
    print(f"Processing {filename}")

schedule.every().hour.do(process_file, filename="data.csv")
```

### Cancel Jobs

```python
job = schedule.every().day.do(my_job)
schedule.cancel_job(job)

# Clear all
schedule.clear()
```

---

## 2. APScheduler

### Installation

```bash
pip install apscheduler
```

### Basic Usage

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=30)
def job_every_30_min():
    print(f"Running at {datetime.now()}")

@scheduler.scheduled_job('cron', hour=8, minute=0)
def daily_report():
    print("Daily report")

scheduler.start()
```

### Trigger Types

| Type | Use Case |
|------|----------|
| `interval` | Fixed intervals |
| `cron` | Unix cron expressions |
| `date` | One-time execution |

### Cron Examples

```python
# Every weekday at 8 AM
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=8)
def weekday_job():
    pass

# First day of month
@scheduler.scheduled_job('cron', day=1, hour=0, minute=0)
def monthly_job():
    pass

# Every 5 minutes
@scheduler.scheduled_job('cron', minute='*/5')
def frequent_job():
    pass
```

### Job Persistence (SQLite)

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}

scheduler = BlockingScheduler(jobstores=jobstores)

# Jobs survive restart
scheduler.add_job(my_job, 'interval', hours=1, id='my_job', replace_existing=True)
```

### Missed Jobs

```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler(
    job_defaults={
        'coalesce': True,  # Combine missed runs
        'max_instances': 1,
        'misfire_grace_time': 3600  # 1 hour grace
    }
)
```

---

## 3. Background Scheduler (Non-Blocking)

```python
from apscheduler.schedulers.background import BackgroundScheduler
import time

scheduler = BackgroundScheduler()
scheduler.add_job(my_job, 'interval', minutes=5)
scheduler.start()

# Main app continues
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()
```

---

## 4. Windows Service Pattern

### Using pywin32

```python
import win32serviceutil
import win32service
import win32event
import servicemanager
from apscheduler.schedulers.background import BackgroundScheduler

class MySchedulerService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'MySchedulerService'
    _svc_display_name_ = 'My Scheduler Service'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.scheduler = BackgroundScheduler()
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.scheduler.shutdown()
        win32event.SetEvent(self.stop_event)
    
    def SvcDoRun(self):
        self.scheduler.add_job(my_job, 'interval', minutes=5)
        self.scheduler.start()
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MySchedulerService)
```

### Install Service

```powershell
python my_service.py install
python my_service.py start
```

---

## 5. Comparison Table

| Feature | schedule | APScheduler |
|---------|----------|-------------|
| Complexity | Simple | Advanced |
| Cron expressions | No | Yes |
| Job persistence | No | Yes |
| Missed job handling | No | Yes |
| Multiple schedulers | No | Yes |
| Job stores | Memory | SQLite, Redis, MongoDB |
| Executor types | Sync | Thread, Process, AsyncIO |

---

## 6. Error Handling

### With schedule

```python
import schedule
import traceback

def safe_job():
    try:
        do_work()
    except Exception as e:
        log_error(e)
        traceback.print_exc()

schedule.every().hour.do(safe_job)
```

### With APScheduler

```python
from apscheduler.events import EVENT_JOB_ERROR

def error_listener(event):
    print(f"Job {event.job_id} failed: {event.exception}")
    # Send alert, log, etc.

scheduler.add_listener(error_listener, EVENT_JOB_ERROR)
```

---

## 7. Best Practices

| Practice | Why |
|----------|-----|
| Use timezone-aware times | Avoid DST issues |
| Add unique job IDs | Prevent duplicates |
| Configure max_instances | Prevent overlapping |
| Handle graceful shutdown | Clean exit |
| Log job start/end | Debugging |
| Use job stores for critical jobs | Survive restarts |

---

## 8. When to Use What

| Scenario | Recommended |
|----------|-------------|
| Simple script with intervals | schedule |
| Complex schedules (cron-like) | APScheduler |
| Must survive restarts | APScheduler + JobStore |
| Windows service | APScheduler + pywin32 |
| Just run on schedule | Windows Task Scheduler |
| Distributed workers | Celery Beat |

---

> **Remember:** In-process schedulers die with your app. For critical tasks, use Task Scheduler or persistent job stores.
