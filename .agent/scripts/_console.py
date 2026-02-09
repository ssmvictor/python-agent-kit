"""
Console output utilities with Rich library (mandatory dependency).

Rich is a REQUIRED dependency for all kit scripts. All terminal output
must go through this module. The only exception is `print()` for
machine-readable `--json` output paths.

If Rich is not installed, the module fails fast with install instructions.

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
from typing import IO, Generator, TextIO, cast

# Rich is a MANDATORY dependency. Fail fast with clear instructions.
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print(
        "ERROR: Rich is required but not installed.\n"
        "Install it with:\n\n"
        "    pip install rich\n\n"
        "Or install all kit dependencies:\n\n"
        "    pip install -r .agent/scripts/requirements.txt\n",
        file=sys.stderr,
    )
    sys.exit(1)


class _UnicodeSafeStream:
    """Wrap stdout to prevent UnicodeEncodeError on limited terminals."""

    def __init__(self, stream: TextIO) -> None:
        self._stream = stream
        self.encoding = getattr(stream, "encoding", None)

    def write(self, text: str) -> int:
        try:
            return self._stream.write(text)
        except UnicodeEncodeError:
            encoding = self.encoding or "utf-8"
            safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
            return self._stream.write(safe_text)

    def flush(self) -> None:
        self._stream.flush()

    def isatty(self) -> bool:
        return self._stream.isatty()

    def fileno(self) -> int:
        return self._stream.fileno()

    def __getattr__(self, name: str):
        return getattr(self._stream, name)


# Global console instance
console = Console(file=cast(IO[str], _UnicodeSafeStream(sys.stdout)))
RICH_AVAILABLE = True


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


def print_table(table: Table) -> None:
    """
    Print a table using the global console.

    Args:
        table: A Rich Table instance
    """
    console.print(table)


# Export all public symbols
__all__ = [
    "console",
    "RICH_AVAILABLE",
    "header",
    "success",
    "error",
    "warning",
    "step",
    "make_table",
    "status",
    "print_table",
]
