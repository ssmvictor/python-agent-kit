# COM Automation Patterns

> Component Object Model automation with Python.
> **Thread-safe, typed, enterprise-ready.**

---

## 1. COM Fundamentals

### Threading Models

```python
"""
COM Threading Apartments:

STA (Single-Threaded Apartment):
├── pythoncom.CoInitialize()
├── One thread, one apartment
├── Simpler, most common
└── Required for most Office apps

MTA (Multi-Threaded Apartment):
├── pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
├── Multiple threads share apartment
└── More complex, fewer restrictions
"""

import pythoncom
from typing import Generator
from contextlib import contextmanager


@contextmanager
def sta_apartment() -> Generator[None, None, None]:
    """Single-Threaded Apartment context."""
    pythoncom.CoInitialize()
    try:
        yield
    finally:
        pythoncom.CoUninitialize()


@contextmanager
def mta_apartment() -> Generator[None, None, None]:
    """Multi-Threaded Apartment context."""
    pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    try:
        yield
    finally:
        pythoncom.CoUninitialize()
```

---

## 2. COM Client Patterns

### Late Binding vs Early Binding

```python
import win32com.client
from typing import Any


def late_binding(prog_id: str) -> Any:
    """
    Late binding - no type information at design time.
    
    Pros: Works with any COM object, no setup needed
    Cons: No IntelliSense, runtime errors for typos
    """
    return win32com.client.Dispatch(prog_id)


def early_binding(prog_id: str) -> Any:
    """
    Early binding - generates Python wrapper with type info.
    
    Pros: IntelliSense, compile-time checks, faster
    Cons: Need to generate type library first
    """
    # First time: generates files in gen_py folder
    return win32com.client.gencache.EnsureDispatch(prog_id)


def get_constants(prog_id: str):
    """Get COM constants (for early binding)."""
    return win32com.client.constants


# Usage for early binding setup:
# python -m win32com.client.makepy "Microsoft Excel 16.0 Object Library"
```

### Generic COM Client

```python
from typing import TypeVar, Generic, Any, Protocol
from dataclasses import dataclass
import pythoncom
import win32com.client


class COMApp(Protocol):
    """Protocol for COM applications."""
    Visible: bool
    def Quit(self) -> None: ...


T = TypeVar('T', bound=COMApp)


@dataclass
class COMConfig:
    """COM client configuration."""
    prog_id: str
    visible: bool = False
    display_alerts: bool = False
    enable_events: bool = False


class COMClient(Generic[T]):
    """Generic typed COM client."""
    
    def __init__(self, config: COMConfig) -> None:
        self._config = config
        self._app: T | None = None
        self._initialized = False
    
    @property
    def app(self) -> T:
        if self._app is None:
            raise RuntimeError("COM client not initialized")
        return self._app
    
    def __enter__(self) -> T:
        pythoncom.CoInitialize()
        self._initialized = True
        
        self._app = win32com.client.Dispatch(self._config.prog_id)
        self._app.Visible = self._config.visible
        
        # Set DisplayAlerts if supported
        if hasattr(self._app, 'DisplayAlerts'):
            self._app.DisplayAlerts = self._config.display_alerts
        
        return self._app
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._app:
            try:
                self._app.Quit()
            except Exception:
                pass
            self._app = None
        
        if self._initialized:
            pythoncom.CoUninitialize()
            self._initialized = False


# Usage:
config = COMConfig(prog_id="Excel.Application", visible=False)
with COMClient[Any](config) as excel:
    wb = excel.Workbooks.Add()
    ws = wb.Sheets(1)
    ws.Cells(1, 1).Value = "Hello COM"
    wb.Close(False)
```

---

## 3. Event Handling

### COM Events with Callbacks

```python
from typing import Callable, Any
import win32com.client


class ExcelEvents:
    """Excel application events handler."""
    
    def __init__(
        self,
        on_workbook_open: Callable[[Any], None] | None = None,
        on_sheet_change: Callable[[Any, Any], None] | None = None
    ) -> None:
        self._on_workbook_open = on_workbook_open
        self._on_sheet_change = on_sheet_change
    
    def OnWorkbookOpen(self, workbook: Any) -> None:
        """Called when a workbook is opened."""
        if self._on_workbook_open:
            self._on_workbook_open(workbook)
    
    def OnSheetChange(self, sheet: Any, target: Any) -> None:
        """Called when a cell value changes."""
        if self._on_sheet_change:
            self._on_sheet_change(sheet, target)


class ExcelWithEvents:
    """Excel client with event handling."""
    
    def __init__(self, events: ExcelEvents) -> None:
        self._events = events
        self._app: Any = None
        self._event_handler: Any = None
    
    def __enter__(self) -> Any:
        pythoncom.CoInitialize()
        self._app = win32com.client.DispatchWithEvents(
            "Excel.Application",
            type(self._events)
        )
        self._app.Visible = True  # Need visible for events
        return self._app
    
    def __exit__(self, *args) -> None:
        if self._app:
            self._app.Quit()
        pythoncom.CoUninitialize()


# Usage:
def on_change(sheet, target):
    print(f"Changed: {sheet.Name} - {target.Address}")

events = ExcelEvents(on_sheet_change=on_change)
with ExcelWithEvents(events) as excel:
    # Excel is now listening for events
    import time
    time.sleep(60)  # Keep alive for testing
```

---

## 4. Threading with COM

### Thread-Safe COM Access

```python
import threading
from queue import Queue
from typing import Callable, Any
import pythoncom


class COMWorker:
    """Thread-safe COM worker for background operations."""
    
    def __init__(self, prog_id: str) -> None:
        self._prog_id = prog_id
        self._queue: Queue = Queue()
        self._thread: threading.Thread | None = None
        self._running = False
    
    def start(self) -> None:
        """Start worker thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop worker thread."""
        self._running = False
        self._queue.put(None)  # Sentinel to wake up thread
        if self._thread:
            self._thread.join(timeout=5)
    
    def submit(self, func: Callable[[Any], Any]) -> None:
        """Submit task to worker."""
        self._queue.put(func)
    
    def _run(self) -> None:
        """Worker thread main loop."""
        pythoncom.CoInitialize()
        try:
            app = win32com.client.Dispatch(self._prog_id)
            
            while self._running:
                task = self._queue.get()
                
                if task is None:
                    break
                
                try:
                    task(app)
                except Exception as e:
                    print(f"Task failed: {e}")
            
            app.Quit()
        finally:
            pythoncom.CoUninitialize()


# Usage:
worker = COMWorker("Excel.Application")
worker.start()

# Submit tasks from any thread
def create_report(excel):
    wb = excel.Workbooks.Add()
    ws = wb.Sheets(1)
    ws.Cells(1, 1).Value = "Report"
    wb.SaveAs("report.xlsx")
    wb.Close()

worker.submit(create_report)
worker.stop()
```

### Marshal COM Objects Between Threads

```python
import pythoncom
import win32com.client
from typing import Any


class COMMarshaller:
    """Marshal COM objects between threads."""
    
    @staticmethod
    def marshal(obj: Any) -> bytes:
        """Marshal COM object to stream."""
        stream = pythoncom.CreateStreamOnHGlobal()
        pythoncom.CoMarshalInterface(
            stream,
            pythoncom.IID_IDispatch,
            obj._oleobj_,
            pythoncom.MSHCTX_INPROC,
            pythoncom.MSHLFLAGS_NORMAL
        )
        stream.Seek(0, 0)
        return stream.Read()
    
    @staticmethod
    def unmarshal(data: bytes) -> Any:
        """Unmarshal COM object from stream."""
        stream = pythoncom.CreateStreamOnHGlobal()
        stream.Write(data)
        stream.Seek(0, 0)
        dispatch = pythoncom.CoUnmarshalInterface(
            stream,
            pythoncom.IID_IDispatch
        )
        return win32com.client.Dispatch(dispatch)
```

---

## 5. Error Handling

### COM Error Types

```python
from dataclasses import dataclass
from typing import Optional
import pythoncom
import pywintypes


@dataclass
class COMErrorInfo:
    """Parsed COM error information."""
    hr: int
    source: str
    description: str
    help_file: Optional[str] = None
    help_context: int = 0
    
    @classmethod
    def from_exception(cls, exc: pywintypes.com_error) -> 'COMErrorInfo':
        """Parse from pywintypes.com_error."""
        hr, desc, exc_info, _ = exc.args
        
        return cls(
            hr=hr,
            source=exc_info[1] if exc_info else "Unknown",
            description=exc_info[2] if exc_info else desc,
            help_file=exc_info[3] if exc_info and len(exc_info) > 3 else None,
            help_context=exc_info[4] if exc_info and len(exc_info) > 4 else 0
        )


class COMError(Exception):
    """Wrapped COM error with context."""
    
    def __init__(
        self,
        message: str,
        info: Optional[COMErrorInfo] = None,
        original: Optional[Exception] = None
    ) -> None:
        super().__init__(message)
        self.info = info
        self.original = original
    
    def __str__(self) -> str:
        msg = super().__str__()
        if self.info:
            msg += f" (HRESULT: 0x{self.info.hr:08X}, Source: {self.info.source})"
        return msg


def handle_com_error(func):
    """Decorator to convert COM errors to COMError."""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pywintypes.com_error as e:
            info = COMErrorInfo.from_exception(e)
            raise COMError(f"COM operation failed: {info.description}", info, e)
    
    return wrapper


# Usage:
@handle_com_error
def open_excel_file(path: str) -> Any:
    with COMClient[Any](COMConfig("Excel.Application")) as excel:
        return excel.Workbooks.Open(path)
```

---

## 6. Common ProgIDs

```python
"""
Common COM ProgIDs for automation:

Office Applications:
├── Excel.Application
├── Word.Application
├── Outlook.Application
├── PowerPoint.Application
└── Access.Application

Windows:
├── Shell.Application
├── Scripting.FileSystemObject
├── WScript.Shell
├── SAPI.SpVoice (Text-to-Speech)
└── ADODB.Connection

Scheduling:
├── Schedule.Service (Task Scheduler)
└── WbemScripting.SWbemLocator (WMI)

Others:
├── InternetExplorer.Application
├── htmlfile (HTML DOM)
└── CDO.Message (Email)
"""

from enum import Enum


class ProgID(str, Enum):
    """Common COM ProgIDs."""
    EXCEL = "Excel.Application"
    WORD = "Word.Application"
    OUTLOOK = "Outlook.Application"
    POWERPOINT = "PowerPoint.Application"
    SHELL = "Shell.Application"
    FSO = "Scripting.FileSystemObject"
    WSCRIPT = "WScript.Shell"
    SCHEDULER = "Schedule.Service"
    WMI = "WbemScripting.SWbemLocator"
```

---

## 7. Best Practices

### Resource Cleanup

```python
from typing import Any
import gc


def force_com_cleanup(obj: Any) -> None:
    """Force release of COM object."""
    if obj is not None:
        try:
            # Release dispatch reference
            if hasattr(obj, '_oleobj_'):
                obj._oleobj_ = None
        except Exception:
            pass
    
    # Force garbage collection
    gc.collect()


class SafeCOMSession:
    """COM session with guaranteed cleanup."""
    
    def __init__(self, prog_id: str) -> None:
        self._prog_id = prog_id
        self._app: Any = None
        self._workbooks: list = []
    
    def __enter__(self) -> 'SafeCOMSession':
        pythoncom.CoInitialize()
        self._app = win32com.client.Dispatch(self._prog_id)
        self._app.Visible = False
        self._app.DisplayAlerts = False
        return self
    
    def __exit__(self, *args) -> None:
        # Close all tracked workbooks
        for wb in self._workbooks:
            try:
                wb.Close(False)
            except Exception:
                pass
        
        # Quit application
        if self._app:
            try:
                self._app.Quit()
            except Exception:
                pass
        
        # Force cleanup
        force_com_cleanup(self._app)
        self._app = None
        
        pythoncom.CoUninitialize()
    
    def open_workbook(self, path: str) -> Any:
        """Open workbook and track for cleanup."""
        wb = self._app.Workbooks.Open(path)
        self._workbooks.append(wb)
        return wb
```

---

> **Remember**: COM automation requires careful attention to threading and resource cleanup. Always use context managers and initialize/uninitialize COM properly in each thread.
