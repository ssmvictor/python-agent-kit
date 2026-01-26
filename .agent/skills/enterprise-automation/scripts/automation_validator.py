#!/usr/bin/env python3
"""
Automation Validator Script

Validates Windows automation environment and dependencies.
Usage: python automation_validator.py [--check-all] [--check-com] [--check-selenium]

Examples:
    python automation_validator.py --check-all
    python automation_validator.py --check-com
    python automation_validator.py --check-selenium
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, List, Optional


class CheckStatus(str, Enum):
    """Check result status."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class CheckResult:
    """Result of a single check."""
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report."""
    checked_at: datetime
    system_info: dict
    checks: List[CheckResult] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """All checks passed (ignoring warnings)."""
        return all(c.status in (CheckStatus.PASS, CheckStatus.WARN, CheckStatus.SKIP) 
                   for c in self.checks)
    
    @property
    def summary(self) -> dict:
        """Summary counts."""
        return {
            "passed": sum(1 for c in self.checks if c.status == CheckStatus.PASS),
            "failed": sum(1 for c in self.checks if c.status == CheckStatus.FAIL),
            "warnings": sum(1 for c in self.checks if c.status == CheckStatus.WARN),
            "skipped": sum(1 for c in self.checks if c.status == CheckStatus.SKIP),
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "checked_at": self.checked_at.isoformat(),
            "system_info": self.system_info,
            "passed": self.passed,
            "summary": self.summary,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


class AutomationValidator:
    """Validate automation environment."""
    
    def __init__(self) -> None:
        self._checks: List[tuple[str, Callable[[], CheckResult]]] = []
    
    def add_check(
        self, 
        name: str, 
        check_fn: Callable[[], CheckResult]
    ) -> "AutomationValidator":
        """Add a check."""
        self._checks.append((name, check_fn))
        return self
    
    def _get_system_info(self) -> dict:
        """Get system information."""
        import platform
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
        }
    
    def run(self) -> ValidationReport:
        """Run all checks."""
        report = ValidationReport(
            checked_at=datetime.now(),
            system_info=self._get_system_info(),
        )
        
        for name, check_fn in self._checks:
            try:
                result = check_fn()
            except Exception as e:
                result = CheckResult(
                    name=name,
                    status=CheckStatus.FAIL,
                    message=f"Check error: {e}",
                )
            report.checks.append(result)
        
        return report


# ============================================================================
# Check Functions
# ============================================================================

def check_python_version() -> CheckResult:
    """Check Python version is 3.10+."""
    import sys
    version = sys.version_info
    
    if version >= (3, 10):
        return CheckResult(
            name="python_version",
            status=CheckStatus.PASS,
            message=f"Python {version.major}.{version.minor}.{version.micro}",
        )
    else:
        return CheckResult(
            name="python_version",
            status=CheckStatus.WARN,
            message=f"Python {version.major}.{version.minor} - recommend 3.10+",
        )


def check_windows_platform() -> CheckResult:
    """Check running on Windows."""
    import platform
    
    if platform.system() == "Windows":
        return CheckResult(
            name="windows_platform",
            status=CheckStatus.PASS,
            message=f"Windows {platform.release()}",
        )
    else:
        return CheckResult(
            name="windows_platform",
            status=CheckStatus.FAIL,
            message=f"Not Windows: {platform.system()}",
        )


def check_pywin32() -> CheckResult:
    """Check pywin32 is installed."""
    try:
        import win32com.client
        import pythoncom
        return CheckResult(
            name="pywin32",
            status=CheckStatus.PASS,
            message="pywin32 installed and working",
        )
    except ImportError as e:
        return CheckResult(
            name="pywin32",
            status=CheckStatus.FAIL,
            message="pywin32 not installed",
            details="pip install pywin32 && python -m pywin32_postinstall -install",
        )


def check_excel_com() -> CheckResult:
    """Check Excel COM automation."""
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            version = excel.Version
            excel.Quit()
            return CheckResult(
                name="excel_com",
                status=CheckStatus.PASS,
                message=f"Excel {version} available",
            )
        finally:
            pythoncom.CoUninitialize()
    except Exception as e:
        return CheckResult(
            name="excel_com",
            status=CheckStatus.FAIL,
            message=f"Excel not available: {e}",
        )


def check_word_com() -> CheckResult:
    """Check Word COM automation."""
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        try:
            word = win32com.client.Dispatch("Word.Application")
            version = word.Version
            word.Quit()
            return CheckResult(
                name="word_com",
                status=CheckStatus.PASS,
                message=f"Word {version} available",
            )
        finally:
            pythoncom.CoUninitialize()
    except Exception as e:
        return CheckResult(
            name="word_com",
            status=CheckStatus.WARN,
            message=f"Word not available: {e}",
        )


def check_outlook_com() -> CheckResult:
    """Check Outlook COM automation."""
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            version = outlook.Version
            return CheckResult(
                name="outlook_com",
                status=CheckStatus.PASS,
                message=f"Outlook {version} available",
            )
        finally:
            pythoncom.CoUninitialize()
    except Exception as e:
        return CheckResult(
            name="outlook_com",
            status=CheckStatus.WARN,
            message=f"Outlook not available: {e}",
        )


def check_selenium() -> CheckResult:
    """Check Selenium is installed."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        return CheckResult(
            name="selenium",
            status=CheckStatus.PASS,
            message="Selenium installed",
        )
    except ImportError:
        return CheckResult(
            name="selenium",
            status=CheckStatus.WARN,
            message="Selenium not installed",
            details="pip install selenium",
        )


def check_chrome_driver() -> CheckResult:
    """Check Chrome WebDriver."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        version = driver.capabilities.get('browserVersion', 'unknown')
        driver.quit()
        
        return CheckResult(
            name="chrome_driver",
            status=CheckStatus.PASS,
            message=f"Chrome {version} with WebDriver",
        )
    except Exception as e:
        return CheckResult(
            name="chrome_driver",
            status=CheckStatus.WARN,
            message=f"Chrome WebDriver not available: {e}",
            details="Install Chrome and chromedriver",
        )


def check_playwright() -> CheckResult:
    """Check Playwright is installed."""
    try:
        from playwright.sync_api import sync_playwright
        return CheckResult(
            name="playwright",
            status=CheckStatus.PASS,
            message="Playwright installed",
        )
    except ImportError:
        return CheckResult(
            name="playwright",
            status=CheckStatus.SKIP,
            message="Playwright not installed (optional)",
            details="pip install playwright && playwright install",
        )


def check_keyring() -> CheckResult:
    """Check keyring for credential management."""
    try:
        import keyring
        return CheckResult(
            name="keyring",
            status=CheckStatus.PASS,
            message="Keyring available for credential management",
        )
    except ImportError:
        return CheckResult(
            name="keyring",
            status=CheckStatus.WARN,
            message="Keyring not installed",
            details="pip install keyring",
        )


# ============================================================================
# Main
# ============================================================================

def print_report(report: ValidationReport, json_output: bool = False) -> None:
    """Print validation report."""
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return
    
    print("\n" + "=" * 60)
    print("🔧 AUTOMATION ENVIRONMENT VALIDATION")
    print("=" * 60)
    print(f"Platform: {report.system_info['platform']} {report.system_info['platform_version']}")
    print(f"Python: {report.system_info['python_version']}")
    print(f"Checked: {report.checked_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    status_icons = {
        CheckStatus.PASS: "✅",
        CheckStatus.FAIL: "❌",
        CheckStatus.WARN: "⚠️",
        CheckStatus.SKIP: "⏭️",
    }
    
    for check in report.checks:
        icon = status_icons[check.status]
        print(f"{icon} [{check.status.value.upper():4}] {check.name}: {check.message}")
        if check.details:
            print(f"       └─ {check.details}")
    
    print("-" * 60)
    summary = report.summary
    status = "✅ READY" if report.passed else "❌ NOT READY"
    print(f"Summary: {summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['warnings']} warnings, {summary['skipped']} skipped")
    print(f"Status: {status}")
    print("=" * 60 + "\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automation Environment Validator",
    )
    parser.add_argument(
        "--check-all", "-a",
        action="store_true",
        help="Run all checks"
    )
    parser.add_argument(
        "--check-com", "-c",
        action="store_true",
        help="Check COM automation (Office apps)"
    )
    parser.add_argument(
        "--check-selenium", "-s",
        action="store_true",
        help="Check Selenium/browser automation"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Default to all if nothing specified
    if not any([args.check_all, args.check_com, args.check_selenium]):
        args.check_all = True
    
    # Build validator
    validator = AutomationValidator()
    
    # Always check basics
    validator.add_check("python_version", check_python_version)
    validator.add_check("windows_platform", check_windows_platform)
    
    if args.check_all or args.check_com:
        validator.add_check("pywin32", check_pywin32)
        validator.add_check("excel_com", check_excel_com)
        validator.add_check("word_com", check_word_com)
        validator.add_check("outlook_com", check_outlook_com)
        validator.add_check("keyring", check_keyring)
    
    if args.check_all or args.check_selenium:
        validator.add_check("selenium", check_selenium)
        validator.add_check("chrome_driver", check_chrome_driver)
        validator.add_check("playwright", check_playwright)
    
    # Run and report
    report = validator.run()
    print_report(report, args.json)
    
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
