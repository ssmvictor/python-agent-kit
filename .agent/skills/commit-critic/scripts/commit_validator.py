#!/usr/bin/env python3
"""
Commit Validator - Valida formato de commits seguindo Conventional Commits.

Uso:
    python commit_validator.py                    # Valida ultimo commit
    python commit_validator.py --message "msg"    # Valida mensagem especifica
    python commit_validator.py --range HEAD~5    # Valida ultimos 5 commits
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


COMMIT_TYPES = {
    "feat": "Nova funcionalidade",
    "fix": "Correcao de bug",
    "docs": "Documentacao",
    "style": "Formatacao",
    "refactor": "Refatoracao",
    "perf": "Performance",
    "test": "Testes",
    "chore": "Manutencao",
    "build": "Build/dependencias",
    "ci": "CI/CD",
}

# Regex para Conventional Commits
COMMIT_PATTERN = re.compile(
    r"^(?P<type>\w+)"
    r"(?P<breaking>!)?"
    r"(?:\((?P<scope>[\w\-]+)\))?"
    r":\s"
    r"(?P<description>.+)$"
)

# Padroes de secrets
SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][^'\"]+['\"]", "API Key detectada"),
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]+['\"]", "Senha detectada"),
    (r"(?i)(secret|token)\s*[:=]\s*['\"][^'\"]+['\"]", "Secret/Token detectado"),
    (r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*", "Bearer token detectado"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Token detectado"),
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key detectada"),
]


@dataclass
class ValidationResult:
    """Resultado da validacao de um commit."""
    valid: bool
    message: str
    commit_type: Optional[str] = None
    scope: Optional[str] = None
    description: Optional[str] = None
    breaking: bool = False
    issues: list = None
    suggestion: Optional[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []


def get_last_commit_message() -> str:
    """Obtem mensagem do ultimo commit."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_commit_diff() -> str:
    """Obtem diff do ultimo commit."""
    result = subprocess.run(
        ["git", "show", "--pretty=format:", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def check_secrets(diff: str) -> list[tuple[str, str]]:
    """Detecta secrets no diff."""
    findings = []
    for pattern, description in SECRET_PATTERNS:
        if re.search(pattern, diff):
            findings.append((description, pattern))
    return findings


def validate_commit(message: str, diff: str = "") -> ValidationResult:
    """Valida uma mensagem de commit."""
    issues = []
    
    # Parse da mensagem
    match = COMMIT_PATTERN.match(message)
    
    if not match:
        return ValidationResult(
            valid=False,
            message=message,
            issues=["Formato invalido. Use: tipo(escopo): descricao"],
            suggestion=suggest_fix(message),
        )
    
    commit_type = match.group("type")
    scope = match.group("scope")
    description = match.group("description")
    breaking = match.group("breaking") == "!"
    
    # Validar tipo
    if commit_type not in COMMIT_TYPES:
        issues.append(f"Tipo '{commit_type}' invalido. Use: {', '.join(COMMIT_TYPES.keys())}")
    
    # Validar descricao
    if description.endswith("."):
        issues.append("Remova pontuacao final")
    
    if len(description) > 72:
        issues.append(f"Descricao muito longa ({len(description)} chars). Max: 72")
    
    if description[0].isupper():
        issues.append("Descricao deve iniciar com minuscula")
    
    # Verificar secrets no diff
    if diff:
        secrets = check_secrets(diff)
        for desc, _ in secrets:
            issues.append(f"🔴 SECURITY: {desc}")
    
    return ValidationResult(
        valid=len(issues) == 0,
        message=message,
        commit_type=commit_type,
        scope=scope,
        description=description,
        breaking=breaking,
        issues=issues,
        suggestion=suggest_fix(message) if issues else None,
    )


def suggest_fix(message: str) -> str:
    """Sugere correcao para mensagem invalida."""
    # Remove pontuacao final
    suggestion = message.rstrip(".")
    
    # Tenta detectar tipo
    lower = message.lower()
    if any(word in lower for word in ["add", "adicionar", "novo", "new", "implement"]):
        suggested_type = "feat"
    elif any(word in lower for word in ["fix", "corrigir", "bug", "resolver"]):
        suggested_type = "fix"
    elif any(word in lower for word in ["doc", "readme", "comment"]):
        suggested_type = "docs"
    elif any(word in lower for word in ["refactor", "clean", "reorgan"]):
        suggested_type = "refactor"
    else:
        suggested_type = "chore"
    
    # Se nao tem formato, sugere
    if not COMMIT_PATTERN.match(suggestion):
        desc = suggestion.lower().replace(".", "")
        return f"{suggested_type}: {desc}"
    
    return suggestion


def format_result(result: ValidationResult) -> str:
    """Formata resultado para exibicao."""
    status = "✅ Aprovado" if result.valid else "❌ Reprovado"
    
    output = [
        "## 🔍 Analise do Commit",
        "",
        f"**Mensagem:** `{result.message}`",
        f"**Status:** {status}",
        "",
    ]
    
    if result.commit_type:
        output.append(f"**Tipo:** `{result.commit_type}` - {COMMIT_TYPES.get(result.commit_type, 'Desconhecido')}")
        if result.scope:
            output.append(f"**Escopo:** `{result.scope}`")
        if result.breaking:
            output.append("**Breaking Change:** ⚠️ Sim")
    
    if result.issues:
        output.extend(["", "### Problemas"])
        for issue in result.issues:
            output.append(f"- {issue}")
    
    if result.suggestion:
        output.extend(["", f"**Sugestao:** `{result.suggestion}`"])
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Valida commits Conventional Commits")
    parser.add_argument("--message", "-m", help="Mensagem para validar")
    parser.add_argument("--range", "-r", help="Range de commits (ex: HEAD~5)")
    parser.add_argument("--json", action="store_true", help="Output em JSON")
    args = parser.parse_args()
    
    try:
        if args.message:
            result = validate_commit(args.message)
        else:
            message = get_last_commit_message()
            diff = get_commit_diff()
            result = validate_commit(message, diff)
        
        print(format_result(result))
        sys.exit(0 if result.valid else 1)
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar git: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
