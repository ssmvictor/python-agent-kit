#!/usr/bin/env python3
"""
Full Verification Suite - Antigravity Kit
==========================================

Runs COMPLETE validation including all checks + performance + E2E.
Use this before deployment or major releases.

Usage:
    python .agent/scripts/verify_all.py . --url <URL>

Includes ALL checks:
    - Security scan (OWASP, secrets, dependencies)
    - Lint check
    - Type coverage (optional)
    - Schema validation
    - Test suite (unit + integration)
    - UX audit (psychology, accessibility)
    - Accessibility check
    - Lighthouse (Core Web Vitals)
    - Playwright E2E (optional)
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Import console utilities
from _console import console, header, success, error, warning, step, make_table, status


# Complete verification suite
VERIFICATION_SUITE = [
    # P0: Security (CRITICAL)
    {
        "category": "Security",
        "checks": [
            ("Security Scan", ".agent/skills/vulnerability-scanner/scripts/security_scan.py", True),
        ]
    },
    
    # P1: Code Quality (CRITICAL)
    {
        "category": "Code Quality",
        "checks": [
            ("Lint Check", ".agent/skills/lint-and-validate/scripts/lint_runner.py", True),
            ("Type Coverage", ".agent/skills/lint-and-validate/scripts/type_coverage.py", False),
        ]
    },
    
    # P2: Data Layer
    {
        "category": "Data Layer",
        "checks": [
            ("Schema Validation", ".agent/skills/database-design/scripts/schema_validator.py", False),
        ]
    },
    
    # P3: Testing
    {
        "category": "Testing",
        "checks": [
            ("Test Suite", ".agent/skills/testing-patterns/scripts/test_runner.py", False),
        ]
    },
    
    # P4: UX & Accessibility
    {
        "category": "UX & Accessibility",
        "checks": [
            ("UX Audit", ".agent/skills/frontend-design/scripts/ux_audit.py", False),
            ("Accessibility Check", ".agent/skills/frontend-design/scripts/accessibility_checker.py", False),
        ]
    },
    
    # P5: Performance (requires URL)
    {
        "category": "Performance",
        "requires_url": True,
        "checks": [
            ("Lighthouse Audit", ".agent/skills/performance-profiling/scripts/lighthouse_audit.py", True),
        ]
    },
    
    # P6: E2E Testing (requires URL)
    {
        "category": "E2E Testing",
        "requires_url": True,
        "checks": [
            ("Playwright E2E", ".agent/skills/webapp-testing/scripts/playwright_runner.py", False),
        ]
    },
]


def run_script(name: str, script_path: Path, project_path: str, url: Optional[str] = None) -> dict:
    """Run validation script"""
    if not script_path.exists():
        warning(f"{name}: Script not found, skipping")
        return {"name": name, "passed": True, "skipped": True, "duration": 0}
    
    step(f"Running: {name}")
    start_time = datetime.now()
    
    # Build command
    cmd = ["python", str(script_path), project_path]
    if url and ("lighthouse" in script_path.name.lower() or "playwright" in script_path.name.lower()):
        cmd.append(url)
    
    # Run
    try:
        with status(f"Running {name}..."):
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for slow checks
            )
        
        duration = (datetime.now() - start_time).total_seconds()
        passed = result.returncode == 0
        
        if passed:
            success(f"{name}: PASSED ({duration:.1f}s)")
        else:
            error(f"{name}: FAILED ({duration:.1f}s)")
            if result.stderr:
                console.print(f"  {result.stderr[:300]}")
        
        return {
            "name": name,
            "passed": passed,
            "output": result.stdout,
            "error": result.stderr,
            "skipped": False,
            "duration": duration
        }
    
    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start_time).total_seconds()
        error(f"{name}: TIMEOUT (>{duration:.0f}s)")
        return {"name": name, "passed": False, "skipped": False, "duration": duration, "error": "Timeout"}
    
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        error(f"{name}: ERROR - {str(e)}")
        return {"name": name, "passed": False, "skipped": False, "duration": duration, "error": str(e)}


def print_final_report(results: List[dict], start_time: datetime):
    """Print comprehensive final report with Rich table"""
    total_duration = (datetime.now() - start_time).total_seconds()
    
    header("FULL VERIFICATION REPORT")
    
    # Statistics
    total = len(results)
    passed = sum(1 for r in results if r["passed"] and not r.get("skipped"))
    failed = sum(1 for r in results if not r["passed"] and not r.get("skipped"))
    skipped = sum(1 for r in results if r.get("skipped"))
    
    console.print(f"Total Duration: {total_duration:.1f}s")
    console.print(f"Total Checks: {total}")
    success(f"Passed:  {passed}")
    error(f"Failed:  {failed}")
    warning(f"Skipped: {skipped}")
    console.print()
    
    # Results table with category breakdown
    table = make_table("Category", "Status", "Check", "Duration")
    current_category = None
    
    for r in results:
        category = r.get("category", "Unknown")
        
        if r.get("skipped"):
            status_text = "[SKIP]"
            status_style = "yellow"
        elif r["passed"]:
            status_text = "[OK]"
            status_style = "green"
        else:
            status_text = "[FAIL]"
            status_style = "red"
        
        duration_str = f"{r.get('duration', 0):.1f}s" if not r.get("skipped") else "-"
        
        table.add_row(
            category if category != current_category else "",
            f"[{status_style}]{status_text}[/{status_style}]",
            r['name'],
            duration_str
        )
        current_category = category
    
    console.print(table)
    console.print()
    
    # Failed checks detail
    if failed > 0:
        error("FAILED CHECKS:")
        for r in results:
            if not r["passed"] and not r.get("skipped"):
                console.print(f"[red]- {r['name']}[/red]")
                if r.get("error"):
                    error_preview = r["error"][:200]
                    console.print(f"  Error: {error_preview}")
        console.print()
    
    # Final verdict
    if failed > 0:
        error(f"VERIFICATION FAILED - {failed} check(s) need attention")
        warning("Tip: fix critical (security, lint) issues first")
        return False
    else:
        success("ALL CHECKS PASSED - Ready for deployment")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Run complete Antigravity Kit verification suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python .agent/scripts/verify_all.py . --url http://localhost:3000
  python .agent/scripts/verify_all.py . --url https://staging.example.com --no-e2e
        """
    )
    parser.add_argument("project", help="Project path to validate")
    parser.add_argument("--url", required=True, help="URL for performance & E2E checks")
    parser.add_argument("--no-e2e", action="store_true", help="Skip E2E tests")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop on first failure")
    
    args = parser.parse_args()
    
    project_path = Path(args.project).resolve()
    
    if not project_path.exists():
        error(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    header("ANTIGRAVITY KIT - FULL VERIFICATION SUITE")
    console.print(f"Project: {project_path}")
    console.print(f"URL: {args.url}")
    console.print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = datetime.now()
    results = []
    
    # Run all verification categories
    for suite in VERIFICATION_SUITE:
        category = suite["category"]
        requires_url = suite.get("requires_url", False)
        
        # Skip if requires URL and not provided
        if requires_url and not args.url:
            continue
        
        # Skip E2E if flag set
        if args.no_e2e and category == "E2E Testing":
            continue
        
        header(category.upper())
        
        for name, script_path, required in suite["checks"]:
            script = project_path / script_path
            result = run_script(name, script, str(project_path), args.url)
            result["category"] = category
            results.append(result)
            
            # Stop on critical failure if flag set
            if args.stop_on_fail and required and not result["passed"] and not result.get("skipped"):
                error(f"CRITICAL: {name} failed. Stopping verification.")
                print_final_report(results, start_time)
                sys.exit(1)
    
    # Print final report
    all_passed = print_final_report(results, start_time)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
