#!/usr/bin/env python3
"""
Master Checklist Runner - Antigravity Kit
==========================================

Orchestrates all validation scripts in priority order.
Use this for incremental validation during development.

Usage:
    python .agent/scripts/checklist.py .                                  # Run STRICT profile (default)
    python .agent/scripts/checklist.py . --profile strict --url <URL>      # STRICT + performance checks
    python .agent/scripts/checklist.py . --profile lite                    # Required checks only (fast)

Checks (priority order):
    P0: Security Scan (vulnerabilities, secrets)
    P1: Lint Check (code quality)
    P2: Schema Validation (if applicable)
    P3: Test Runner (unit/integration tests)
    P4: UX Audit (psychology, accessibility)
    P5: Performance (lighthouse + e2e; requires URL)
"""

from __future__ import annotations

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional

# Import console utilities
from _console import console, header, success, error, warning, step, make_table, status


# Define priority-ordered checks
CORE_CHECKS = [
    ("Security Scan", ".agent/skills/vulnerability-scanner/scripts/security_scan.py", True),
    ("Lint Check", ".agent/skills/lint-and-validate/scripts/lint_runner.py", True),
    ("Rich Policy", ".agent/scripts/rich_policy_check.py", True),
    ("Schema Validation", ".agent/skills/database-design/scripts/schema_validator.py", False),
    ("Test Runner", ".agent/skills/testing-patterns/scripts/test_runner.py", False),
    ("UX Audit", ".agent/skills/frontend-design/scripts/ux_audit.py", False),
]

PERFORMANCE_CHECKS = [
    ("Lighthouse Audit", ".agent/skills/performance-profiling/scripts/lighthouse_audit.py", True),
    ("Playwright E2E", ".agent/skills/webapp-testing/scripts/playwright_runner.py", False),
]


def select_core_checks(profile: str) -> List[tuple[str, str, bool]]:
    """Select core checks based on execution profile."""
    if profile == "lite":
        return [check for check in CORE_CHECKS if check[2]]
    return CORE_CHECKS


def check_script_exists(script_path: Path) -> bool:
    """Check if script file exists"""
    return script_path.exists() and script_path.is_file()


def run_script(name: str, script_path: Path, project_path: str, url: Optional[str] = None) -> dict:
    """
    Run a validation script and capture results
    
    Returns:
        dict with keys: name, passed, output, skipped
    """
    if not check_script_exists(script_path):
        warning(f"{name}: Script not found, skipping")
        return {"name": name, "passed": True, "output": "", "skipped": True}
    
    step(f"Running: {name}")
    
    # Build command
    cmd = ["python", str(script_path), project_path]
    if url and ("lighthouse" in script_path.name.lower() or "playwright" in script_path.name.lower()):
        cmd.append(url)
    
    # Run script with status spinner
    try:
        with status(f"Running {name}..."):
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
        
        passed = result.returncode == 0
        
        if passed:
            success(f"{name}: PASSED")
        else:
            error(f"{name}: FAILED")
            if result.stderr:
                console.print(f"  Error: {result.stderr[:200]}")
        
        return {
            "name": name,
            "passed": passed,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": False
        }
    
    except subprocess.TimeoutExpired:
        error(f"{name}: TIMEOUT (>5 minutes)")
        return {"name": name, "passed": False, "output": "", "error": "Timeout", "skipped": False}
    
    except Exception as e:
        error(f"{name}: ERROR - {str(e)}")
        return {"name": name, "passed": False, "output": "", "error": str(e), "skipped": False}


def print_summary(results: List[dict]):
    """Print final summary report with Rich table"""
    header("CHECKLIST SUMMARY")
    
    passed_count = sum(1 for r in results if r["passed"] and not r.get("skipped"))
    failed_count = sum(1 for r in results if not r["passed"] and not r.get("skipped"))
    skipped_count = sum(1 for r in results if r.get("skipped"))
    
    console.print(f"Total Checks: {len(results)}")
    success(f"Passed:  {passed_count}")
    error(f"Failed:  {failed_count}")
    warning(f"Skipped: {skipped_count}")
    console.print()
    
    # Detailed results in a table
    table = make_table("Status", "Check Name")
    for r in results:
        if r.get("skipped"):
            status_text = "[SKIP]"
            style = "yellow"
        elif r["passed"]:
            status_text = "[OK]"
            style = "green"
        else:
            status_text = "[FAIL]"
            style = "red"
        
        if hasattr(table, 'add_row'):
            table.add_row(f"[{style}]{status_text}[/{style}]", r['name'])
    
    console.print(table)
    console.print()
    
    if failed_count > 0:
        error(f"{failed_count} check(s) FAILED - Please fix before proceeding")
        return False
    else:
        success("All checks PASSED")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Run Antigravity Kit validation checklist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python .agent/scripts/checklist.py .                                     # STRICT profile (default)
  python .agent/scripts/checklist.py . --profile strict --url http://localhost:3000
  python .agent/scripts/checklist.py . --profile lite
        """
    )
    parser.add_argument("project", help="Project path to validate")
    parser.add_argument(
        "--profile",
        choices=["lite", "strict", "full"],
        default="strict",
        help="Validation profile: lite (required checks only), strict (default), full (strict + prefer URL for performance)"
    )
    parser.add_argument("--url", help="URL for performance checks (lighthouse, playwright)")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance checks even if URL provided")
    
    args = parser.parse_args()
    
    project_path = Path(args.project).resolve()
    
    if not project_path.exists():
        error(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    header("ANTIGRAVITY KIT - MASTER CHECKLIST")
    console.print(f"Project: {project_path}")
    console.print(f"Profile: {args.profile.upper()}")
    url_info = args.url if args.url else "Not provided (performance checks skipped)"
    console.print(f"URL: {url_info}")

    results = []
    selected_core_checks = select_core_checks(args.profile)

    # Run core checks
    header("CORE CHECKS")
    for name, script_path, required in selected_core_checks:
        script = project_path / script_path
        result = run_script(name, script, str(project_path))
        results.append(result)
        
        # If required check fails, stop
        if required and not result["passed"] and not result.get("skipped"):
            error(f"CRITICAL: {name} failed. Stopping checklist.")
            print_summary(results)
            sys.exit(1)
    
    # Run performance checks based on profile
    if args.profile == "lite":
        if args.url and not args.skip_performance:
            warning("Profile LITE ignores performance checks. Use --profile strict or --profile full.")
    elif args.url and not args.skip_performance:
        header("PERFORMANCE CHECKS")
        for name, script_path, required in PERFORMANCE_CHECKS:
            script = project_path / script_path
            result = run_script(name, script, str(project_path), args.url)
            results.append(result)
    elif args.profile == "full" and not args.url:
        error("Profile FULL requires --url for performance checks. Use --profile strict to skip them.")
        sys.exit(1)
    
    # Print summary
    all_passed = print_summary(results)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
