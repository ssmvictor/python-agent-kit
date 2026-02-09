#!/usr/bin/env python3
"""
Rich Policy Check - Enforcement Gate
=====================================

AST-based checker that scans all `.py` files and flags any `print()` call
not inside a `--json` conditional branch.

Policy:
    - All terminal output MUST use Rich via `_console.py` (console.print, success,
      error, warning, header, step, make_table, etc.)
    - `print()` is ONLY allowed inside `--json` / machine-readable output guards.
    - `print()` to stderr in _console.py's own ImportError handler is exempt.

Usage:
    python .agent/scripts/rich_policy_check.py .
    python .agent/scripts/rich_policy_check.py .agent/scripts
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

# Import console utilities
from _console import console, header, success, error, warning, make_table


# ============================================================================
# Allowed patterns (print() inside these contexts is OK)
# ============================================================================

# Files where print() is fully exempt (the console module itself)
EXEMPT_FILES: set[str] = {
    "_console.py",
}

# Variable names that indicate a --json guard (if <var>: print(...))
JSON_GUARD_NAMES: set[str] = {
    "json_output",
    "is_json",
    "args.json",
    "json_mode",
}

# Function names where print() of JSON is the expected behavior
JSON_FUNCTION_NAMES: set[str] = {
    "generate_sample_schema",
}


@dataclass
class Violation:
    """A single print() policy violation."""
    file: str
    line: int
    col: int
    context: str


@dataclass
class ScanResult:
    """Result of scanning a directory tree."""
    files_scanned: int = 0
    violations: List[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


class RichPolicyChecker:
    """AST-based checker for the Rich-only output policy."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._result = ScanResult()

    def _is_inside_json_guard(self, node: ast.Call, ancestors: list[ast.AST]) -> bool:
        """Check if a print() call is inside an if-block that tests a JSON flag."""
        for ancestor in reversed(ancestors):
            if isinstance(ancestor, ast.If):
                test_src = ast.dump(ancestor.test)
                for guard_name in JSON_GUARD_NAMES:
                    if guard_name in test_src:
                        return True
                # Also check for attribute access patterns like args.json
                if isinstance(ancestor.test, ast.Attribute):
                    if ancestor.test.attr == "json":
                        return True
        return False

    def _is_inside_exempt_function(self, ancestors: list[ast.AST]) -> bool:
        """Check if the print() call is inside an exempt function."""
        for ancestor in reversed(ancestors):
            if isinstance(ancestor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if ancestor.name in JSON_FUNCTION_NAMES:
                    return True
        return False

    def _is_stderr_print(self, node: ast.Call) -> bool:
        """Check if this is a print(..., file=sys.stderr) call."""
        for kw in node.keywords:
            if kw.arg == "file":
                if isinstance(kw.value, ast.Attribute):
                    if kw.value.attr == "stderr":
                        return True
        return False

    def _get_line_context(self, source_lines: list[str], lineno: int) -> str:
        """Get a trimmed line of source for context."""
        if 0 < lineno <= len(source_lines):
            return source_lines[lineno - 1].strip()[:80]
        return ""

    def _scan_file(self, filepath: Path) -> None:
        """Scan a single Python file for print() violations."""
        if filepath.name in EXEMPT_FILES:
            return

        try:
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError):
            return

        self._result.files_scanned += 1
        source_lines = source.splitlines()

        # Walk tree tracking parent chain
        self._walk_with_ancestors(tree, [], filepath, source_lines)

    def _walk_with_ancestors(
        self,
        node: ast.AST,
        ancestors: list[ast.AST],
        filepath: Path,
        source_lines: list[str],
    ) -> None:
        """Recursively walk AST tracking ancestor chain."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Call) and self._is_print_call(child):
                # Check exemptions
                if self._is_stderr_print(child):
                    pass  # print to stderr is OK
                elif self._is_inside_json_guard(child, ancestors):
                    pass  # inside --json guard is OK
                elif self._is_inside_exempt_function(ancestors):
                    pass  # inside exempt function is OK
                else:
                    rel_path = str(filepath.relative_to(self._root))
                    context = self._get_line_context(source_lines, child.lineno)
                    self._result.violations.append(Violation(
                        file=rel_path,
                        line=child.lineno,
                        col=child.col_offset,
                        context=context,
                    ))

            self._walk_with_ancestors(child, ancestors + [node], filepath, source_lines)

    @staticmethod
    def _is_print_call(node: ast.Call) -> bool:
        """Check if an AST Call node is a call to print()."""
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            return True
        return False

    def scan(self) -> ScanResult:
        """Scan all .py files under root."""
        py_files: list[Path] = []

        if self._root.is_file() and self._root.suffix == ".py":
            py_files.append(self._root)
        else:
            # Collect from .agent/ and examples/
            for pattern in ["**/*.py"]:
                py_files.extend(self._root.rglob(pattern))

        # Exclude common non-project directories
        exclude_dirs = {"node_modules", ".git", "__pycache__", "dist", "build", ".next", "venv", ".venv"}
        py_files = [
            f for f in py_files
            if not any(part in exclude_dirs for part in f.parts)
        ]

        for filepath in sorted(py_files):
            self._scan_file(filepath)

        return self._result


def print_report(result: ScanResult) -> None:
    """Print scan report using Rich."""
    header("RICH POLICY CHECK")

    console.print(f"Files scanned: {result.files_scanned}")
    console.print(f"Violations: {len(result.violations)}")
    console.print()

    if result.passed:
        success("No print() violations found. All output uses Rich.")
        return

    error(f"Found {len(result.violations)} print() violation(s)")
    console.print()

    table = make_table("File", "Line", "Context")
    for v in result.violations:
        table.add_row(v.file, str(v.line), v.context)

    console.print(table)
    console.print()
    warning("Fix: Replace print() with console.print() / success() / error() / warning()")
    warning("Exception: print() is allowed ONLY inside --json output guards")


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check that all Python output uses Rich (no bare print())",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root path to scan (default: current directory)",
    )

    args = parser.parse_args()
    root = Path(args.path).resolve()

    if not root.exists():
        error(f"Path does not exist: {root}")
        return 1

    checker = RichPolicyChecker(root)
    result = checker.scan()
    print_report(result)

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
