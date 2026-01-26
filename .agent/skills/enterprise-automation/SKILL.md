---
name: enterprise-automation
description: Windows enterprise automation principles. pywin32, COM automation, Selenium, scheduled tasks. Teaches OOP patterns for reliable automation.
tier: standard
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Enterprise Automation Skill

> Windows automation principles for enterprise environments.
> **OOP-first, strongly-typed, production-ready.**

---

## ⚠️ How to Use This Skill

This skill teaches **decision-making principles** for enterprise automation, not fixed code to copy.

- ASK about target application before choosing technology
- Consider GUI vs API automation based on CONTEXT
- Always implement proper error handling and cleanup

---

## 1. Technology Selection (2025)

### Decision Tree

```
What are you automating?
│
├── Microsoft Office (Excel, Word, Outlook)
│   └── win32com.client (COM automation)
│
├── Windows services/processes
│   └── pywin32 + subprocess
│
├── Web application (modern)
│   └── Selenium or Playwright
│
├── Web application (legacy/IE)
│   └── Selenium with IE mode
│
├── Windows desktop GUI app
│   └── pywinauto or pyautogui
│
├── File system monitoring
│   └── watchdog
│
└── Command line / scripts
    └── subprocess + PowerShell
```

### Comparison Principles

| Factor | pywin32 | Selenium | pywinauto |
|--------|---------|----------|-----------|
| **Best for** | Office/COM apps | Web apps | Desktop GUI |
| **Reliability** | High | Medium | Medium |
| **Setup complexity** | Low | Medium | Medium |
| **Maintenance** | Low | High (UI changes) | High |
| **Headless support** | Yes | Yes | No |

### Selection Questions to Ask:

1. What application needs automation?
2. Is there an API available?
3. Is the target GUI stable or frequently changing?
4. Does it need to run headless/unattended?
5. What's the error recovery strategy?

---

## 2. OOP Patterns for Automation

### Pattern Philosophy

```
Every automation should be:
├── Encapsulated in a class
├── Typed with configuration dataclasses
├── Testable in isolation
├── Recoverable from errors
└── Logged for debugging
```

### Base Automation Pattern

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar, Any
import logging

logger = logging.getLogger(__name__)


class AutomationStatus(str, Enum):
    """Automation execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class AutomationResult:
    """Result of an automation run."""
    status: AutomationStatus
    started_at: datetime
    ended_at: datetime | None = None
    message: str = ""
    output: Any = None
    errors: list[str] = field(default_factory=list)
    retry_count: int = 0
    
    @property
    def duration_seconds(self) -> float:
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0.0
    
    @property
    def success(self) -> bool:
        return self.status == AutomationStatus.SUCCESS


Config = TypeVar('Config')


class BaseAutomation(ABC, Generic[Config]):
    """Abstract base for all automation tasks."""
    
    def __init__(self, config: Config, max_retries: int = 3) -> None:
        self._config = config
        self._max_retries = max_retries
        self._logger = logging.getLogger(self.__class__.__name__)
    
    @property
    def config(self) -> Config:
        return self._config
    
    @abstractmethod
    def validate(self) -> tuple[bool, str]:
        """Validate environment is ready. Return (is_valid, message)."""
        ...
    
    @abstractmethod
    def execute(self) -> AutomationResult:
        """Execute the automation task."""
        ...
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources after execution."""
        ...
    
    def run(self) -> AutomationResult:
        """Run automation with validation, retries, and cleanup."""
        result = AutomationResult(
            status=AutomationStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Validate environment
        is_valid, msg = self.validate()
        if not is_valid:
            result.status = AutomationStatus.FAILED
            result.message = f"Validation failed: {msg}"
            result.ended_at = datetime.now()
            return result
        
        # Execute with retries
        for attempt in range(self._max_retries):
            try:
                result = self.execute()
                if result.success:
                    break
            except Exception as e:
                result.errors.append(f"Attempt {attempt + 1}: {e}")
                result.retry_count = attempt + 1
                self._logger.warning(f"Attempt {attempt + 1} failed: {e}")
        
        # Cleanup
        try:
            self.cleanup()
        except Exception as e:
            self._logger.error(f"Cleanup failed: {e}")
        
        result.ended_at = datetime.now()
        return result
```

---

## 3. COM Automation Patterns

### COM Session Context Manager

```python
from contextlib import contextmanager
from typing import Generator, Any
import pythoncom


@contextmanager
def com_session() -> Generator[None, None, None]:
    """Initialize and cleanup COM session."""
    pythoncom.CoInitialize()
    try:
        yield
    finally:
        pythoncom.CoUninitialize()


class COMClient:
    """Type-safe COM client wrapper."""
    
    def __init__(self, prog_id: str) -> None:
        self._prog_id = prog_id
        self._client: Any = None
    
    def __enter__(self) -> Any:
        import win32com.client
        pythoncom.CoInitialize()
        self._client = win32com.client.Dispatch(self._prog_id)
        return self._client
    
    def __exit__(self, *args) -> None:
        self._client = None
        pythoncom.CoUninitialize()


# Usage:
with COMClient("Excel.Application") as excel:
    excel.Visible = False
    wb = excel.Workbooks.Open(r"C:\data\file.xlsx")
    # Work with workbook
    wb.Close(False)
    excel.Quit()
```

### Typed Excel Automation

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List


@dataclass
class ExcelConfig:
    """Excel automation configuration."""
    visible: bool = False
    display_alerts: bool = False
    enable_events: bool = False


class ExcelAutomation:
    """Typed Excel COM automation."""
    
    def __init__(self, config: ExcelConfig) -> None:
        self._config = config
        self._app: Any = None
    
    def __enter__(self) -> 'ExcelAutomation':
        import win32com.client
        pythoncom.CoInitialize()
        self._app = win32com.client.Dispatch("Excel.Application")
        self._app.Visible = self._config.visible
        self._app.DisplayAlerts = self._config.display_alerts
        self._app.EnableEvents = self._config.enable_events
        return self
    
    def __exit__(self, *args) -> None:
        if self._app:
            self._app.Quit()
            self._app = None
        pythoncom.CoUninitialize()
    
    def open_workbook(self, path: Path) -> Any:
        """Open Excel workbook."""
        return self._app.Workbooks.Open(str(path.absolute()))
    
    def read_range(self, sheet: Any, range_addr: str) -> List[List[Any]]:
        """Read data from range."""
        data = sheet.Range(range_addr).Value
        if data is None:
            return []
        if not isinstance(data, tuple):
            return [[data]]
        return [list(row) for row in data]
    
    def write_range(
        self, 
        sheet: Any, 
        start_cell: str, 
        data: List[List[Any]]
    ) -> None:
        """Write data to range starting at cell."""
        if not data or not data[0]:
            return
        
        rows = len(data)
        cols = len(data[0])
        
        # Calculate end cell
        start_col = sheet.Range(start_cell).Column
        start_row = sheet.Range(start_cell).Row
        end_cell = sheet.Cells(start_row + rows - 1, start_col + cols - 1).Address
        
        sheet.Range(f"{start_cell}:{end_cell}").Value = data


# Usage:
config = ExcelConfig(visible=False)
with ExcelAutomation(config) as excel:
    wb = excel.open_workbook(Path("data.xlsx"))
    ws = wb.Sheets("Sheet1")
    data = excel.read_range(ws, "A1:D100")
    wb.Close(SaveChanges=False)
```

---

## 4. Selenium Patterns

### Typed Selenium Automation

```python
from dataclasses import dataclass
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


@dataclass
class SeleniumConfig:
    """Selenium configuration."""
    headless: bool = True
    timeout: int = 30
    implicit_wait: int = 10
    window_size: tuple[int, int] = (1920, 1080)


class SeleniumAutomation:
    """Typed Selenium automation base."""
    
    def __init__(self, config: SeleniumConfig) -> None:
        self._config = config
        self._driver: Optional[webdriver.Chrome] = None
    
    def __enter__(self) -> 'SeleniumAutomation':
        options = webdriver.ChromeOptions()
        
        if self._config.headless:
            options.add_argument("--headless=new")
        
        options.add_argument(f"--window-size={self._config.window_size[0]},{self._config.window_size[1]}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        self._driver = webdriver.Chrome(options=options)
        self._driver.implicitly_wait(self._config.implicit_wait)
        
        return self
    
    def __exit__(self, *args) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None
    
    @property
    def driver(self) -> webdriver.Chrome:
        if not self._driver:
            raise RuntimeError("Driver not initialized. Use context manager.")
        return self._driver
    
    def navigate(self, url: str) -> None:
        """Navigate to URL."""
        self.driver.get(url)
    
    def wait_for(
        self, 
        by: By, 
        value: str, 
        timeout: Optional[int] = None
    ) -> WebElement:
        """Wait for element to be present and return it."""
        wait = WebDriverWait(self.driver, timeout or self._config.timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_and_click(self, by: By, value: str) -> None:
        """Wait for element to be clickable and click it."""
        wait = WebDriverWait(self.driver, self._config.timeout)
        element = wait.until(EC.element_to_be_clickable((by, value)))
        element.click()
    
    def find_all(self, by: By, value: str) -> List[WebElement]:
        """Find all matching elements."""
        return self.driver.find_elements(by, value)
    
    def take_screenshot(self, path: str) -> bool:
        """Take screenshot and save to path."""
        return self.driver.save_screenshot(path)


# Usage:
config = SeleniumConfig(headless=True)
with SeleniumAutomation(config) as browser:
    browser.navigate("https://example.com/login")
    browser.wait_for(By.ID, "username").send_keys("user")
    browser.wait_for(By.ID, "password").send_keys("pass")
    browser.wait_and_click(By.ID, "submit")
```

---

## 5. Error Handling Patterns

### Typed Automation Exceptions

```python
from dataclasses import dataclass
from typing import Optional


class AutomationError(Exception):
    """Base automation exception."""
    pass


@dataclass
class COMError(AutomationError):
    """COM automation failed."""
    prog_id: str
    operation: str
    reason: str
    
    def __str__(self) -> str:
        return f"COM Error ({self.prog_id}): {self.operation} failed - {self.reason}"


@dataclass
class ElementNotFoundError(AutomationError):
    """Web element not found."""
    by: str
    value: str
    timeout: int
    
    def __str__(self) -> str:
        return f"Element not found: {self.by}='{self.value}' (timeout: {self.timeout}s)"


@dataclass
class TimeoutError(AutomationError):
    """Operation timed out."""
    operation: str
    timeout: int
    
    def __str__(self) -> str:
        return f"Timeout: {self.operation} did not complete in {self.timeout}s"
```

### Retry Pattern

```python
from typing import Callable, TypeVar, Tuple, Type
from functools import wraps
import time
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """Retry decorator with exponential backoff."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error: Optional[Exception] = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_attempts} "
                        f"failed: {e}"
                    )
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_error  # type: ignore
        
        return wrapper
    return decorator
```

---

## 6. Process Automation

### Subprocess Wrapper

```python
from dataclasses import dataclass
from typing import Optional, List
import subprocess
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """Result of process execution."""
    return_code: int
    stdout: str
    stderr: str
    
    @property
    def success(self) -> bool:
        return self.return_code == 0


class ProcessRunner:
    """Typed subprocess wrapper."""
    
    def __init__(
        self, 
        timeout: int = 300,
        encoding: str = 'utf-8'
    ) -> None:
        self._timeout = timeout
        self._encoding = encoding
    
    def run(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        env: Optional[dict] = None
    ) -> ProcessResult:
        """Run command and return result."""
        logger.info(f"Running: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=self._timeout,
                cwd=cwd,
                env=env,
                encoding=self._encoding
            )
            
            return ProcessResult(
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except subprocess.TimeoutExpired as e:
            return ProcessResult(
                return_code=-1,
                stdout="",
                stderr=f"Timeout after {self._timeout}s"
            )
    
    def run_powershell(
        self,
        script: str,
        **kwargs
    ) -> ProcessResult:
        """Run PowerShell script."""
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-Command", script
        ]
        return self.run(command, **kwargs)


# Usage:
runner = ProcessRunner(timeout=60)
result = runner.run_powershell("Get-Process | Select-Object -First 5")
if result.success:
    print(result.stdout)
```

---

## 7. Scheduling Patterns

### Windows Task Scheduler Integration

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class TaskConfig:
    """Windows Task Scheduler task configuration."""
    name: str
    executable: str
    arguments: str = ""
    working_directory: Optional[str] = None
    run_as_user: str = "SYSTEM"
    run_whether_logged_on: bool = True


class TaskSchedulerManager:
    """Manage Windows Task Scheduler tasks."""
    
    def __init__(self) -> None:
        import win32com.client
        self._scheduler = win32com.client.Dispatch("Schedule.Service")
        self._scheduler.Connect()
    
    def create_daily_task(
        self,
        config: TaskConfig,
        start_time: datetime,
        days_interval: int = 1
    ) -> bool:
        """Create a daily scheduled task."""
        try:
            root_folder = self._scheduler.GetFolder("\\")
            
            task_def = self._scheduler.NewTask(0)
            task_def.RegistrationInfo.Description = f"Automated task: {config.name}"
            
            # Trigger
            trigger = task_def.Triggers.Create(2)  # Daily trigger
            trigger.StartBoundary = start_time.isoformat()
            trigger.DaysInterval = days_interval
            trigger.Enabled = True
            
            # Action
            action = task_def.Actions.Create(0)  # Execute
            action.Path = config.executable
            action.Arguments = config.arguments
            if config.working_directory:
                action.WorkingDirectory = config.working_directory
            
            # Settings
            task_def.Settings.Enabled = True
            task_def.Settings.StopIfGoingOnBatteries = False
            
            # Register
            root_folder.RegisterTaskDefinition(
                config.name,
                task_def,
                6,  # TASK_CREATE_OR_UPDATE
                None,
                None,
                3 if config.run_whether_logged_on else 1
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return False
```

---

## 📚 References

See detailed patterns in:
- [pywin32-patterns.md](./references/pywin32-patterns.md)
- [selenium-enterprise.md](./references/selenium-enterprise.md)
- [com-automation.md](./references/com-automation.md)

---

## ✅ Decision Checklist

Before implementing automation:

- [ ] Chose technology based on target application?
- [ ] Created typed configuration dataclass?
- [ ] Implemented context managers for cleanup?
- [ ] Added retry logic for transient failures?
- [ ] Implemented proper error handling?
- [ ] Added logging for debugging?
- [ ] Secured credentials properly?
- [ ] Tested on target environment?

---

> **Remember**: Enterprise automation must be reliable. Build for the failure case first.
