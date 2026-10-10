"""
Changelog Generator
Track and manage project changes
"""

import json
from datetime import datetime
from typing import List, Dict, Any

class Changelog:
    """Manage project changelog"""
    
    def __init__(self):
        self.changelog_file = "CHANGELOG.md"
        self.changes_file = "changes.json"
    
    def add_entry(self, version: str, date: str, changes: List[Dict[str, str]]):
        """Add a changelog entry"""
        entry = {
            "version": version,
            "date": date,
            "changes": changes
        }
        
        # Load existing changes
        try:
            with open(self.changes_file, "r", encoding="utf-8") as f:
                all_changes = json.load(f)
        except:
            all_changes = []
        
        all_changes.insert(0, entry)
        
        # Save
        with open(self.changes_file, "w", encoding="utf-8") as f:
            json.dump(all_changes, f, indent=2, ensure_ascii=False)
        
        # Generate markdown
        self.generate_markdown()
    
    def generate_markdown(self):
        """Generate CHANGELOG.md from JSON"""
        try:
            with open(self.changes_file, "r", encoding="utf-8") as f:
                all_changes = json.load(f)
        except:
            all_changes = []
        
        markdown = "# Changelog\n\n"
        markdown += "All notable changes to this project will be documented in this file.\n\n"
        markdown += "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\n"
        markdown += "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"
        markdown += "---\n\n"
        
        for entry in all_changes:
            markdown += f"## [{entry['version']}] - {entry['date']}\n\n"
            
            # Group by type
            by_type = {}
            for change in entry['changes']:
                change_type = change.get('type', 'changed')
                if change_type not in by_type:
                    by_type[change_type] = []
                by_type[change_type].append(change)
            
            # Write by type
            type_labels = {
                'added': 'Added',
                'changed': 'Changed',
                'deprecated': 'Deprecated',
                'removed': 'Removed',
                'fixed': 'Fixed',
                'security': 'Security'
            }
            
            for change_type in ['added', 'changed', 'fixed', 'security', 'deprecated', 'removed']:
                if change_type in by_type:
                    markdown += f"### {type_labels[change_type]}\n\n"
                    for change in by_type[change_type]:
                        markdown += f"- {change['description']}\n"
                    markdown += "\n"
            
            markdown += "---\n\n"
        
        with open(self.changelog_file, "w", encoding="utf-8") as f:
            f.write(markdown)

def initialize_changelog():
    """Initialize changelog with current version"""
    changelog = Changelog()
    
    # Add current version
    changelog.add_entry(
        version="1.0.0",
        date="2025-11-05",
        changes=[
            {"type": "added", "description": "Complete API platform with 18+ endpoints"},
            {"type": "added", "description": "API key authentication system with tier-based access"},
            {"type": "added", "description": "Analytics and monitoring system"},
            {"type": "added", "description": "User dashboard for key management"},
            {"type": "added", "description": "Interactive API documentation"},
            {"type": "added", "description": "Deployment automation scripts"},
            {"type": "added", "description": "Comprehensive test suite"},
            {"type": "added", "description": "CI/CD pipeline setup"},
            {"type": "added", "description": "Response caching for performance"},
            {"type": "added", "description": "Webhook support"},
            {"type": "added", "description": "API versioning system"},
            {"type": "added", "description": "Marketing content generator"},
            {"type": "added", "description": "Integration examples for multiple languages"},
            {"type": "added", "description": "Launch preparation tools"},
            {"type": "added", "description": "Monitoring configuration"},
            {"type": "security", "description": "Production-ready security implementation"},
            {"type": "security", "description": "API key management and rate limiting"}
        ]
    )
    
    print("Changelog initialized!")
    print(f"Saved to: {changelog.changelog_file}")

if __name__ == "__main__":
    initialize_changelog()

