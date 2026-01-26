#!/usr/bin/env python3
"""
PR Analyzer - Analisa Pull Requests seguindo boas praticas.

Uso:
    python pr_analyzer.py                         # Analisa PR atual (branch)
    python pr_analyzer.py --title "titulo"        # Valida titulo
    python pr_analyzer.py --base main             # Compara com branch base
"""

import argparse
import re
import subprocess
import sys
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


def format_analysis(pr: PRAnalysis) -> str:
    """Formata analise para exibicao."""
    # Status geral
    all_issues = pr.title_issues + pr.commit_issues
    if not all_issues:
        status = "✅ Aprovado"
    elif any("SECURITY" in i for i in all_issues):
        status = "🔴 Bloqueado"
    else:
        status = "⚠️ Ajustes Necessarios"
    
    output = [
        "## 🔍 Analise da PR",
        "",
        f"**Branch:** `{pr.branch}`",
        f"**Titulo:** `{pr.title}`",
        f"**Commits:** {len(pr.commits)}",
        f"**Status:** {status}",
        "",
    ]
    
    # Titulo
    output.append("### Titulo")
    if pr.title_valid:
        output.append("- [x] Formato Conventional Commits")
    else:
        output.append("- [ ] Formato Conventional Commits")
        for issue in pr.title_issues:
            output.append(f"  - {issue}")
    
    if pr.suggested_title:
        output.append(f"- **Sugestao:** `{pr.suggested_title}`")
    
    # Commits
    output.extend(["", "### Commits"])
    if not pr.commit_issues:
        output.append("- [x] Todos os commits validos")
    else:
        for issue in pr.commit_issues:
            output.append(f"- [ ] {issue}")
    
    if pr.squash_recommended:
        output.append("- 💡 **Recomendacao:** Squash antes do merge")
    
    # Breaking Changes
    if pr.has_breaking_change:
        output.extend([
            "",
            "### ⚠️ Breaking Changes",
            "- [ ] Label `breaking-change` aplicada",
            "- [ ] Documentacao atualizada",
            "- [ ] Migration guide",
        ])
    
    # Linked Issues
    output.extend(["", "### Linked Issues"])
    if pr.linked_issues:
        for issue in pr.linked_issues:
            output.append(f"- #{issue}")
    else:
        output.append("- ⚠️ Nenhuma issue linkada. Adicione `Closes #123`")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Analisa Pull Requests")
    parser.add_argument("--title", "-t", help="Titulo da PR para validar")
    parser.add_argument("--base", "-b", default="main", help="Branch base (default: main)")
    args = parser.parse_args()
    
    try:
        title = args.title or get_current_branch()
        pr = analyze_pr(title, args.base)
        print(format_analysis(pr))
        
        # Exit code baseado na validacao
        has_issues = pr.title_issues or pr.commit_issues
        sys.exit(1 if has_issues else 0)
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar git: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
