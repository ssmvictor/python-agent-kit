# Selenium Enterprise Patterns

> Web automation for enterprise applications.
> **Typed, maintainable, production-ready.**

---

## 1. Configuration & Setup

### Browser Configuration

```python
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class BrowserConfig:
    """Browser automation configuration."""
    headless: bool = True
    timeout: int = 30
    implicit_wait: int = 10
    window_size: tuple[int, int] = (1920, 1080)
    download_path: Optional[Path] = None
    user_agent: Optional[str] = None
    disable_images: bool = False
    proxy: Optional[str] = None
    extra_args: List[str] = field(default_factory=list)


def create_chrome_options(config: BrowserConfig) -> "ChromeOptions":
    """Create Chrome options from config."""
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    
    if config.headless:
        options.add_argument("--headless=new")
    
    options.add_argument(f"--window-size={config.window_size[0]},{config.window_size[1]}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    if config.user_agent:
        options.add_argument(f"--user-agent={config.user_agent}")
    
    if config.disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    
    if config.download_path:
        prefs = {
            "download.default_directory": str(config.download_path),
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)
    
    if config.proxy:
        options.add_argument(f"--proxy-server={config.proxy}")
    
    for arg in config.extra_args:
        options.add_argument(arg)
    
    return options
```

---

## 2. Page Object Pattern

### Base Page Class

```python
from abc import ABC
from typing import Optional, List, TypeVar, Type
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

T = TypeVar('T', bound='BasePage')


class BasePage(ABC):
    """Base class for Page Object pattern."""
    
    URL: Optional[str] = None
    
    def __init__(self, driver: WebDriver, timeout: int = 30) -> None:
        self._driver = driver
        self._timeout = timeout
        self._wait = WebDriverWait(driver, timeout)
    
    @property
    def driver(self) -> WebDriver:
        return self._driver
    
    def navigate(self) -> None:
        """Navigate to page URL."""
        if self.URL:
            self._driver.get(self.URL)
    
    def wait_for(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> WebElement:
        """Wait for element to be present."""
        wait = WebDriverWait(self._driver, timeout or self._timeout)
        return wait.until(EC.presence_of_element_located((by, value)))
    
    def wait_for_visible(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> WebElement:
        """Wait for element to be visible."""
        wait = WebDriverWait(self._driver, timeout or self._timeout)
        return wait.until(EC.visibility_of_element_located((by, value)))
    
    def wait_for_clickable(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None
    ) -> WebElement:
        """Wait for element to be clickable."""
        wait = WebDriverWait(self._driver, timeout or self._timeout)
        return wait.until(EC.element_to_be_clickable((by, value)))
    
    def find(self, by: By, value: str) -> WebElement:
        """Find single element."""
        return self._driver.find_element(by, value)
    
    def find_all(self, by: By, value: str) -> List[WebElement]:
        """Find all matching elements."""
        return self._driver.find_elements(by, value)
    
    def click(self, by: By, value: str) -> None:
        """Wait for element and click."""
        self.wait_for_clickable(by, value).click()
    
    def type_text(
        self,
        by: By,
        value: str,
        text: str,
        clear: bool = True
    ) -> None:
        """Type text into input field."""
        element = self.wait_for_visible(by, value)
        if clear:
            element.clear()
        element.send_keys(text)
    
    def get_text(self, by: By, value: str) -> str:
        """Get element text."""
        return self.wait_for_visible(by, value).text
    
    def is_visible(self, by: By, value: str) -> bool:
        """Check if element is visible."""
        try:
            WebDriverWait(self._driver, 2).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except:
            return False
```

### Concrete Page Example

```python
from dataclasses import dataclass
from selenium.webdriver.common.by import By


@dataclass
class Locators:
    """Page locators - centralized for easy maintenance."""
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    DASHBOARD_TITLE = (By.TAG_NAME, "h1")


class LoginPage(BasePage):
    """Login page object."""
    
    URL = "https://app.example.com/login"
    
    def login(self, username: str, password: str) -> "DashboardPage":
        """Perform login action."""
        self.navigate()
        self.type_text(*Locators.USERNAME, username)
        self.type_text(*Locators.PASSWORD, password)
        self.click(*Locators.LOGIN_BUTTON)
        return DashboardPage(self._driver, self._timeout)
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if displayed."""
        if self.is_visible(*Locators.ERROR_MESSAGE):
            return self.get_text(*Locators.ERROR_MESSAGE)
        return None


class DashboardPage(BasePage):
    """Dashboard page object."""
    
    URL = "https://app.example.com/dashboard"
    
    def get_title(self) -> str:
        """Get dashboard title."""
        return self.get_text(*Locators.DASHBOARD_TITLE)
    
    def is_loaded(self) -> bool:
        """Check if dashboard is loaded."""
        return self.is_visible(*Locators.DASHBOARD_TITLE)


# Usage:
def test_login(driver: WebDriver) -> None:
    login_page = LoginPage(driver)
    dashboard = login_page.login("user@example.com", "password123")
    
    assert dashboard.is_loaded()
    assert "Dashboard" in dashboard.get_title()
```

---

## 3. Wait Strategies

### Custom Wait Conditions

```python
from typing import Callable, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


class CustomConditions:
    """Custom wait conditions."""
    
    @staticmethod
    def element_has_attribute(
        by: By,
        value: str,
        attribute: str,
        expected_value: str
    ) -> Callable[[WebDriver], bool]:
        """Wait until element has specific attribute value."""
        def condition(driver: WebDriver) -> bool:
            element = driver.find_element(by, value)
            return element.get_attribute(attribute) == expected_value
        return condition
    
    @staticmethod
    def text_in_element(
        by: By,
        value: str,
        text: str
    ) -> Callable[[WebDriver], bool]:
        """Wait until element contains text."""
        def condition(driver: WebDriver) -> bool:
            element = driver.find_element(by, value)
            return text in element.text
        return condition
    
    @staticmethod
    def ajax_complete() -> Callable[[WebDriver], bool]:
        """Wait until all AJAX requests complete (jQuery)."""
        def condition(driver: WebDriver) -> bool:
            return driver.execute_script(
                "return jQuery.active == 0"
            )
        return condition
    
    @staticmethod
    def page_fully_loaded() -> Callable[[WebDriver], bool]:
        """Wait until page is fully loaded."""
        def condition(driver: WebDriver) -> bool:
            return driver.execute_script(
                "return document.readyState === 'complete'"
            )
        return condition


# Usage:
wait = WebDriverWait(driver, 30)
wait.until(CustomConditions.page_fully_loaded())
wait.until(CustomConditions.text_in_element(By.ID, "status", "Complete"))
```

---

## 4. File Downloads

### Download Handler

```python
from pathlib import Path
from typing import Optional
import time
import os


class DownloadHandler:
    """Handle file downloads in Selenium."""
    
    def __init__(
        self,
        download_dir: Path,
        timeout: int = 60
    ) -> None:
        self._download_dir = download_dir
        self._timeout = timeout
        self._download_dir.mkdir(parents=True, exist_ok=True)
    
    def wait_for_download(
        self,
        expected_filename: Optional[str] = None
    ) -> Optional[Path]:
        """Wait for download to complete."""
        start_time = time.time()
        
        while time.time() - start_time < self._timeout:
            files = list(self._download_dir.glob("*"))
            
            # Check for temp files (download in progress)
            temp_files = [f for f in files if f.suffix in ('.tmp', '.crdownload')]
            
            if not temp_files:
                if expected_filename:
                    target = self._download_dir / expected_filename
                    if target.exists():
                        return target
                else:
                    # Return newest file
                    completed = [f for f in files if f.suffix not in ('.tmp', '.crdownload')]
                    if completed:
                        return max(completed, key=os.path.getctime)
            
            time.sleep(1)
        
        return None
    
    def clear_downloads(self) -> int:
        """Remove all files from download directory."""
        count = 0
        for file in self._download_dir.glob("*"):
            if file.is_file():
                file.unlink()
                count += 1
        return count
```

---

## 5. Authentication Patterns

### Cookie-based Session

```python
import pickle
from pathlib import Path
from typing import Optional


class SessionManager:
    """Manage browser sessions via cookies."""
    
    def __init__(
        self,
        driver: WebDriver,
        cookie_file: Path
    ) -> None:
        self._driver = driver
        self._cookie_file = cookie_file
    
    def save_session(self) -> None:
        """Save cookies to file."""
        cookies = self._driver.get_cookies()
        with open(self._cookie_file, 'wb') as f:
            pickle.dump(cookies, f)
    
    def load_session(self) -> bool:
        """Load cookies from file if exists."""
        if not self._cookie_file.exists():
            return False
        
        try:
            with open(self._cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                self._driver.add_cookie(cookie)
            
            return True
        except Exception:
            return False
    
    def clear_session(self) -> None:
        """Clear session cookies."""
        self._driver.delete_all_cookies()
        if self._cookie_file.exists():
            self._cookie_file.unlink()


# Usage:
session = SessionManager(driver, Path("session.pkl"))

# First login
driver.get("https://app.example.com")
if not session.load_session():
    # Perform manual login
    login_page.login(username, password)
    session.save_session()

driver.refresh()  # Reload with cookies
```

---

## 6. Error Handling

### Typed Exceptions

```python
from dataclasses import dataclass
from typing import Optional


class SeleniumAutomationError(Exception):
    """Base Selenium automation error."""
    pass


@dataclass
class ElementNotFoundError(SeleniumAutomationError):
    """Element not found within timeout."""
    by: str
    value: str
    timeout: int
    page_url: Optional[str] = None
    
    def __str__(self) -> str:
        msg = f"Element not found: {self.by}='{self.value}' (timeout: {self.timeout}s)"
        if self.page_url:
            msg += f" on page: {self.page_url}"
        return msg


@dataclass
class PageLoadError(SeleniumAutomationError):
    """Page failed to load."""
    url: str
    reason: str
    
    def __str__(self) -> str:
        return f"Failed to load {self.url}: {self.reason}"


@dataclass
class AuthenticationError(SeleniumAutomationError):
    """Authentication failed."""
    username: str
    reason: str
    
    def __str__(self) -> str:
        return f"Authentication failed for {self.username}: {self.reason}"
```

### Screenshot on Failure

```python
from functools import wraps
from typing import Callable, TypeVar
from datetime import datetime
from pathlib import Path

T = TypeVar('T')


def screenshot_on_failure(
    screenshot_dir: Path
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to capture screenshot on test failure."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> T:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Capture screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"failure_{func.__name__}_{timestamp}.png"
                filepath = screenshot_dir / filename
                
                if hasattr(self, '_driver'):
                    self._driver.save_screenshot(str(filepath))
                
                raise
        
        return wrapper
    return decorator
```

---

## 7. Iframe & Window Handling

```python
from contextlib import contextmanager
from typing import Generator


class FrameHandler:
    """Handle iframes and windows."""
    
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
    
    @contextmanager
    def switch_to_frame(
        self,
        frame_reference: str | int | WebElement
    ) -> Generator[None, None, None]:
        """Context manager for iframe switching."""
        self._driver.switch_to.frame(frame_reference)
        try:
            yield
        finally:
            self._driver.switch_to.default_content()
    
    @contextmanager
    def switch_to_window(
        self,
        window_handle: str
    ) -> Generator[None, None, None]:
        """Context manager for window switching."""
        original = self._driver.current_window_handle
        self._driver.switch_to.window(window_handle)
        try:
            yield
        finally:
            self._driver.switch_to.window(original)
    
    def switch_to_new_window(self) -> str:
        """Switch to newly opened window, return its handle."""
        current_handles = set(self._driver.window_handles)
        new_handle = (current_handles - {self._driver.current_window_handle}).pop()
        self._driver.switch_to.window(new_handle)
        return new_handle


# Usage:
frame_handler = FrameHandler(driver)

with frame_handler.switch_to_frame("content-frame"):
    # Work inside iframe
    element = driver.find_element(By.ID, "inner-element")
# Automatically switches back to main content
```

---

> **Remember**: Enterprise web apps often have complex flows. Use Page Objects, explicit waits, and proper error handling for maintainable automation.
