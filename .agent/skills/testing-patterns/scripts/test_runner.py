#!/usr/bin/env python3
"""
Test Runner - Unified test execution and coverage reporting
Runs tests and generates coverage report based on project type.

Usage:
    python test_runner.py <project_path> [--coverage]

Supports:
    - Node.js: npm test, jest, vitest
    - Python: pytest, unittest
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from _console import console, success, error, warning, step

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except:
    pass


def detect_test_framework(project_path: Path) -> dict:
    """Detect test framework and commands."""
    result = {
        "type": "unknown",
        "framework": None,
        "cmd": None,
        "coverage_cmd": None
    }
    
    # Node.js project
    package_json = project_path / "package.json"
    if package_json.exists():
        result["type"] = "node"
        try:
            pkg = json.loads(package_json.read_text(encoding='utf-8'))
            scripts = pkg.get("scripts", {})
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            # Check for test script
            if "test" in scripts:
                result["framework"] = "npm test"
                result["cmd"] = ["npm", "test"]
                
                # Try to detect specific framework for coverage
                if "vitest" in deps:
                    result["framework"] = "vitest"
                    result["coverage_cmd"] = ["npx", "vitest", "run", "--coverage"]
                elif "jest" in deps:
                    result["framework"] = "jest"
                    result["coverage_cmd"] = ["npx", "jest", "--coverage"]
            elif "vitest" in deps:
                result["framework"] = "vitest"
                result["cmd"] = ["npx", "vitest", "run"]
                result["coverage_cmd"] = ["npx", "vitest", "run", "--coverage"]
            elif "jest" in deps:
                result["framework"] = "jest"
                result["cmd"] = ["npx", "jest"]
                result["coverage_cmd"] = ["npx", "jest", "--coverage"]
                
        except:
            pass
    
    # Python project
    if (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
        result["type"] = "python"
        result["framework"] = "pytest"
        result["cmd"] = ["python", "-m", "pytest", "-v"]
        result["coverage_cmd"] = ["python", "-m", "pytest", "--cov", "--cov-report=term-missing"]
    
    return result


def run_tests(cmd: list, cwd: Path) -> dict:
    """Run tests and return results."""
    result = {
        "passed": False,
        "output": "",
        "error": "",
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0
    }
    
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300  # 5 min timeout for tests
        )
        
        result["output"] = proc.stdout[:3000] if proc.stdout else ""
        result["error"] = proc.stderr[:500] if proc.stderr else ""
        result["passed"] = proc.returncode == 0
        
        # Try to parse test counts from output
        output = proc.stdout or ""
        
        # Jest/Vitest pattern: "Tests: X passed, Y failed, Z total"
        if "passed" in output.lower() and "failed" in output.lower():
            import re
            match = re.search(r'(\d+)\s+passed', output, re.IGNORECASE)
            if match:
                result["tests_passed"] = int(match.group(1))
            match = re.search(r'(\d+)\s+failed', output, re.IGNORECASE)
            if match:
                result["tests_failed"] = int(match.group(1))
            result["tests_run"] = result["tests_passed"] + result["tests_failed"]
        
        # Pytest pattern: "X passed, Y failed"
        if "pytest" in str(cmd):
            import re
            match = re.search(r'(\d+)\s+passed', output)
            if match:
                result["tests_passed"] = int(match.group(1))
            match = re.search(r'(\d+)\s+failed', output)
            if match:
                result["tests_failed"] = int(match.group(1))
            result["tests_run"] = result["tests_passed"] + result["tests_failed"]
        
    except FileNotFoundError:
        result["error"] = f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout after 300s"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    with_coverage = "--coverage" in sys.argv
    
    from _console import header
    header("TEST RUNNER - Unified Test Execution")
    console.print(f"Project: {project_path}")
    console.print(f"Coverage: {'enabled' if with_coverage else 'disabled'}")
    console.print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detect test framework
    test_info = detect_test_framework(project_path)
    console.print(f"Type: {test_info['type']}")
    step(f"Framework: {test_info['framework']}")
    console.print("-"*60)
    
    if not test_info["cmd"]:
        warning("No test framework found for this project.")
        output = {
            "script": "test_runner",
            "project": str(project_path),
            "type": test_info['type'],
            "framework": None,
            "passed": True,
            "message": "No tests configured"
        }
        console.print(json.dumps(output, indent=2))
        sys.exit(0)
    
    # Choose command
    cmd = test_info["coverage_cmd"] if with_coverage and test_info["coverage_cmd"] else test_info["cmd"]
    
    step(f"Running: {' '.join(cmd)}")
    console.print("-"*60)
    
    # Run tests
    result = run_tests(cmd, project_path)
    
    # Print output (truncated)
    if result["output"]:
        lines = result["output"].split("\n")
        for line in lines[:30]:
            console.print(line)
        if len(lines) > 30:
            console.print(f"... ({len(lines) - 30} more lines)")
    
    # Summary
    console.print("\n" + "="*60)
    console.print("SUMMARY")
    console.print("="*60)
    
    if result["passed"]:
        success("All tests passed")
    else:
        error("Some tests failed")
        if result["error"]:
            console.print(f"Error: {result['error'][:200]}")
    
    if result["tests_run"] > 0:
        console.print(f"Tests: {result['tests_run']} total, {result['tests_passed']} passed, {result['tests_failed']} failed")
    
    output = {
        "script": "test_runner",
        "project": str(project_path),
        "type": test_info['type'],
        "framework": test_info['framework'],
        "tests_run": result['tests_run'],
        "tests_passed": result['tests_passed'],
        "tests_failed": result['tests_failed'],
        "passed": result['passed']
    }
    
    console.print("\n" + json.dumps(output, indent=2))
    
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
