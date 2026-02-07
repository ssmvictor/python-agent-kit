#!/usr/bin/env python3
"""
Session Manager - Antigravity Kit
=================================
Analyzes project state, detects tech stack, tracks file statistics, and provides
a summary of the current session.

Usage:
    python .agent/scripts/session_manager.py status [path]
    python .agent/scripts/session_manager.py info [path]
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Import console utilities
from _console import console, success, header, RICH_AVAILABLE


def get_project_root(path: str) -> Path:
    return Path(path).resolve()


def analyze_package_json(root: Path) -> Dict[str, Any]:
    pkg_file = root / "package.json"
    if not pkg_file.exists():
        return {"type": "unknown", "dependencies": {}}
    
    try:
        with open(pkg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}
        
        stack = []
        if "next" in all_deps: stack.append("Next.js")
        elif "react" in all_deps: stack.append("React")
        elif "vue" in all_deps: stack.append("Vue")
        elif "svelte" in all_deps: stack.append("Svelte")
        elif "express" in all_deps: stack.append("Express")
        elif "nestjs" in all_deps or "@nestjs/core" in all_deps: stack.append("NestJS")
        
        if "tailwindcss" in all_deps: stack.append("Tailwind CSS")
        if "prisma" in all_deps: stack.append("Prisma")
        if "typescript" in all_deps: stack.append("TypeScript")
        
        return {
            "name": data.get("name", "unnamed"),
            "version": data.get("version", "0.0.0"),
            "stack": stack,
            "scripts": list(data.get("scripts", {}).keys())
        }
    except Exception as e:
        return {"error": str(e)}


def count_files(root: Path) -> Dict[str, int]:
    stats = {"created": 0, "modified": 0, "total": 0}
    # Simple count for now, comprehensive tracking would require git diff or extensive history
    exclude = {".git", "node_modules", ".next", "dist", "build", ".agent", ".gemini", "__pycache__"}
    
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in exclude]
        stats["total"] += len(files)
        
    return stats


def detect_features(root: Path) -> List[str]:
    # Heuristic: look at folder names in src/
    features = []
    src = root / "src"
    if src.exists():
        possible_dirs = ["components", "modules", "features", "app", "pages", "services"]
        for d in possible_dirs:
            p = src / d
            if p.exists() and p.is_dir():
                # List subdirectories as likely features
                for child in p.iterdir():
                    if child.is_dir():
                        features.append(child.name)
    return features[:10]  # Limit to top 10


def print_status(root: Path):
    info = analyze_package_json(root)
    stats = count_files(root)
    features = detect_features(root)
    
    header("PROJECT STATUS")
    
    if RICH_AVAILABLE:
        from rich.panel import Panel
        # Project info panel
        console.print(Panel(
            f"[bold]Project:[/bold] {info.get('name', root.name)}\n"
            f"[bold]Path:[/bold] {root}\n"
            f"[bold]Type:[/bold] {', '.join(info.get('stack', ['Generic']))}\n"
            f"[bold]Status:[/bold] active",
            title="Project Overview",
            expand=False
        ))
    else:
        # Fallback: simple text output
        console.print(f"Project: {info.get('name', root.name)}")
        console.print(f"Path: {root}")
        console.print(f"Type: {', '.join(info.get('stack', ['Generic']))}")
        console.print("Status: active")
    
    # Tech stack
    console.print("\nTech stack:")
    for tech in info.get('stack', []):
        console.print(f"  ● {tech}")
        
    # Features
    console.print(f"\nDetected modules/features ({len(features)}):")
    if features:
        for feat in features:
            console.print(f"  • {feat}")
    else:
        console.print("   (No distinct feature modules detected)")
        
    console.print(f"\nFiles: {stats['total']} total files tracked")
    console.print()


def main():
    parser = argparse.ArgumentParser(description="Session Manager")
    parser.add_argument("command", choices=["status", "info"], help="Command to run")
    parser.add_argument("path", nargs="?", default=".", help="Project path")
    
    args = parser.parse_args()
    root = get_project_root(args.path)
    
    if args.command == "status":
        print_status(root)
    elif args.command == "info":
        print(json.dumps(analyze_package_json(root), indent=2))


if __name__ == "__main__":
    main()
