# UNC Paths Reference

> Network share access patterns for Windows.

---

## 1. UNC Path Syntax

### Basic Format

```
\\server\share\folder\file.txt
   │      │      │
   │      │      └── Path within share
   │      └── Share name
   └── Server name or IP
```

### Path Examples

| Type | Example |
|------|---------|
| Server share | `\\fileserver\shared` |
| IP address | `\\192.168.1.100\data` |
| Admin share | `\\server\C$\folder` |
| DFS | `\\domain.com\namespace\folder` |

---

## 2. Python UNC Access

### Using pathlib

```python
from pathlib import Path

# Define UNC path
share = Path(r"\\server\share\data")

# Read file
content = (share / "file.txt").read_text(encoding='utf-8')

# Write file
(share / "output.csv").write_text(data, encoding='utf-8')

# List files
for file in share.glob("*.csv"):
    print(file.name)
```

### Check Connectivity

```python
from pathlib import Path

def is_share_accessible(unc_path: str) -> bool:
    try:
        path = Path(unc_path)
        return path.exists()
    except OSError:
        return False

# Usage
if is_share_accessible(r"\\server\share"):
    process_files()
else:
    log_error("Share not accessible")
```

---

## 3. Authentication

### net use Command

```powershell
# Connect with credentials
net use \\server\share /user:DOMAIN\username password

# Connect and map to drive (interactive use only)
net use Z: \\server\share /user:DOMAIN\username password

# Disconnect
net use \\server\share /delete

# List connections
net use
```

### Python with subprocess

```python
import subprocess

def connect_share(server: str, share: str, user: str, password: str):
    unc = f"\\\\{server}\\{share}"
    cmd = f'net use "{unc}" /user:{user} "{password}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise ConnectionError(f"Failed to connect: {result.stderr}")
    
    return unc

# Usage
unc = connect_share("server", "share", "DOMAIN\\user", "password")
```

### Windows Credential Manager

```python
import keyring

# Store credential (one-time)
keyring.set_password("\\\\server\\share", "username", "password")

# Retrieve credential
password = keyring.get_password("\\\\server\\share", "username")
```

---

## 4. Retry Pattern for Network

```python
import time
from pathlib import Path

def robust_read(file_path: Path, max_retries: int = 5):
    """Read file with retry for network issues."""
    delays = [1, 2, 5, 10, 30]  # Progressive backoff
    
    for attempt in range(max_retries):
        try:
            return file_path.read_text(encoding='utf-8')
        except OSError as e:
            if "network" in str(e).lower() or attempt < max_retries - 1:
                time.sleep(delays[min(attempt, len(delays)-1)])
            else:
                raise

def robust_write(file_path: Path, content: str, max_retries: int = 5):
    """Write file with retry for network issues."""
    delays = [1, 2, 5, 10, 30]
    
    for attempt in range(max_retries):
        try:
            file_path.write_text(content, encoding='utf-8')
            return
        except OSError as e:
            if attempt < max_retries - 1:
                time.sleep(delays[min(attempt, len(delays)-1)])
            else:
                raise
```

---

## 5. File Locking on Network

### Check if File is Complete

```python
import time
from pathlib import Path

def wait_for_file_complete(file_path: Path, timeout: int = 60):
    """Wait until file stops growing (upload complete)."""
    start = time.time()
    last_size = -1
    
    while time.time() - start < timeout:
        try:
            current_size = file_path.stat().st_size
            if current_size == last_size and current_size > 0:
                return True  # Size stable, file complete
            last_size = current_size
            time.sleep(2)
        except OSError:
            time.sleep(2)
    
    return False
```

### Test if File is Locked

```python
from pathlib import Path

def is_file_locked(file_path: Path) -> bool:
    """Check if file is locked by another process."""
    try:
        with open(file_path, 'r+'):
            return False
    except IOError:
        return True
```

---

## 6. Copy Operations

### Using shutil

```python
import shutil
from pathlib import Path

# Copy file
shutil.copy2(src, dst)  # Preserves metadata

# Copy directory
shutil.copytree(src_dir, dst_dir)

# Move (works across network)
shutil.move(src, dst)
```

### Using robocopy (Large Files)

```python
import subprocess

def robocopy_file(src_dir: str, dst_dir: str, filename: str):
    """Use robocopy for reliable network copy."""
    cmd = f'robocopy "{src_dir}" "{dst_dir}" "{filename}" /R:5 /W:10'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    
    # robocopy exit codes: 0-7 are success, 8+ are errors
    if result.returncode >= 8:
        raise IOError(f"Robocopy failed: {result.returncode}")
```

---

## 7. Permissions Issues

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Access Denied | No NTFS permissions | Grant share + NTFS access |
| Network path not found | Server offline or wrong name | Verify server reachable |
| Logon failure | Bad credentials | Verify user/password |

### Check Permissions in Python

```python
import os
from pathlib import Path

def check_permissions(path: Path):
    """Check read/write permissions."""
    result = {
        'exists': path.exists(),
        'readable': os.access(path, os.R_OK),
        'writable': os.access(path, os.W_OK)
    }
    return result
```

---

## 8. Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Use mapped drives in services | Use UNC paths |
| Hard-code credentials | Use Credential Manager |
| Ignore network timeouts | Implement retry logic |
| Assume share always available | Check connectivity first |
| Use single \ in Python strings | Use raw strings r"\\server" |

---

## 9. Service Account Setup

### Best Practices

1. **Dedicated service account** for automated processes
2. **Grant minimum permissions** (only needed folders)
3. **NTFS + Share permissions** both must allow access
4. **Test with service account** before deployment
5. **Log access failures** for troubleshooting

### Test Access

```powershell
# Run as service account
runas /user:DOMAIN\serviceaccount "cmd /c dir \\server\share"
```

---

> **Remember:** UNC paths are essential for services and scheduled tasks. Mapped drives only work for interactive users.
