#!/usr/bin/env python3
"""
Lint Runner - Unified linting and type checking
Runs appropriate linters based on project type.

Usage:
    python lint_runner.py <project_path>

Supports:
    - Node.js: npm run lint, npx tsc --noEmit
    - Python: ruff check, mypy
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


def detect_project_type(project_path: Path) -> dict:
    """Detect project type and available linters."""
    result = {
        "type": "unknown",
        "linters": []
    }
    
    # Node.js project
    package_json = project_path / "package.json"
    if package_json.exists():
        result["type"] = "node"
        try:
            pkg = json.loads(package_json.read_text(encoding='utf-8'))
            scripts = pkg.get("scripts", {})
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            # Check for lint script
            if "lint" in scripts:
                result["linters"].append({"name": "npm lint", "cmd": ["npm", "run", "lint"]})
            elif "eslint" in deps:
                result["linters"].append({"name": "eslint", "cmd": ["npx", "eslint", "."]})
            
            # Check for TypeScript
            if "typescript" in deps or (project_path / "tsconfig.json").exists():
                result["linters"].append({"name": "tsc", "cmd": ["npx", "tsc", "--noEmit"]})
                
        except:
            pass
    
    # Python project
    if (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
        result["type"] = "python"
        
        # Check for ruff
        result["linters"].append({"name": "ruff", "cmd": ["ruff", "check", "."]})
        
        # Check for mypy
        if (project_path / "mypy.ini").exists() or (project_path / "pyproject.toml").exists():
            result["linters"].append({"name": "mypy", "cmd": ["mypy", "."]})
    
    return result


def run_linter(linter: dict, cwd: Path) -> dict:
    """Run a single linter and return results."""
    result = {
        "name": linter["name"],
        "passed": False,
        "output": "",
        "error": ""
    }
    
    try:
        proc = subprocess.run(
            linter["cmd"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120
        )
        
        result["output"] = proc.stdout[:2000] if proc.stdout else ""
        result["error"] = proc.stderr[:500] if proc.stderr else ""
        result["passed"] = proc.returncode == 0
        
    except FileNotFoundError:
        result["error"] = f"Command not found: {linter['cmd'][0]}"
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout after 120s"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    project_path = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    
    from _console import header
    header("LINT RUNNER - Unified Linting")
    console.print(f"Project: {project_path}")
    console.print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Detect project type
    project_info = detect_project_type(project_path)
    console.print(f"Type: {project_info['type']}")
    step(f"Linters: {len(project_info['linters'])}")
    console.print("-"*60)
    
    if not project_info["linters"]:
        warning("No linters found for this project type.")
        output = {
            "script": "lint_runner",
            "project": str(project_path),
            "type": project_info['type'],
            "checks": [],
            "passed": True,
            "message": "No linters configured"
        }
        console.print(json.dumps(output, indent=2))
        sys.exit(0)
    
    # Run each linter
    results = []
    all_passed = True
    
    for linter in project_info["linters"]:
        step(f"Running: {linter['name']}...")
        result = run_linter(linter, project_path)
        results.append(result)
        
        if result["passed"]:
            success(f"  {linter['name']}")
        else:
            error(f"  {linter['name']}")
            if result["error"]:
                console.print(f"  Error: {result['error'][:200]}")
            all_passed = False
    
    # Summary
    console.print("\n" + "="*60)
    console.print("SUMMARY")
    console.print("="*60)
    
    for r in results:
        if r["passed"]:
            success(f"{r['name']}")
        else:
            error(f"{r['name']}")
    
    output = {
        "script": "lint_runner",
        "project": str(project_path),
        "type": project_info['type'],
        "checks": results,
        "passed": all_passed
    }
    
    console.print("\n" + json.dumps(output, indent=2))
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
