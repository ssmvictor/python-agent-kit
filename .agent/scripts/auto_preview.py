#!/usr/bin/env python3
"""
Auto Preview - Antigravity Kit
==============================
Manages (start/stop/status) the local development server for previewing the application.

Usage:
    python .agent/scripts/auto_preview.py start [port]
    python .agent/scripts/auto_preview.py stop
    python .agent/scripts/auto_preview.py status
"""

import os
import sys
import time
import json
import signal
import argparse
import subprocess
from pathlib import Path

# Import console utilities
from _console import console, success, error, warning, header, RICH_AVAILABLE


AGENT_DIR = Path(".agent")
PID_FILE = AGENT_DIR / "preview.pid"
LOG_FILE = AGENT_DIR / "preview.log"


def get_project_root():
    return Path(".").resolve()


def is_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_start_command(root):
    pkg_file = root / "package.json"
    if not pkg_file.exists():
        return None
    
    with open(pkg_file, 'r') as f:
        data = json.load(f)
    
    scripts = data.get("scripts", {})
    if "dev" in scripts:
        return ["npm", "run", "dev"]
    elif "start" in scripts:
        return ["npm", "start"]
    return None


def start_server(port=3000):
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if is_running(pid):
                warning(f"Preview already running (PID: {pid})")
                return
        except:
            pass  # Invalid PID file

    root = get_project_root()
    cmd = get_start_command(root)
    
    if not cmd:
        error("No 'dev' or 'start' script found in package.json")
        sys.exit(1)
    
    # Add port env var if needed (simple heuristic)
    env = os.environ.copy()
    env["PORT"] = str(port)
    
    step_msg = f"Starting preview on port {port}..."
    if RICH_AVAILABLE:
        from rich.panel import Panel
        console.print(Panel(
            f"[bold]Starting preview server[/bold]\nPort: {port}",
            expand=False
        ))
    else:
        console.print(step_msg)
    
    with open(LOG_FILE, "w") as log:
        process = subprocess.Popen(
            cmd,
            cwd=str(root),
            stdout=log,
            stderr=log,
            env=env,
            shell=True  # Required for npm on windows often, or consistent path handling
        )
    
    PID_FILE.write_text(str(process.pid))
    success(f"Preview started (PID: {process.pid})")
    console.print(f"   Logs: {LOG_FILE}")
    console.print(f"   URL: http://localhost:{port}")


def stop_server():
    if not PID_FILE.exists():
        warning("No preview server found.")
        return

    try:
        pid = int(PID_FILE.read_text().strip())
        if is_running(pid):
            # Try gentle kill first
            if sys.platform != 'win32':
                os.kill(pid, signal.SIGTERM)
            else:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
            success(f"Preview stopped (PID: {pid})")
        else:
            warning("Process was not running.")
    except Exception as e:
        error(f"Failed to stop server: {e}")
    finally:
        if PID_FILE.exists():
            PID_FILE.unlink()


def status_server():
    running = False
    pid = None
    url = "Unknown"
    
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            if is_running(pid):
                running = True
                # Heuristic for URL, strictly we should save it
                url = "http://localhost:3000"
        except:
            pass
    
    header("PREVIEW STATUS")
    
    if RICH_AVAILABLE:
        from rich.panel import Panel
        if running:
            console.print(Panel(
                f"[bold green]Status:[/bold green] Running\n"
                f"[bold]PID:[/bold] {pid}\n"
                f"[bold]URL:[/bold] {url}\n"
                f"[bold]Logs:[/bold] {LOG_FILE}",
                title="Preview Server",
                expand=False
            ))
        else:
            console.print(Panel(
                "[bold red]Status:[/bold red] Stopped",
                title="Preview Server",
                expand=False
            ))
    else:
        if running:
            console.print("Status: running")
            console.print(f"PID: {pid}")
            console.print(f"URL: {url} (heuristic)")
            console.print(f"Logs: {LOG_FILE}")
        else:
            console.print("Status: stopped")
    console.print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start", "stop", "status"])
    parser.add_argument("port", nargs="?", default="3000")
    
    args = parser.parse_args()
    
    if args.action == "start":
        start_server(int(args.port))
    elif args.action == "stop":
        stop_server()
    elif args.action == "status":
        status_server()


if __name__ == "__main__":
    main()
