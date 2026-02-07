"""
Console output utilities with Rich library support and graceful fallback.

This module provides a unified interface for terminal output formatting.
When Rich is installed, it provides rich formatting (colors, tables, panels).
When Rich is not available, it falls back to plain text output without errors.

Usage:
    from _console import console, header, success, error, warning, step, make_table, status
    
    header("My Application")
    success("Operation completed")
    error("Something went wrong")
    warning("Be careful")
    step("Running task...")
    
    table = make_table("Column 1", "Column 2")
    table.add_row("Value 1", "Value 2")
    console.print(table)
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Generator, List, Optional, Tuple, Union

# Try to import Rich with graceful fallback
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.table import Table
    from rich.text import Text
    
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# ============================================================================
# Rich Available Implementation
# ============================================================================

if RICH_AVAILABLE:
    # Global console instance
    console = Console()
    
    def header(text: str) -> None:
        """Print a header panel with centered title."""
        console.print(Panel(
            Text(text, justify="center"),
            expand=False,
            padding=(1, 4)
        ))
    
    def success(text: str) -> None:
        """Print success message with green OK prefix."""
        console.print(f"[green][OK][/green] {text}")
    
    def error(text: str) -> None:
        """Print error message with red FAIL prefix."""
        console.print(f"[red][FAIL][/red] {text}")
    
    def warning(text: str) -> None:
        """Print warning message with yellow WARN prefix."""
        console.print(f"[yellow][WARN][/yellow] {text}")
    
    def step(text: str) -> None:
        """Print step message with blue RUN prefix."""
        console.print(f"[blue][RUN][/blue] {text}")
    
    def make_table(*columns: str) -> Table:
        """Create a Rich table with specified columns."""
        table = Table(show_header=True, header_style="bold")
        for col in columns:
            table.add_column(col)
        return table
    
    @contextmanager
    def status(text: str) -> Generator[None, None, None]:
        """Context manager that shows a spinner status while executing."""
        with console.status(text):
            yield


# ============================================================================
# Fallback Implementation (no Rich)
# ============================================================================

else:
    # Simple console wrapper
    class _FallbackConsole:
        """Fallback console that just prints to stdout."""
        
        def print(self, *args: Any, **kwargs: Any) -> None:
            """Print message, stripping Rich markup."""
            if args:
                text = str(args[0])
                # Remove Rich markup like [green], [/green], etc.
                import re
                text = re.sub(r'\[/?[^\]]+\]', '', text)
                print(text)
            else:
                print()
    
    console = _FallbackConsole()
    
    def header(text: str) -> None:
        """Print a simple text header with separators."""
        print("=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def success(text: str) -> None:
        """Print success message with OK prefix."""
        print(f"[OK] {text}")
    
    def error(text: str) -> None:
        """Print error message with FAIL prefix."""
        print(f"[FAIL] {text}")
    
    def warning(text: str) -> None:
        """Print warning message with WARN prefix."""
        print(f"[WARN] {text}")
    
    def step(text: str) -> None:
        """Print step message with RUN prefix."""
        print(f"[RUN] {text}")
    
    class _FallbackTable:
        """Fallback table that prints tabular text."""
        
        def __init__(self, columns: List[str]) -> None:
            self._columns = columns
            self._rows: List[List[str]] = []
        
        def add_row(self, *values: str) -> None:
            """Add a row to the table."""
            self._rows.append(list(values))
        
        def __str__(self) -> str:
            """Render table as plain text."""
            if not self._rows:
                return ""
            
            # Calculate column widths
            widths = [len(col) for col in self._columns]
            for row in self._rows:
                for i, val in enumerate(row):
                    if i < len(widths):
                        widths[i] = max(widths[i], len(str(val)))
            
            # Build output
            lines = []
            
            # Header row
            header_row = " | ".join(
                col.ljust(widths[i]) for i, col in enumerate(self._columns)
            )
            lines.append(header_row)
            lines.append("-" * len(header_row))
            
            # Data rows
            for row in self._rows:
                lines.append(" | ".join(
                    str(val).ljust(widths[i]) for i, val in enumerate(row)
                ))
            
            return "\n".join(lines)
        
        def print(self) -> None:
            """Print the table."""
            print(str(self))
    
    def make_table(*columns: str) -> _FallbackTable:
        """Create a fallback table with specified columns."""
        return _FallbackTable(list(columns))
    
    @contextmanager
    def status(text: str) -> Generator[None, None, None]:
        """Context manager that just prints the status text."""
        print(text)
        yield


# ============================================================================
# Utility Functions (work with both implementations)
# ============================================================================

def print_table(table: Union[Table, _FallbackTable]) -> None:
    """
    Print a table in a consistent way regardless of Rich availability.
    
    Args:
        table: A Rich Table or FallbackTable instance
    """
    if RICH_AVAILABLE:
        console.print(table)
    else:
        table.print()


# Export all public symbols
__all__ = [
    "console",
    "header",
    "success", 
    "error",
    "warning",
    "step",
    "make_table",
    "status",
    "print_table",
    "RICH_AVAILABLE",
]
