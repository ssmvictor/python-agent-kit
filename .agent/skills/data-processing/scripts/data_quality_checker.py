#!/usr/bin/env python3
"""
Data Quality Checker Script

Validates data files against quality rules.
Usage: python data_quality_checker.py <path> [--format csv|parquet|json]

Examples:
    python data_quality_checker.py data.csv
    python data_quality_checker.py data.parquet --format parquet
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Protocol

# Type aliases
CheckFunction = Callable[["DataFrameProtocol"], bool]


class DataFrameProtocol(Protocol):
    """Protocol for DataFrame-like objects."""
    
    def __len__(self) -> int: ...
    @property
    def columns(self) -> list[str]: ...
    def isnull(self) -> "DataFrameProtocol": ...
    def sum(self) -> dict[str, int]: ...
    def nunique(self) -> dict[str, int]: ...


class Severity(str, Enum):
    """Check severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CheckResult:
    """Result of a single quality check."""
    name: str
    passed: bool
    severity: Severity
    message: str
    details: dict | None = None


@dataclass
class QualityReport:
    """Complete quality check report."""
    file_path: str
    checked_at: datetime
    total_rows: int
    total_columns: int
    checks: list[CheckResult] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """Report passes if no ERROR or CRITICAL failures."""
        return not any(
            not c.passed and c.severity in (Severity.ERROR, Severity.CRITICAL)
            for c in self.checks
        )
    
    @property
    def summary(self) -> dict[str, int]:
        """Count of checks by status."""
        return {
            "passed": sum(1 for c in self.checks if c.passed),
            "warnings": sum(
                1 for c in self.checks 
                if not c.passed and c.severity == Severity.WARNING
            ),
            "errors": sum(
                1 for c in self.checks 
                if not c.passed and c.severity in (Severity.ERROR, Severity.CRITICAL)
            ),
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "checked_at": self.checked_at.isoformat(),
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "passed": self.passed,
            "summary": self.summary,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "severity": c.severity.value,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


@dataclass
class QualityCheck:
    """Definition of a quality check."""
    name: str
    description: str
    severity: Severity
    check_fn: CheckFunction
    
    def run(self, df: DataFrameProtocol) -> CheckResult:
        """Execute check and return result."""
        try:
            passed = self.check_fn(df)
            return CheckResult(
                name=self.name,
                passed=passed,
                severity=self.severity,
                message=self.description if passed else f"FAILED: {self.description}",
            )
        except Exception as e:
            return CheckResult(
                name=self.name,
                passed=False,
                severity=Severity.ERROR,
                message=f"Check error: {e}",
            )


class DataQualityChecker:
    """Main quality checker class."""
    
    def __init__(self) -> None:
        self._checks: list[QualityCheck] = []
        self._register_default_checks()
    
    def _register_default_checks(self) -> None:
        """Register default quality checks."""
        
        # Check: No completely empty rows
        self.add_check(QualityCheck(
            name="no_empty_rows",
            description="Dataset should have no completely empty rows",
            severity=Severity.WARNING,
            check_fn=lambda df: len(df) > 0,
        ))
        
        # Check: No duplicate columns
        self.add_check(QualityCheck(
            name="no_duplicate_columns",
            description="Column names should be unique",
            severity=Severity.ERROR,
            check_fn=lambda df: len(df.columns) == len(set(df.columns)),
        ))
    
    def add_check(self, check: QualityCheck) -> "DataQualityChecker":
        """Add a quality check."""
        self._checks.append(check)
        return self
    
    def add_null_check(
        self, 
        column: str, 
        max_null_pct: float = 0.0,
        severity: Severity = Severity.ERROR
    ) -> "DataQualityChecker":
        """Add null value check for specific column."""
        self.add_check(QualityCheck(
            name=f"null_check_{column}",
            description=f"Column '{column}' should have <= {max_null_pct*100}% nulls",
            severity=severity,
            check_fn=lambda df, col=column, pct=max_null_pct: (
                df[col].isnull().sum() / len(df) <= pct if col in df.columns else True
            ),
        ))
        return self
    
    def add_uniqueness_check(
        self,
        column: str,
        severity: Severity = Severity.ERROR
    ) -> "DataQualityChecker":
        """Add uniqueness check for specific column."""
        self.add_check(QualityCheck(
            name=f"unique_check_{column}",
            description=f"Column '{column}' should have unique values",
            severity=severity,
            check_fn=lambda df, col=column: (
                df[col].nunique() == len(df) if col in df.columns else True
            ),
        ))
        return self
    
    def run(self, df: DataFrameProtocol, file_path: str = "") -> QualityReport:
        """Run all checks and return report."""
        report = QualityReport(
            file_path=file_path,
            checked_at=datetime.now(),
            total_rows=len(df),
            total_columns=len(df.columns),
        )
        
        for check in self._checks:
            result = check.run(df)
            report.checks.append(result)
        
        return report


def load_dataframe(path: Path, format: str) -> "DataFrameProtocol":
    """Load DataFrame from file."""
    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas is required. Install with: pip install pandas")
        sys.exit(1)
    
    if format == "csv":
        return pd.read_csv(path)
    elif format == "parquet":
        return pd.read_parquet(path)
    elif format == "json":
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported format: {format}")


def print_report(report: QualityReport, json_output: bool = False) -> None:
    """Print quality report."""
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return
    
    print("\n" + "=" * 60)
    print("📊 DATA QUALITY REPORT")
    print("=" * 60)
    print(f"File: {report.file_path}")
    print(f"Checked: {report.checked_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Rows: {report.total_rows:,} | Columns: {report.total_columns}")
    print("-" * 60)
    
    for check in report.checks:
        icon = "✅" if check.passed else ("⚠️" if check.severity == Severity.WARNING else "❌")
        print(f"{icon} [{check.severity.value.upper():8}] {check.name}: {check.message}")
    
    print("-" * 60)
    summary = report.summary
    status = "✅ PASSED" if report.passed else "❌ FAILED"
    print(f"Summary: {summary['passed']} passed, {summary['warnings']} warnings, {summary['errors']} errors")
    print(f"Status: {status}")
    print("=" * 60 + "\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Data Quality Checker - Validate data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("path", type=Path, help="Path to data file")
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "parquet", "json"],
        default="csv",
        help="Data file format (default: csv)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output report as JSON"
    )
    parser.add_argument(
        "--null-check",
        nargs="+",
        metavar="COLUMN",
        help="Check these columns for null values"
    )
    parser.add_argument(
        "--unique-check",
        nargs="+",
        metavar="COLUMN",
        help="Check these columns for uniqueness"
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.path.exists():
        print(f"ERROR: File not found: {args.path}")
        return 1
    
    # Load data
    try:
        df = load_dataframe(args.path, args.format)
    except Exception as e:
        print(f"ERROR: Failed to load file: {e}")
        return 1
    
    # Create checker with optional column-specific checks
    checker = DataQualityChecker()
    
    if args.null_check:
        for col in args.null_check:
            checker.add_null_check(col)
    
    if args.unique_check:
        for col in args.unique_check:
            checker.add_uniqueness_check(col)
    
    # Run checks
    report = checker.run(df, str(args.path))
    
    # Output report
    print_report(report, args.json)
    
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
