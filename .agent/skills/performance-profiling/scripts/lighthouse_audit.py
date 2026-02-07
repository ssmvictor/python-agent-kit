#!/usr/bin/env python3
"""
Skill: performance-profiling
Script: lighthouse_audit.py
Purpose: Run Lighthouse performance audit on a URL
Usage: python lighthouse_audit.py https://example.com
Output: JSON with performance scores
Note: Requires lighthouse CLI (npm install -g lighthouse)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from _console import console, success, error, warning, step

import subprocess
import json
import os
import tempfile

def run_lighthouse(url: str) -> dict:
    """Run Lighthouse audit on URL."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name
        
        result = subprocess.run(
            [
                "lighthouse",
                url,
                "--output=json",
                f"--output-path={output_path}",
                "--chrome-flags=--headless",
                "--only-categories=performance,accessibility,best-practices,seo"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                report = json.load(f)
            os.unlink(output_path)
            
            categories = report.get("categories", {})
            return {
                "url": url,
                "scores": {
                    "performance": int(categories.get("performance", {}).get("score", 0) * 100),
                    "accessibility": int(categories.get("accessibility", {}).get("score", 0) * 100),
                    "best_practices": int(categories.get("best-practices", {}).get("score", 0) * 100),
                    "seo": int(categories.get("seo", {}).get("score", 0) * 100)
                },
                "summary": get_summary(categories)
            }
        else:
            return {"error": "Lighthouse failed to generate report", "stderr": result.stderr[:500]}
            
    except subprocess.TimeoutExpired:
        return {"error": "Lighthouse audit timed out"}
    except FileNotFoundError:
        return {"error": "Lighthouse CLI not found. Install with: npm install -g lighthouse"}

def get_summary(categories: dict) -> str:
    """Generate summary based on scores."""
    perf = categories.get("performance", {}).get("score", 0) * 100
    if perf >= 90:
        return "Excellent performance"
    elif perf >= 50:
        return "Needs improvement"
    else:
        return "Poor performance"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        error("Usage: python lighthouse_audit.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    step(f"Running Lighthouse audit for {url}...")
    result = run_lighthouse(url)
    
    if "error" in result:
        error(result["error"])
    else:
        scores = result.get("scores", {})
        perf = scores.get("performance", 0)
        if perf >= 90:
            success(f"Performance: {perf}/100 - {result.get('summary', '')}")
        elif perf >= 50:
            warning(f"Performance: {perf}/100 - {result.get('summary', '')}")
        else:
            error(f"Performance: {perf}/100 - {result.get('summary', '')}")
    
    console.print(json.dumps(result, indent=2))
