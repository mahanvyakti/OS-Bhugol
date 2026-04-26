"""
Changelog Updater for OS-Bhugol

Automatically updates CHANGELOG.md files based on git commits.
Can be edited manually after generation.

Usage:
    python update_changelog.py

Author: mahanvyakti
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path


def get_latest_version():
    """Get latest version tag from git, or return 0.0.0 if none."""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip().lstrip('v')
    except:
        pass
    return '0.0.0'


def get_recent_commits(path='.', limit=20):
    """Get recent commits affecting a path."""
    try:
        result = subprocess.run(
            ['git', 'log', f'-{limit}', '--pretty=format:%H|%s|%ad', '--date=short', '--', path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        commits.append({
                            'hash': parts[0][:7],
                            'message': parts[1],
                            'date': parts[2]
                        })
            return commits
    except:
        pass
    return []


def categorize_commit(message):
    """Categorize commit message."""
    msg_lower = message.lower()
    if any(word in msg_lower for word in ['add', 'new', 'create']):
        return 'Added'
    elif any(word in msg_lower for word in ['fix', 'correct', 'repair']):
        return 'Fixed'
    elif any(word in msg_lower for word in ['change', 'update', 'modify', 'refactor']):
        return 'Changed'
    elif any(word in msg_lower for word in ['remove', 'delete']):
        return 'Removed'
    return 'Changed'


def update_repo_changelog():
    """Update the main repository CHANGELOG.md."""
    changelog_path = Path('CHANGELOG.md')
    today = datetime.now().strftime('%Y-%m-%d')
    version = get_latest_version()
    
    # Check if changelog exists
    if changelog_path.exists():
        with open(changelog_path, 'r', encoding='utf-8') as f:
            existing = f.read()
        if f'[{version}]' in existing:
            # Already up to date
            return
    else:
        existing = ''
    
    # Get recent commits
    commits = get_recent_commits(limit=50)
    
    # Group by category
    categories = {'Added': [], 'Changed': [], 'Fixed': [], 'Removed': []}
    for commit in commits:
        if '[skip ci]' in commit['message']:
            continue
        category = categorize_commit(commit['message'])
        categories[category].append(commit['message'])
    
    # Generate changelog content
    content = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

"""
    
    # Add categories
    for category, items in categories.items():
        if items:
            content += f"### {category}\n"
            for item in items[:10]:  # Limit to 10 per category
                content += f"- {item}\n"
            content += "\n"
    
    content += f"""## [1.0.0] - {today}

### Added
- Initial release with Parbhani Municipal Corporation ward boundaries
- 16 wards with GeoJSON and KML formats
- Source documentation with official PCMC maps
- Automated KML to GeoJSON conversion
- Validation scripts for data quality

---

*This changelog is auto-generated and can be edited manually.*
"""
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated: {changelog_path}")


def update_municipality_changelog(municipality_path):
    """Update changelog for a specific municipality."""
    changelog_path = Path(municipality_path) / 'CHANGELOG.md'
    today = datetime.now().strftime('%Y-%m-%d')
    
    content = f"""# Changelog — Parbhani Municipal Corporation

## [1.0.0] - {today}

### Added
- Initial ward boundaries (16 wards)
- Municipal corporation boundary
- Source documentation with official PCMC election maps
- Individual ward GeoJSON and KML files
- Per-ward metadata files

### Sources
- [PCMC Election 2025](https://pcmcparbhani.org/en/pcmc/election-2025)

---

*This changelog is auto-generated and can be edited manually.*
"""
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated: {changelog_path}")


def main():
    update_repo_changelog()
    
    # Find municipality directories and update their changelogs
    data_path = Path('data')
    if data_path.exists():
        for meta_file in data_path.rglob('_meta.json'):
            parent_dir = meta_file.parent
            if 'municipalities' in str(parent_dir) or 'municipal' in str(parent_dir):
                update_municipality_changelog(parent_dir)


if __name__ == '__main__':
    main()
