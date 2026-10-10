"""
Code Quality Checker
Check code quality and suggest improvements
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any

class CodeQualityChecker:
    """Check code quality"""
    
    def __init__(self):
        self.issues = []
        self.project_root = Path(__file__).parent.parent
    
    def check_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check a single Python file"""
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Check for common issues
            for node in ast.walk(tree):
                # Check for print statements (should use logging)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == "print":
                        issues.append({
                            "type": "info",
                            "message": "Consider using logger instead of print",
                            "line": node.lineno
                        })
            
            # Check file length
            lines = content.split("\n")
            if len(lines) > 500:
                issues.append({
                    "type": "warning",
                    "message": f"File is long ({len(lines)} lines). Consider splitting.",
                    "line": 0
                })
            
        except SyntaxError as e:
            issues.append({
                "type": "error",
                "message": f"Syntax error: {e}",
                "line": e.lineno
            })
        except Exception as e:
            issues.append({
                "type": "error",
                "message": f"Error checking file: {e}",
                "line": 0
            })
        
        return issues
    
    def check_project(self) -> Dict[str, Any]:
        """Check entire project"""
        results = {
            "files_checked": 0,
            "total_issues": 0,
            "files": {}
        }
        
        # Check API files
        api_dir = self.project_root / "api"
        if api_dir.exists():
            for file_path in api_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    issues = self.check_file(file_path)
                    if issues:
                        results["files"][str(file_path.relative_to(self.project_root))] = issues
                        results["total_issues"] += len(issues)
                    results["files_checked"] += 1
        
        return results
    
    def print_report(self, results: Dict[str, Any]):
        """Print quality report"""
        print("=" * 60)
        print("CODE QUALITY REPORT")
        print("=" * 60)
        print()
        print(f"Files checked: {results['files_checked']}")
        print(f"Total issues: {results['total_issues']}")
        print()
        
        if results["files"]:
            print("Issues found:")
            for file, issues in results["files"].items():
                print(f"\n{file}:")
                for issue in issues[:5]:  # Show first 5
                    print(f"  [{issue['type'].upper()}] Line {issue['line']}: {issue['message']}")
        else:
            print("No issues found! Code quality is good.")

def main():
    """Run code quality check"""
    checker = CodeQualityChecker()
    results = checker.check_project()
    checker.print_report(results)

if __name__ == "__main__":
    main()

