# pywin32 Patterns

> Windows API automation with pywin32.
> **Typed, context-managed, enterprise-ready.**

---

## 1. Installation & Setup

```bash
pip install pywin32
# After install, run (required on some systems):
python -m pywin32_postinstall -install
```

---

## 2. COM Object Patterns

### Safe COM Initialization

```python
from contextlib import contextmanager
from typing import Generator, Any, TypeVar
import pythoncom
import win32com.client

T = TypeVar('T')


@contextmanager
def com_apartment() -> Generator[None, None, None]:
    """Initialize COM apartment for current thread."""
    pythoncom.CoInitialize()
    try:
        yield
    finally:
        pythoncom.CoUninitialize()


def dispatch(prog_id: str) -> Any:
    """Create COM object from ProgID."""
    return win32com.client.Dispatch(prog_id)


def dispatch_ex(prog_id: str) -> Any:
    """Create COM object with early binding (type library)."""
    return win32com.client.gencache.EnsureDispatch(prog_id)
```

### Typed COM Client

```python
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class COMApplication(Protocol):
    """Protocol for COM applications."""
    Visible: bool
    def Quit(self) -> None: ...


class COMClient[T: COMApplication]:
    """Generic COM client with type hints."""
    
    def __init__(self, prog_id: str) -> None:
        self._prog_id = prog_id
        self._app: T | None = None
    
    @property
    def app(self) -> T:
        if self._app is None:
            raise RuntimeError("COM client not initialized")
        return self._app
    
    def __enter__(self) -> T:
        pythoncom.CoInitialize()
        self._app = win32com.client.Dispatch(self._prog_id)
        return self._app
    
    def __exit__(self, *args) -> None:
        if self._app:
            try:
                self._app.Quit()
            except Exception:
                pass
            self._app = None
        pythoncom.CoUninitialize()


# Usage:
with COMClient[Any]("Excel.Application") as excel:
    excel.Visible = False
    wb = excel.Workbooks.Add()
    # Work with workbook
```

---

## 3. Excel Automation

### Read/Write Operations

```python
from pathlib import Path
from typing import Any, List, Optional
from dataclasses import dataclass


@dataclass
class CellRange:
    """Represents a cell range."""
    start_row: int
    start_col: int
    end_row: int
    end_col: int
    
    def to_address(self, sheet: Any) -> str:
        """Convert to Excel address (e.g., 'A1:D10')."""
        start = sheet.Cells(self.start_row, self.start_col).Address
        end = sheet.Cells(self.end_row, self.end_col).Address
        return f"{start}:{end}"


class ExcelOperations:
    """Excel read/write operations."""
    
    def __init__(self, app: Any) -> None:
        self._app = app
    
    def open_workbook(
        self, 
        path: Path, 
        read_only: bool = False
    ) -> Any:
        """Open workbook from path."""
        return self._app.Workbooks.Open(
            str(path.absolute()),
            ReadOnly=read_only
        )
    
    def read_range(
        self,
        sheet: Any,
        address: str
    ) -> List[List[Any]]:
        """Read data from range address."""
        data = sheet.Range(address).Value
        
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
        """Write 2D data starting at cell."""
        if not data or not data[0]:
            return
        
        rows = len(data)
        cols = len(data[0])
        
        start = sheet.Range(start_cell)
        end = sheet.Cells(start.Row + rows - 1, start.Column + cols - 1)
        
        sheet.Range(start, end).Value = data
    
    def find_last_row(
        self,
        sheet: Any,
        column: int = 1
    ) -> int:
        """Find last used row in column."""
        return sheet.Cells(sheet.Rows.Count, column).End(-4162).Row  # xlUp
    
    def find_last_column(
        self,
        sheet: Any,
        row: int = 1
    ) -> int:
        """Find last used column in row."""
        return sheet.Cells(row, sheet.Columns.Count).End(-4159).Column  # xlToLeft


# Usage:
with COMClient("Excel.Application") as excel:
    excel.Visible = False
    ops = ExcelOperations(excel)
    
    wb = ops.open_workbook(Path("data.xlsx"), read_only=True)
    ws = wb.Sheets("Sheet1")
    
    last_row = ops.find_last_row(ws)
    data = ops.read_range(ws, f"A1:D{last_row}")
    
    wb.Close(False)
```

---

## 4. Outlook Automation

### Email Operations

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class EmailMessage:
    """Email message data."""
    to: List[str]
    subject: str
    body: str
    cc: List[str] | None = None
    attachments: List[str] | None = None
    html_body: bool = False


class OutlookOperations:
    """Outlook automation operations."""
    
    def __init__(self, app: Any) -> None:
        self._app = app
        self._namespace = app.GetNamespace("MAPI")
    
    def send_email(self, msg: EmailMessage) -> bool:
        """Send email via Outlook."""
        try:
            mail = self._app.CreateItem(0)  # olMailItem
            
            mail.To = "; ".join(msg.to)
            mail.Subject = msg.subject
            
            if msg.html_body:
                mail.HTMLBody = msg.body
            else:
                mail.Body = msg.body
            
            if msg.cc:
                mail.CC = "; ".join(msg.cc)
            
            if msg.attachments:
                for path in msg.attachments:
                    mail.Attachments.Add(path)
            
            mail.Send()
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to send email: {e}")
    
    def get_inbox_messages(
        self,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[dict]:
        """Get messages from inbox."""
        inbox = self._namespace.GetDefaultFolder(6)  # olFolderInbox
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        
        if unread_only:
            messages = messages.Restrict("[UnRead] = True")
        
        result = []
        for i, msg in enumerate(messages):
            if i >= limit:
                break
            result.append({
                "subject": msg.Subject,
                "sender": msg.SenderEmailAddress,
                "received": msg.ReceivedTime,
                "unread": msg.UnRead
            })
        
        return result


# Usage:
with COMClient("Outlook.Application") as outlook:
    ops = OutlookOperations(outlook)
    
    email = EmailMessage(
        to=["user@example.com"],
        subject="Test Email",
        body="This is a test email."
    )
    ops.send_email(email)
```

---

## 5. Word Automation

### Document Operations

```python
from pathlib import Path
from typing import Any, List


class WordOperations:
    """Word document operations."""
    
    def __init__(self, app: Any) -> None:
        self._app = app
    
    def open_document(
        self,
        path: Path,
        read_only: bool = False
    ) -> Any:
        """Open Word document."""
        return self._app.Documents.Open(
            str(path.absolute()),
            ReadOnly=read_only
        )
    
    def create_document(self) -> Any:
        """Create new document."""
        return self._app.Documents.Add()
    
    def replace_text(
        self,
        doc: Any,
        find_text: str,
        replace_text: str,
        replace_all: bool = True
    ) -> int:
        """Find and replace text in document."""
        find = doc.Content.Find
        find.ClearFormatting()
        find.Replacement.ClearFormatting()
        
        count = 0
        while find.Execute(
            FindText=find_text,
            ReplaceWith=replace_text,
            Replace=2 if replace_all else 1  # wdReplaceAll / wdReplaceOne
        ):
            count += 1
            if not replace_all:
                break
        
        return count
    
    def export_to_pdf(
        self,
        doc: Any,
        output_path: Path
    ) -> None:
        """Export document to PDF."""
        doc.ExportAsFixedFormat(
            str(output_path.absolute()),
            17,  # wdExportFormatPDF
            False,
            0,
            0,
            1,
            1,
            0
        )


# Usage:
with COMClient("Word.Application") as word:
    word.Visible = False
    ops = WordOperations(word)
    
    doc = ops.open_document(Path("template.docx"))
    ops.replace_text(doc, "{{NAME}}", "John Doe")
    ops.export_to_pdf(doc, Path("output.pdf"))
    doc.Close(False)
```

---

## 6. Windows Services

### Service Control

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import win32service
import win32serviceutil


class ServiceState(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    PENDING = "pending"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Windows service information."""
    name: str
    display_name: str
    state: ServiceState
    start_type: str


class ServiceManager:
    """Manage Windows services."""
    
    @staticmethod
    def _state_to_enum(state: int) -> ServiceState:
        mapping = {
            win32service.SERVICE_RUNNING: ServiceState.RUNNING,
            win32service.SERVICE_STOPPED: ServiceState.STOPPED,
            win32service.SERVICE_PAUSED: ServiceState.PAUSED,
            win32service.SERVICE_START_PENDING: ServiceState.PENDING,
            win32service.SERVICE_STOP_PENDING: ServiceState.PENDING,
        }
        return mapping.get(state, ServiceState.UNKNOWN)
    
    def get_status(self, service_name: str) -> ServiceInfo:
        """Get service status."""
        try:
            status = win32serviceutil.QueryServiceStatus(service_name)
            return ServiceInfo(
                name=service_name,
                display_name=service_name,
                state=self._state_to_enum(status[1]),
                start_type="unknown"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to query service {service_name}: {e}")
    
    def start(self, service_name: str, wait: bool = True) -> bool:
        """Start a service."""
        try:
            win32serviceutil.StartService(service_name)
            if wait:
                win32serviceutil.WaitForServiceStatus(
                    service_name,
                    win32service.SERVICE_RUNNING,
                    30
                )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to start {service_name}: {e}")
    
    def stop(self, service_name: str, wait: bool = True) -> bool:
        """Stop a service."""
        try:
            win32serviceutil.StopService(service_name)
            if wait:
                win32serviceutil.WaitForServiceStatus(
                    service_name,
                    win32service.SERVICE_STOPPED,
                    30
                )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to stop {service_name}: {e}")
```

---

## 7. Registry Operations

```python
from typing import Any, Optional
import winreg


class RegistryOperations:
    """Windows Registry operations."""
    
    HIVES = {
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKCR": winreg.HKEY_CLASSES_ROOT,
    }
    
    def read_value(
        self,
        hive: str,
        key_path: str,
        value_name: str
    ) -> Optional[Any]:
        """Read registry value."""
        hive_key = self.HIVES.get(hive)
        if not hive_key:
            raise ValueError(f"Unknown hive: {hive}")
        
        try:
            with winreg.OpenKey(hive_key, key_path) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
        except FileNotFoundError:
            return None
    
    def write_value(
        self,
        hive: str,
        key_path: str,
        value_name: str,
        value: Any,
        value_type: int = winreg.REG_SZ
    ) -> bool:
        """Write registry value."""
        hive_key = self.HIVES.get(hive)
        if not hive_key:
            raise ValueError(f"Unknown hive: {hive}")
        
        try:
            with winreg.CreateKeyEx(hive_key, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value)
                return True
        except PermissionError:
            raise RuntimeError("Insufficient permissions to write registry")
```

---

> **Remember**: pywin32 is powerful but requires careful resource management. Always use context managers and handle COM errors gracefully.
