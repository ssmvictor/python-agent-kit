---
name: file-integration
description: File-based integration patterns for Windows on-premise. UNC paths, network shares, file watchers, encoding handling.
tier: standard
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# File Integration (On-Premise)

> File-based integration patterns for Windows enterprise environments.
> **Learn to THINK, not memorize code.**

---

## ⚠️ How to Use This Skill

This skill teaches **file integration decision-making** for on-premise Windows.

- Choose the right approach for your integration
- Handle Windows-specific challenges (paths, encoding, permissions)
- Design for reliability and error recovery

---

## 1. Integration Decision Tree

### Which Pattern to Use?

```
What's your integration scenario?
│
├── Drop file, process, move to done
│   └── Input/Output folder pattern
│
├── Watch for new files in real-time
│   ├── Low latency needed → watchdog library
│   └── Simple polling OK → scheduled check
│
├── Access files on network share
│   └── UNC path pattern (not mapped drives)
│
├── Exchange data with legacy system
│   ├── CSV/Excel → pandas + openpyxl
│   ├── Fixed-width → custom parser
│   └── XML → lxml or ElementTree
│
└── Atomic file operations
    └── Temp file + rename pattern
```

### Comparison Table

| Pattern | Best For | Complexity |
|---------|----------|------------|
| **Polling** | Simple, periodic checks | Low |
| **watchdog** | Real-time file events | Medium |
| **Input/Output folders** | Batch processing | Low |
| **Temp + rename** | Atomic writes | Low |

---

## 2. Path Handling Principles

### UNC vs Mapped Drives

| Type | Example | Use In |
|------|---------|--------|
| **UNC** | `\\server\share\folder` | Services, scheduled tasks |
| **Mapped** | `Z:\folder` | Interactive user only |

> 🔴 **Rule:** Always use UNC paths for automated processes. Mapped drives are user-specific.

### pathlib vs os.path

| Feature | pathlib | os.path |
|---------|---------|---------|
| Syntax | Object-oriented | Function-based |
| UNC support | ✅ Yes | ✅ Yes |
| Modern Python | ✅ Recommended | Legacy |
| Path operations | Cleaner | Verbose |

```python
from pathlib import Path

# UNC path
server_path = Path(r"\\server\share\folder")

# Join paths
file_path = server_path / "data" / "file.csv"

# Check exists
if file_path.exists():
    content = file_path.read_text(encoding='utf-8')
```

For UNC patterns: [references/unc-paths.md](references/unc-paths.md)

---

## 3. Encoding Handling

### Common Encodings in Enterprise

| Encoding | When You'll See It |
|----------|-------------------|
| **UTF-8** | Modern systems, APIs |
| **UTF-8 BOM** | Excel exports, some Windows apps |
| **Windows-1252** | Legacy Windows apps |
| **Latin-1** | Older European systems |
| **ASCII** | Very old systems |

### Detection Strategy

```python
# Try common encodings in order
encodings = ['utf-8-sig', 'utf-8', 'windows-1252', 'latin-1']

for encoding in encodings:
    try:
        content = file_path.read_text(encoding=encoding)
        break
    except UnicodeDecodeError:
        continue
```

### Writing Files

| Target System | Use Encoding |
|---------------|--------------|
| Modern apps | `utf-8` |
| Excel/Windows apps | `utf-8-sig` (with BOM) |
| Legacy systems | Match their encoding |

---

## 4. File Watching Patterns

### When to Use Each

| Approach | Use When |
|----------|----------|
| **Polling** | Simple, small folders, low frequency |
| **watchdog** | Real-time, large folders, many files |
| **Task Scheduler** | Periodic batch, system integration |

### Polling Pattern

```python
from pathlib import Path
import time

def poll_folder(input_dir: Path, interval: int = 60):
    processed = set()
    
    while True:
        for file in input_dir.glob("*.csv"):
            if file.name not in processed:
                process_file(file)
                processed.add(file.name)
        time.sleep(interval)
```

### watchdog Pattern

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            process_file(Path(event.src_path))

observer = Observer()
observer.schedule(FileHandler(), path=str(input_dir), recursive=False)
observer.start()
```

For watcher patterns: [references/file-watchers.md](references/file-watchers.md)

---

## 5. Input/Output Folder Pattern

### Standard Structure

```
\\server\share\app\
├── input\          # Drop files here
├── processing\     # Currently being processed
├── done\           # Successfully processed
├── error\          # Failed processing
└── logs\           # Processing logs
```

### Processing Flow

```
1. Check input/ for new files
2. Move file to processing/
3. Process the file
4. On success: Move to done/
5. On error: Move to error/, log details
```

### Implementation

```python
from pathlib import Path
import shutil

def process_input_folder(base: Path):
    input_dir = base / "input"
    processing_dir = base / "processing"
    done_dir = base / "done"
    error_dir = base / "error"
    
    for file in input_dir.glob("*"):
        # Move to processing
        processing_file = processing_dir / file.name
        shutil.move(file, processing_file)
        
        try:
            process_file(processing_file)
            # Success: move to done
            shutil.move(processing_file, done_dir / file.name)
        except Exception as e:
            # Error: move to error
            shutil.move(processing_file, error_dir / file.name)
            log_error(file.name, e)
```

---

## 6. Atomic File Operations

### The Problem

```
Writing directly to target file:
├── Process crashes mid-write → Corrupt file
├── Reader sees partial data → Processing errors
└── No rollback possible → Data loss
```

### The Solution: Temp + Rename

```python
from pathlib import Path
import tempfile
import shutil

def atomic_write(target: Path, content: str):
    # Write to temp file in same directory
    temp_file = target.with_suffix('.tmp')
    
    try:
        temp_file.write_text(content, encoding='utf-8')
        # Atomic rename (same filesystem)
        temp_file.replace(target)
    except:
        temp_file.unlink(missing_ok=True)
        raise
```

### File Locking

```python
import msvcrt  # Windows only

def locked_write(file_path: Path, content: str):
    with open(file_path, 'w') as f:
        # Lock the file
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        try:
            f.write(content)
        finally:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
```

---

## 7. Error Handling Patterns

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `PermissionError` | File in use, no access | Retry with backoff |
| `FileNotFoundError` | Path doesn't exist | Verify path, create dirs |
| `OSError: Network path` | Share unavailable | Retry, check connectivity |

### Retry Pattern

```python
import time
from pathlib import Path

def read_with_retry(file_path: Path, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return file_path.read_text(encoding='utf-8')
        except (PermissionError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

---

## 8. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Use mapped drives in services | Use UNC paths |
| Write directly to final file | Use temp + rename |
| Ignore encoding | Specify encoding explicitly |
| Process in place | Use input/processing/done folders |
| Ignore file locks | Check if file is complete |
| Hard-code paths | Use config/environment |

---

## 9. Decision Checklist

Before implementing file integration:

- [ ] **UNC paths for all network access?**
- [ ] **Encoding handling defined?**
- [ ] **Error handling with retry?**
- [ ] **Atomic writes for critical files?**
- [ ] **Input/Output folder structure?**
- [ ] **Logging for all operations?**
- [ ] **Permissions verified?**

---

## Reference Files

- [references/unc-paths.md](references/unc-paths.md) - Network share access patterns
- [references/file-watchers.md](references/file-watchers.md) - File monitoring patterns

---

> **Remember:** File-based integration is simple in concept but requires careful error handling. Files can be locked, networks can disconnect, and encodings can surprise you.
