"""
Backup System
Automated backup creation and management
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class BackupSystem:
    """Manage project backups"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.backup_index_file = self.backup_dir / "backup_index.json"
    
    def create_backup(self, name: str = None) -> str:
        """Create a backup of the project"""
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"BACKUP_{timestamp}"
        
        backup_path = self.backup_dir / name
        
        # Files/directories to backup
        items_to_backup = [
            "api",
            "dashboard",
            "docs",
            "saas_landing",
            "scripts",
            "examples",
            ".github",
            "*.md",
            "*.txt",
            "*.json",
            "*.yml",
            "*.yaml",
            "*.html",
            "*.py",
            ".gitignore"
        ]
        
        # Create backup directory
        backup_path.mkdir(exist_ok=True)
        
        # Copy files
        project_root = Path(".")
        files_copied = []
        
        for item in items_to_backup:
            source = project_root / item
            if source.exists():
                if source.is_file():
                    dest = backup_path / item
                    shutil.copy2(source, dest)
                    files_copied.append(str(item))
                elif source.is_dir():
                    dest = backup_path / item
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                    files_copied.append(str(item))
        
        # Save backup metadata
        backup_info = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "files_copied": len(files_copied),
            "path": str(backup_path)
        }
        
        # Update index
        self._update_index(backup_info)
        
        print(f"Backup created: {backup_path}")
        print(f"Files copied: {len(files_copied)}")
        
        return str(backup_path)
    
    def list_backups(self) -> List[Dict]:
        """List all backups"""
        try:
            with open(self.backup_index_file, "r") as f:
                index = json.load(f)
            return index.get("backups", [])
        except:
            return []
    
    def restore_backup(self, backup_name: str):
        """Restore from backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"Backup not found: {backup_name}")
            return False
        
        print(f"Restoring from: {backup_name}")
        print("WARNING: This will overwrite existing files!")
        
        # Restore files
        project_root = Path(".")
        for item in backup_path.iterdir():
            dest = project_root / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
        
        print("Restore complete!")
        return True
    
    def _update_index(self, backup_info: Dict):
        """Update backup index"""
        try:
            with open(self.backup_index_file, "r") as f:
                index = json.load(f)
        except:
            index = {"backups": []}
        
        index["backups"].insert(0, backup_info)
        
        # Keep only last 10 backups
        if len(index["backups"]) > 10:
            old_backups = index["backups"][10:]
            for old_backup in old_backups:
                old_path = Path(old_backup["path"])
                if old_path.exists():
                    shutil.rmtree(old_path)
            index["backups"] = index["backups"][:10]
        
        with open(self.backup_index_file, "w") as f:
            json.dump(index, f, indent=2)

def main():
    """Create backup"""
    backup_system = BackupSystem()
    backup_path = backup_system.create_backup()
    
    print("\nBackups:")
    for backup in backup_system.list_backups()[:5]:
        print(f"  - {backup['name']} ({backup['timestamp']})")

if __name__ == "__main__":
    main()

