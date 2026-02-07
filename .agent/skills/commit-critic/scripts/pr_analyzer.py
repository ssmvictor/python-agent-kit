#!/usr/bin/env python3
"""
PR Analyzer - Analisa Pull Requests seguindo boas praticas.

Uso:
    python pr_analyzer.py                         # Analisa PR atual (branch)
    python pr_analyzer.py --title "titulo"        # Valida titulo
    python pr_analyzer.py --base main             # Compara com branch base
"""

import sys
from pathlib import Path

# Adiciona path para encontrar _console.py
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from _console import console, success, error, warning, step, make_table, header, RICH_AVAILABLE

import argparse
import re
import subprocess
from dataclasses import dataclass, field
from typing import Optional


COMMIT_PATTERN = re.compile(
    r"^(?P<type>\w+)"
    r"(?P<breaking>!)?"
    r"(?:\((?P<scope>[\w\-]+)\))?"
    r":\s"
    r"(?P<description>.+)$"
)

VALID_TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "build", "ci"]

# Padroes de linked issues
ISSUE_PATTERNS = [
    r"(?i)closes?\s+#(\d+)",
    r"(?i)fixes?\s+#(\d+)",
    r"(?i)resolves?\s+#(\d+)",
    r"#(\d+)",
]


@dataclass
class PRAnalysis:
    """Resultado da analise de uma PR."""
    title: str
    branch: str
    commits: list[str] = field(default_factory=list)
    title_valid: bool = False
    title_issues: list[str] = field(default_factory=list)
    commit_issues: list[str] = field(default_factory=list)
    linked_issues: list[str] = field(default_factory=list)
    has_breaking_change: bool = False
    suggested_title: Optional[str] = None
    squash_recommended: bool = False


def get_current_branch() -> str:
    """Obtem branch atual."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_commits_since_base(base: str = "main") -> list[str]:
    """Obtem commits desde a branch base."""
    try:
        result = subprocess.run(
            ["git", "log", f"{base}..HEAD", "--pretty=%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [c for c in result.stdout.strip().split("\n") if c]
    except subprocess.CalledProcessError:
        return []


def validate_title(title: str) -> tuple[bool, list[str], Optional[str]]:
    """Valida titulo da PR."""
    issues = []
    
    match = COMMIT_PATTERN.match(title)
    
    if not match:
        issues.append("Titulo nao segue Conventional Commits")
        suggestion = suggest_title(title)
        return False, issues, suggestion
    
    commit_type = match.group("type")
    description = match.group("description")
    
    if commit_type not in VALID_TYPES:
        issues.append(f"Tipo '{commit_type}' invalido")
    
    if description.endswith("."):
        issues.append("Remova pontuacao final")
    
    if "wip" in title.lower():
        issues.append("Remova 'WIP' do titulo final")
    
    return len(issues) == 0, issues, None


def suggest_title(title: str) -> str:
    """Sugere titulo corrigido."""
    lower = title.lower()
    
    # Detecta tipo
    if any(word in lower for word in ["add", "adicionar", "novo", "new", "implement"]):
        suggested_type = "feat"
    elif any(word in lower for word in ["fix", "corrigir", "bug", "resolver"]):
        suggested_type = "fix"
    elif any(word in lower for word in ["doc", "readme"]):
        suggested_type = "docs"
    elif any(word in lower for word in ["refactor", "clean"]):
        suggested_type = "refactor"
    else:
        suggested_type = "feat"
    
    # Limpa titulo
    clean = re.sub(r"^\[?wip\]?\s*:?\s*", "", title, flags=re.IGNORECASE)
    clean = clean.rstrip(".").lower()
    
    return f"{suggested_type}: {clean}"


def analyze_commits(commits: list[str]) -> tuple[list[str], bool, bool]:
    """Analisa commits da PR."""
    issues = []
    has_breaking = False
    squash_recommended = False
    
    if len(commits) > 5:
        squash_recommended = True
        issues.append(f"Muitos commits ({len(commits)}). Considere squash")
    
    wip_count = 0
    fixup_count = 0
    
    for commit in commits:
        if "!" in commit or "BREAKING CHANGE" in commit:
            has_breaking = True
        
        if "wip" in commit.lower():
            wip_count += 1
        
        if commit.startswith("fixup!") or commit.startswith("squash!"):
            fixup_count += 1
        
        if not COMMIT_PATTERN.match(commit):
            issues.append(f"Commit invalido: `{commit[:50]}...`" if len(commit) > 50 else f"Commit invalido: `{commit}`")
    
    if wip_count > 0:
        issues.append(f"{wip_count} commits WIP - limpe antes do merge")
        squash_recommended = True
    
    if fixup_count > 0:
        issues.append(f"{fixup_count} commits fixup/squash pendentes")
        squash_recommended = True
    
    return issues, has_breaking, squash_recommended


def find_linked_issues(commits: list[str]) -> list[str]:
    """Encontra issues linkadas nos commits."""
    issues = set()
    
    for commit in commits:
        for pattern in ISSUE_PATTERNS:
            matches = re.findall(pattern, commit)
            issues.update(matches)
    
    return sorted(issues)


def analyze_pr(title: str, base: str = "main") -> PRAnalysis:
    """Executa analise completa da PR."""
    branch = get_current_branch()
    commits = get_commits_since_base(base)
    
    title_valid, title_issues, suggested = validate_title(title)
    commit_issues, has_breaking, squash = analyze_commits(commits)
    linked = find_linked_issues(commits)
    
    return PRAnalysis(
        title=title,
        branch=branch,
        commits=commits,
        title_valid=title_valid,
        title_issues=title_issues,
        commit_issues=commit_issues,
        linked_issues=linked,
        has_breaking_change=has_breaking,
        suggested_title=suggested,
        squash_recommended=squash,
    )


def format_analysis(pr: PRAnalysis) -> None:
    """Formata analise para exibicao com Rich."""
    header("ANALISE DA PR")
    
    # Status geral
    all_issues = pr.title_issues + pr.commit_issues
    if not all_issues:
        success("Status: Aprovado")
    elif any("SECURITY" in i for i in all_issues):
        error("Status: Bloqueado")
    else:
        warning("Status: Ajustes Necessarios")
    
    # Info basica
    console.print(f"\n[b]Branch:[/b] `{pr.branch}`")
    console.print(f"[b]Titulo:[/b] `{pr.title}`")
    console.print(f"[b]Commits:[/b] {len(pr.commits)}")
    
    # Titulo section
    console.print("\n[b]Titulo[/b]")
    if pr.title_valid:
        success("Formato Conventional Commits")
    else:
        for issue in pr.title_issues:
            warning(issue)
    
    if pr.suggested_title:
        console.print(f"[b]Sugestao:[/b] `{pr.suggested_title}`")
    
    # Commits table
    console.print("\n[b]Commits[/b]")
    if not pr.commit_issues:
        success("Todos os commits validos")
    else:
        table = make_table("Problema")
        for issue in pr.commit_issues:
            table.add_row(issue)
        console.print(table)
    
    if pr.squash_recommended:
        warning("Recomendacao: Squash antes do merge")
    
    # Breaking Changes
    if pr.has_breaking_change:
        console.print("\n[bold red]Breaking Changes[/bold red]")
        console.print("  - Label `breaking-change` aplicada")
        console.print("  - Documentacao atualizada")
        console.print("  - Migration guide")
    
    # Linked Issues
    console.print("\n[b]Linked Issues[/b]")
    if pr.linked_issues:
        for issue in pr.linked_issues:
            console.print(f"  - #{issue}")
    else:
        warning("Nenhuma issue linkada. Adicione `Closes #123`")


def main():
    parser = argparse.ArgumentParser(description="Analisa Pull Requests")
    parser.add_argument("--title", "-t", help="Titulo da PR para validar")
    parser.add_argument("--base", "-b", default="main", help="Branch base (default: main)")
    args = parser.parse_args()
    
    try:
        title = args.title or get_current_branch()
        pr = analyze_pr(title, args.base)
        format_analysis(pr)
        
        # Exit code baseado na validacao
        has_issues = pr.title_issues or pr.commit_issues
        sys.exit(1 if has_issues else 0)
        
    except subprocess.CalledProcessError as e:
        error(f"Erro ao executar git: {e}")
        sys.exit(2)
    except Exception as e:
        error(f"Erro: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
