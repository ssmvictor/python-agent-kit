#!/usr/bin/env python3
"""
Database Connection Tester Script

Test database connectivity and diagnose connection issues.
Usage: python connection_tester.py --driver <driver> --host <host> --database <db>

Examples:
    python connection_tester.py --driver sqlserver --host localhost --database testdb
    python connection_tester.py --driver oracle --host oracle.company.com --database PROD
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from _console import console, success, error, warning, step, make_table, print_table

import argparse
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DatabaseDriver(str, Enum):
    """Supported database drivers."""
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class TestStatus(str, Enum):
    """Test result status."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class TestResult:
    """Single test result."""
    name: str
    status: TestStatus
    message: str
    duration_ms: float = 0.0
    details: Optional[str] = None


@dataclass
class ConnectionTestReport:
    """Complete connection test report."""
    driver: str
    host: str
    database: str
    tested_at: datetime
    tests: List[TestResult] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """All tests passed."""
        return all(t.status != TestStatus.FAIL for t in self.tests)
    
    @property
    def summary(self) -> Dict[str, int]:
        """Test summary."""
        return {
            "passed": sum(1 for t in self.tests if t.status == TestStatus.PASS),
            "failed": sum(1 for t in self.tests if t.status == TestStatus.FAIL),
            "skipped": sum(1 for t in self.tests if t.status == TestStatus.SKIP),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "driver": self.driver,
            "host": self.host,
            "database": self.database,
            "tested_at": self.tested_at.isoformat(),
            "passed": self.passed,
            "summary": self.summary,
            "tests": [
                {
                    "name": t.name,
                    "status": t.status.value,
                    "message": t.message,
                    "duration_ms": round(t.duration_ms, 2),
                    "details": t.details,
                }
                for t in self.tests
            ],
        }


class ConnectionTester:
    """Test database connectivity."""
    
    def __init__(
        self,
        driver: DatabaseDriver,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str
    ) -> None:
        self._driver = driver
        self._host = host
        self._port = port
        self._database = database
        self._username = username
        self._password = password
        self._tests: List[TestResult] = []
    
    def _run_test(self, name: str, test_fn) -> TestResult:
        """Run a single test and capture result."""
        start = time.time()
        try:
            message = test_fn()
            duration = (time.time() - start) * 1000
            return TestResult(
                name=name,
                status=TestStatus.PASS,
                message=message or "OK",
                duration_ms=duration
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return TestResult(
                name=name,
                status=TestStatus.FAIL,
                message=str(e),
                duration_ms=duration
            )
    
    def test_driver_available(self) -> TestResult:
        """Test if database driver is installed."""
        def check():
            if self._driver == DatabaseDriver.SQLSERVER:
                import pyodbc
                return f"pyodbc {pyodbc.version}"
            elif self._driver == DatabaseDriver.ORACLE:
                import oracledb
                return f"oracledb {oracledb.__version__}"
            elif self._driver == DatabaseDriver.POSTGRESQL:
                import psycopg2
                return f"psycopg2 {psycopg2.__version__}"
            elif self._driver == DatabaseDriver.MYSQL:
                import mysql.connector
                return f"mysql-connector {mysql.connector.__version__}"
        
        return self._run_test("driver_available", check)
    
    def test_host_reachable(self) -> TestResult:
        """Test if host is reachable."""
        import socket
        
        def check():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                result = sock.connect_ex((self._host, self._port))
                if result == 0:
                    return f"Port {self._port} is open"
                else:
                    raise ConnectionError(f"Port {self._port} is closed (code: {result})")
            finally:
                sock.close()
        
        return self._run_test("host_reachable", check)
    
    def test_connection(self) -> TestResult:
        """Test database connection."""
        def check():
            if self._driver == DatabaseDriver.SQLSERVER:
                import pyodbc
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self._host},{self._port};"
                    f"DATABASE={self._database};"
                    f"UID={self._username};"
                    f"PWD={self._password};"
                    f"Connection Timeout=10;"
                )
                conn = pyodbc.connect(conn_str)
                conn.close()
                return "Connection successful"
            
            elif self._driver == DatabaseDriver.ORACLE:
                import oracledb
                dsn = f"{self._host}:{self._port}/{self._database}"
                conn = oracledb.connect(
                    user=self._username,
                    password=self._password,
                    dsn=dsn
                )
                conn.close()
                return "Connection successful"
            
            elif self._driver == DatabaseDriver.POSTGRESQL:
                import psycopg2
                conn = psycopg2.connect(
                    host=self._host,
                    port=self._port,
                    database=self._database,
                    user=self._username,
                    password=self._password,
                    connect_timeout=10
                )
                conn.close()
                return "Connection successful"
            
            elif self._driver == DatabaseDriver.MYSQL:
                import mysql.connector
                conn = mysql.connector.connect(
                    host=self._host,
                    port=self._port,
                    database=self._database,
                    user=self._username,
                    password=self._password,
                    connection_timeout=10
                )
                conn.close()
                return "Connection successful"
        
        return self._run_test("connection", check)
    
    def test_query(self) -> TestResult:
        """Test simple query execution."""
        def check():
            if self._driver == DatabaseDriver.SQLSERVER:
                import pyodbc
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self._host},{self._port};"
                    f"DATABASE={self._database};"
                    f"UID={self._username};"
                    f"PWD={self._password};"
                )
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 AS test")
                row = cursor.fetchone()
                conn.close()
                return f"Query returned: {row[0]}"
            
            elif self._driver == DatabaseDriver.ORACLE:
                import oracledb
                dsn = f"{self._host}:{self._port}/{self._database}"
                conn = oracledb.connect(
                    user=self._username,
                    password=self._password,
                    dsn=dsn
                )
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM DUAL")
                row = cursor.fetchone()
                conn.close()
                return f"Query returned: {row[0]}"
            
            elif self._driver == DatabaseDriver.POSTGRESQL:
                import psycopg2
                conn = psycopg2.connect(
                    host=self._host,
                    port=self._port,
                    database=self._database,
                    user=self._username,
                    password=self._password
                )
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                conn.close()
                return f"Query returned: {row[0]}"
            
            elif self._driver == DatabaseDriver.MYSQL:
                import mysql.connector
                conn = mysql.connector.connect(
                    host=self._host,
                    port=self._port,
                    database=self._database,
                    user=self._username,
                    password=self._password
                )
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                conn.close()
                return f"Query returned: {row[0]}"
        
        return self._run_test("query_execution", check)
    
    def run_all(self) -> ConnectionTestReport:
        """Run all tests."""
        self._tests = [
            self.test_driver_available(),
            self.test_host_reachable(),
            self.test_connection(),
            self.test_query(),
        ]
        
        return ConnectionTestReport(
            driver=self._driver.value,
            host=self._host,
            database=self._database,
            tested_at=datetime.now(),
            tests=self._tests
        )


def print_report(report: ConnectionTestReport, json_output: bool = False) -> None:
    """Print test report."""
    if json_output:
        print(json.dumps(report.to_dict(), indent=2))
        return
    
    from _console import header
    header("DATABASE CONNECTION TEST")
    
    console.print(f"Driver: {report.driver}")
    console.print(f"Host: {report.host}")
    console.print(f"Database: {report.database}")
    console.print(f"Tested: {report.tested_at.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print("-" * 60)
    
    # Create Rich table
    table = make_table("Status", "Duration", "Test", "Message")
    
    for test in report.tests:
        if test.status == TestStatus.PASS:
            status_text = "[green]PASS[/green]"
        elif test.status == TestStatus.FAIL:
            status_text = "[red]FAIL[/red]"
        else:
            status_text = "[yellow]SKIP[/yellow]"
        
        table.add_row(
            status_text,
            f"{test.duration_ms:.1f}ms",
            test.name,
            test.message
        )
    
    print_table(table)
    
    console.print("-" * 60)
    summary = report.summary
    if report.passed:
        success(f"ALL TESTS PASSED ({summary['passed']} passed, {summary['failed']} failed)")
    else:
        error(f"SOME TESTS FAILED ({summary['passed']} passed, {summary['failed']} failed)")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database Connection Tester",
    )
    parser.add_argument(
        "--driver", "-d",
        type=str,
        choices=["sqlserver", "oracle", "postgresql", "mysql"],
        required=True,
        help="Database driver"
    )
    parser.add_argument("--host", "-H", required=True, help="Database host")
    parser.add_argument("--port", "-p", type=int, help="Database port")
    parser.add_argument("--database", "-D", required=True, help="Database name")
    parser.add_argument("--username", "-u", help="Username (or use DB_USER env)")
    parser.add_argument("--password", "-P", help="Password (or use DB_PASSWORD env)")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Resolve defaults
    driver = DatabaseDriver(args.driver)
    
    port_defaults = {
        DatabaseDriver.SQLSERVER: 1433,
        DatabaseDriver.ORACLE: 1521,
        DatabaseDriver.POSTGRESQL: 5432,
        DatabaseDriver.MYSQL: 3306,
    }
    port = args.port or port_defaults.get(driver, 0)
    
    username = args.username or os.environ.get("DB_USER", "")
    password = args.password or os.environ.get("DB_PASSWORD", "")
    
    if not username or not password:
        print("ERROR: Username and password required (use args or DB_USER/DB_PASSWORD env)")
        return 1
    
    # Run tests
    tester = ConnectionTester(
        driver=driver,
        host=args.host,
        port=port,
        database=args.database,
        username=username,
        password=password
    )
    
    report = tester.run_all()
    print_report(report, args.json)
    
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
