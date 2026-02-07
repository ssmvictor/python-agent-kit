#!/usr/bin/env python3
"""
Skill Tier Audit Script

Lists all skills by maturity tier (lite, standard, pro).
Detects skills with missing tier field.

Usage:
    python .agent/scripts/skill_tier_audit.py
"""

from pathlib import Path
from dataclasses import dataclass
import re
import sys

# Import console utilities
from _console import console, success, error, warning, header, make_table


@dataclass
class SkillInfo:
    """Skill metadata from frontmatter."""
    name: str
    tier: str
    file_count: int
    has_references: bool
    has_scripts: bool


def parse_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()
    return frontmatter


def analyze_skill(skill_dir: Path) -> SkillInfo | None:
    """Analyze a skill directory and return SkillInfo."""
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        return None
    
    content = skill_md.read_text(encoding='utf-8')
    frontmatter = parse_frontmatter(content)
    
    # Count files recursively
    file_count = sum(1 for _ in skill_dir.rglob('*') if _.is_file())
    
    return SkillInfo(
        name=frontmatter.get('name', skill_dir.name),
        tier=frontmatter.get('tier', '[MISSING]'),
        file_count=file_count,
        has_references=(skill_dir / 'references').is_dir(),
        has_scripts=(skill_dir / 'scripts').is_dir(),
    )


def get_tier_style(tier: str) -> str:
    """Get Rich style for tier."""
    tier_styles = {
        'pro': 'green',
        'standard': 'blue',
        'lite': 'yellow',
        '[MISSING]': 'red'
    }
    return tier_styles.get(tier, 'white')


def main() -> int:
    """Main entry point."""
    # Find skills directory
    script_dir = Path(__file__).parent
    skills_dir = script_dir.parent / 'skills'
    
    if not skills_dir.exists():
        error(f"Skills directory not found: {skills_dir}")
        return 1
    
    # Analyze all skills
    skills: list[SkillInfo] = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if skill_dir.is_dir():
            info = analyze_skill(skill_dir)
            if info:
                skills.append(info)
    
    # Group by tier
    tiers = {'pro': [], 'standard': [], 'lite': [], '[MISSING]': []}
    for skill in skills:
        tier_key = skill.tier if skill.tier in tiers else '[MISSING]'
        tiers[tier_key].append(skill)
    
    # Print report
    header("SKILL TIER AUDIT REPORT")
    
    for tier_name in ['pro', 'standard', 'lite', '[MISSING]']:
        tier_skills = tiers[tier_name]
        if not tier_skills:
            continue
        
        tier_labels = {
            'pro': '[PRO]',
            'standard': '[STD]',
            'lite': '[LITE]',
            '[MISSING]': '[WARN]'
        }
        
        tier_style = get_tier_style(tier_name)
        console.print(f"\n[{tier_style}]{tier_labels[tier_name]}[/{tier_style}] {tier_name.upper()} ({len(tier_skills)} skills)")
        console.print("-" * 40)
        
        # Create table for this tier
        table = make_table("Refs", "Scripts", "Name", "Files")
        for skill in sorted(tier_skills, key=lambda s: s.name):
            refs = 'R' if skill.has_references else '-'
            scripts = 'S' if skill.has_scripts else '-'
            table.add_row(refs, scripts, skill.name, str(skill.file_count))
        
        console.print(table)
    
    # Summary
    header("SUMMARY")
    success(f"Total Skills: {len(skills)}")
    console.print(f"[green]Pro:[/green]          {len(tiers['pro'])}")
    console.print(f"[blue]Standard:[/blue]     {len(tiers['standard'])}")
    console.print(f"[yellow]Lite:[/yellow]         {len(tiers['lite'])}")
    
    missing_count = len(tiers['[MISSING]'])
    if missing_count > 0:
        error(f"Missing:      {missing_count}")
        return 1
    
    success("OK: all skills have tier defined")
    return 0


if __name__ == '__main__':
    sys.exit(main())
