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


def main() -> int:
    """Main entry point."""
    # Find skills directory
    script_dir = Path(__file__).parent
    skills_dir = script_dir.parent / 'skills'
    
    if not skills_dir.exists():
        print(f"ERROR: Skills directory not found: {skills_dir}")
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
    print("\n" + "=" * 60)
    print("SKILL TIER AUDIT REPORT")
    print("=" * 60)
    
    for tier_name in ['pro', 'standard', 'lite', '[MISSING]']:
        tier_skills = tiers[tier_name]
        if not tier_skills:
            continue
        
        label = {'pro': '[PRO]', 'standard': '[STD]', 'lite': '[LITE]', '[MISSING]': '[WARN]'}
        print(f"\n{label[tier_name]} {tier_name.upper()} ({len(tier_skills)} skills)")
        print("-" * 40)
        
        for skill in sorted(tier_skills, key=lambda s: s.name):
            refs = 'R' if skill.has_references else '-'
            scripts = 'S' if skill.has_scripts else '-'
            print(f"  {refs} {scripts} {skill.name:<30} ({skill.file_count} files)")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total Skills: {len(skills)}")
    print(f"  Pro:          {len(tiers['pro'])}")
    print(f"  Standard:     {len(tiers['standard'])}")
    print(f"  Lite:         {len(tiers['lite'])}")
    
    missing_count = len(tiers['[MISSING]'])
    if missing_count > 0:
        print(f"  Missing:      {missing_count}")
        return 1
    
    print("\nOK: all skills have tier defined")
    return 0


if __name__ == '__main__':
    sys.exit(main())
