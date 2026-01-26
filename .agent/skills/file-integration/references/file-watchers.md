# File Watchers Reference

> File monitoring patterns for Python.

---

## 1. watchdog Library

### Installation

```bash
pip install watchdog
```

### Basic Usage

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file: {event.src_path}")
            process_file(Path(event.src_path))
    
    def on_modified(self, event):
        if not event.is_directory:
            print(f"Modified: {event.src_path}")
    
    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")
    
    def on_moved(self, event):
        print(f"Moved: {event.src_path} -> {event.dest_path}")

# Start watching
observer = Observer()
observer.schedule(MyHandler(), path="C:\\watch", recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

---

## 2. Pattern Matching

### Filter by Extension

```python
from watchdog.events import PatternMatchingEventHandler

class CSVHandler(PatternMatchingEventHandler):
    patterns = ["*.csv", "*.CSV"]
    ignore_patterns = ["*_temp*", "~*"]
    ignore_directories = True
    
    def on_created(self, event):
        process_csv(Path(event.src_path))

observer.schedule(CSVHandler(), path="C:\\data", recursive=False)
```

### Regex Matching

```python
from watchdog.events import RegexMatchingEventHandler

class DataHandler(RegexMatchingEventHandler):
    regexes = [r".*\d{8}\.csv$"]  # Matches date-stamped CSVs
    
    def on_created(self, event):
        process_file(Path(event.src_path))
```

---

## 3. Debounce Pattern

### Problem: Multiple Events for One Save

```
When file is saved:
├── on_modified (content change)
├── on_modified (metadata update)
└── on_modified (final)
= 3 events for 1 save
```

### Solution: Debounce

```python
from watchdog.events import FileSystemEventHandler
from threading import Timer
from pathlib import Path

class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, callback, delay=1.0):
        self.callback = callback
        self.delay = delay
        self.timers = {}
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        path = event.src_path
        
        # Cancel existing timer for this file
        if path in self.timers:
            self.timers[path].cancel()
        
        # Set new timer
        timer = Timer(self.delay, self._process, [path])
        self.timers[path] = timer
        timer.start()
    
    def _process(self, path):
        del self.timers[path]
        self.callback(Path(path))

# Usage
def process_file(path: Path):
    print(f"Processing: {path}")

handler = DebouncedHandler(process_file, delay=2.0)
```

---

## 4. Wait for File Complete

### Problem: File Still Being Written

```python
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time

class SafeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        # Wait for file to be complete
        if self._wait_for_complete(path):
            self._process_file(path)
    
    def _wait_for_complete(self, path: Path, timeout: int = 60) -> bool:
        """Wait until file size stabilizes."""
        start = time.time()
        last_size = -1
        
        while time.time() - start < timeout:
            try:
                size = path.stat().st_size
                if size == last_size and size > 0:
                    # Also check if file is readable
                    try:
                        with open(path, 'rb'):
                            return True
                    except IOError:
                        pass
                last_size = size
                time.sleep(1)
            except OSError:
                time.sleep(1)
        
        return False
    
    def _process_file(self, path: Path):
        print(f"Processing complete file: {path}")
```

---

## 5. Polling Alternative

### When to Use Polling

| Scenario | Use |
|----------|-----|
| Network shares (UNC paths) | Polling (watchdog may not work) |
| Simple requirements | Polling |
| Guaranteed delivery | Polling + tracking |
| Low frequency checks | Polling |

### Polling Implementation

```python
from pathlib import Path
import time
from typing import Set

class FolderPoller:
    def __init__(self, folder: Path, interval: int = 60):
        self.folder = folder
        self.interval = interval
        self.processed: Set[str] = set()
    
    def poll(self, callback):
        """Poll folder for new files."""
        while True:
            try:
                for file in self.folder.glob("*"):
                    if file.is_file() and file.name not in self.processed:
                        # Wait for complete
                        if self._is_complete(file):
                            callback(file)
                            self.processed.add(file.name)
            except OSError as e:
                print(f"Folder access error: {e}")
            
            time.sleep(self.interval)
    
    def _is_complete(self, file: Path) -> bool:
        """Check if file has stopped growing."""
        try:
            size1 = file.stat().st_size
            time.sleep(2)
            size2 = file.stat().st_size
            return size1 == size2 and size1 > 0
        except OSError:
            return False

# Usage
poller = FolderPoller(Path(r"\\server\share\input"), interval=30)
poller.poll(process_file)
```

---

## 6. Tracking Processed Files

### Using File Marker

```python
from pathlib import Path

def is_processed(file: Path) -> bool:
    marker = file.with_suffix(file.suffix + '.done')
    return marker.exists()

def mark_processed(file: Path):
    marker = file.with_suffix(file.suffix + '.done')
    marker.touch()
```

### Using Database

```python
import sqlite3
from pathlib import Path
from datetime import datetime

class ProcessingTracker:
    def __init__(self, db_path: str = "processed.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS processed (
                filename TEXT PRIMARY KEY,
                processed_at TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()
    
    def is_processed(self, filename: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM processed WHERE filename = ?", 
            (filename,)
        )
        return cur.fetchone() is not None
    
    def mark_processed(self, filename: str, status: str = "success"):
        self.conn.execute(
            "INSERT OR REPLACE INTO processed VALUES (?, ?, ?)",
            (filename, datetime.now().isoformat(), status)
        )
        self.conn.commit()
```

---

## 7. Windows Service Integration

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32serviceutil
import win32service
import win32event

class WatcherService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'FileWatcherService'
    _svc_display_name_ = 'File Watcher Service'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.observer = Observer()
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.observer.stop()
        win32event.SetEvent(self.stop_event)
    
    def SvcDoRun(self):
        handler = MyHandler()
        self.observer.schedule(handler, path="C:\\watch", recursive=False)
        self.observer.start()
        
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        self.observer.join()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(WatcherService)
```

---

## 8. Error Handling

```python
import logging
from watchdog.events import FileSystemEventHandler 
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        try:
            self._process_with_retry(path)
        except Exception as e:
            logger.error(f"Failed to process {path}: {e}")
            self._move_to_error(path)
    
    def _process_with_retry(self, path: Path, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                process_file(path)
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
    
    def _move_to_error(self, path: Path):
        error_dir = path.parent / "error"
        error_dir.mkdir(exist_ok=True)
        path.rename(error_dir / path.name)
```

---

## 9. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Process immediately on event | Wait for file complete |
| Ignore duplicate events | Debounce or deduplicate |
| Rely solely on watchdog for UNC | Use polling for network shares |
| Process without tracking | Track processed files |
| Ignore errors | Log and handle failures |

---

> **Remember:** File watching looks simple but has many edge cases. Always handle incomplete files, duplicate events, and network failures.
