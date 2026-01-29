#!/usr/bin/env python3
"""
Kit Integrity Checker

Validates `.agent` kit consistency:
- Skills referenced by agents exist
- Agents referenced by orchestrator/rules exist
- Frontmatter includes required fields
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    """Validation result."""
    missing_skills: list[tuple[str, str]] = field(default_factory=list)
    missing_agents: list[tuple[str, str]] = field(default_factory=list)
    invalid_frontmatter: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return bool(self.missing_skills or self.missing_agents or self.invalid_frontmatter)
    
    @property
    def error_count(self) -> int:
        return len(self.missing_skills) + len(self.missing_agents) + len(self.invalid_frontmatter)


class KitIntegrityChecker:
    """Integrity checker for the `.agent` kit."""
    
    REQUIRED_FRONTMATTER = ['name', 'description']
    OPTIONAL_FRONTMATTER = ['skills', 'tools', 'model', 'tier']
    
    def __init__(self, agent_dir: Path):
        self.agent_dir = agent_dir
        self.agents_dir = agent_dir / 'agents'
        self.skills_dir = agent_dir / 'skills'
        self.result = ValidationResult()
        
        # Cache de recursos existentes
        self._existing_agents: set[str] = set()
        self._existing_skills: set[str] = set()
    
    def _load_existing_resources(self):
        """Carrega lista de agents e skills existentes."""
        if self.agents_dir.exists():
            for f in self.agents_dir.glob('*.md'):
                self._existing_agents.add(f.stem)
        
        if self.skills_dir.exists():
            for d in self.skills_dir.iterdir():
                if d.is_dir() and (d / 'SKILL.md').exists():
                    self._existing_skills.add(d.name)
    
    def _parse_frontmatter(self, content: str) -> Optional[dict]:
        """Extract YAML frontmatter from a markdown file."""
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter
    
    def _check_agent(self, agent_file: Path):
        """Validate an agent file."""
        content = agent_file.read_text(encoding='utf-8')
        frontmatter = self._parse_frontmatter(content)
        
        if not frontmatter:
            self.result.invalid_frontmatter.append(
                (agent_file.name, "Frontmatter not found")
            )
            return
        
        # Verificar campos obrigatórios
        for field in self.REQUIRED_FRONTMATTER:
            if field not in frontmatter:
                self.result.invalid_frontmatter.append(
                    (agent_file.name, f"Missing required field '{field}'")
                )
        
        # Verificar skills referenciadas
        skills_str = frontmatter.get('skills', '')
        if skills_str:
            skills = [s.strip() for s in skills_str.split(',')]
            for skill in skills:
                if skill and skill not in self._existing_skills:
                    self.result.missing_skills.append((agent_file.name, skill))
    
    def _check_skill(self, skill_dir: Path):
        """Validate a skill directory."""
        skill_file = skill_dir / 'SKILL.md'
        if not skill_file.exists():
            self.result.warnings.append(f"Skill '{skill_dir.name}' is missing SKILL.md")
            return
        
        content = skill_file.read_text(encoding='utf-8')
        frontmatter = self._parse_frontmatter(content)
        
        if not frontmatter:
            self.result.invalid_frontmatter.append(
                (f"skills/{skill_dir.name}/SKILL.md", "Frontmatter not found")
            )
            return
        
        # Verificar campos obrigatórios
        for field in self.REQUIRED_FRONTMATTER:
            if field not in frontmatter:
                self.result.invalid_frontmatter.append(
                    (f"skills/{skill_dir.name}/SKILL.md", f"Missing required field '{field}'")
                )
    
    def _check_orchestrator_references(self):
        """Validate agents referenced in orchestrator docs."""
        orchestrator_file = self.agents_dir / 'orchestrator.md'
        if not orchestrator_file.exists():
            return
        
        content = orchestrator_file.read_text(encoding='utf-8')
        
        # Procurar por referências a agents no formato `agent-name`
        agent_refs = re.findall(r'\| `([a-z-]+)` \|', content)
        
        for agent_ref in agent_refs:
            if agent_ref not in self._existing_agents:
                self.result.missing_agents.append(('orchestrator.md', agent_ref))
    
    def check(self) -> ValidationResult:
        """Run all checks."""
        self._load_existing_resources()
        
        # Verificar agents
        if self.agents_dir.exists():
            for agent_file in self.agents_dir.glob('*.md'):
                self._check_agent(agent_file)
        
        # Verificar skills
        if self.skills_dir.exists():
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir():
                    self._check_skill(skill_dir)
        
        # Verificar referências no orchestrator
        self._check_orchestrator_references()
        
        return self.result
    
    def generate_report(self) -> str:
        """Generate a markdown report."""
        lines = ["# Kit Integrity Report", ""]
        
        if not self.result.has_errors and not self.result.warnings:
            lines.append("OK: no problems found.")
            lines.append("")
            lines.append(f"- Agents checked: {len(self._existing_agents)}")
            lines.append(f"- Skills checked: {len(self._existing_skills)}")
            return '\n'.join(lines)
        
        # Missing Skills
        if self.result.missing_skills:
            lines.append("## Missing skills")
            lines.append("")
            lines.append("| File | Referenced skill |")
            lines.append("|------|------------------|")
            for file, skill in self.result.missing_skills:
                lines.append(f"| `{file}` | `{skill}` |")
            lines.append("")
        
        # Missing Agents
        if self.result.missing_agents:
            lines.append("## Missing agents")
            lines.append("")
            lines.append("| File | Referenced agent |")
            lines.append("|------|------------------|")
            for file, agent in self.result.missing_agents:
                lines.append(f"| `{file}` | `{agent}` |")
            lines.append("")
        
        # Invalid Frontmatter
        if self.result.invalid_frontmatter:
            lines.append("## Invalid frontmatter")
            lines.append("")
            lines.append("| File | Problem |")
            lines.append("|------|---------|")
            for file, problem in self.result.invalid_frontmatter:
                lines.append(f"| `{file}` | {problem} |")
            lines.append("")
        
        # Warnings
        if self.result.warnings:
            lines.append("## Warnings")
            lines.append("")
            for warning in self.result.warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        # Summary
        lines.append("---")
        lines.append("")
        lines.append(f"**Total errors:** {self.result.error_count}")
        lines.append(f"**Total warnings:** {len(self.result.warnings)}")
        
        return '\n'.join(lines)


def main():
    """Main entry point."""
    # Determinar diretório .agent
    if len(sys.argv) > 1:
        agent_dir = Path(sys.argv[1])
    else:
        agent_dir = Path(__file__).parent.parent
    
    if not agent_dir.exists():
        print(f"ERROR: directory not found: {agent_dir}")
        sys.exit(1)
    
    checker = KitIntegrityChecker(agent_dir)
    result = checker.check()
    
    print(checker.generate_report())
    
    sys.exit(1 if result.has_errors else 0)


if __name__ == '__main__':
    main()
