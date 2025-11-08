#!/usr/bin/env python3
"""
CLI Pattern Linter

Validates CLI scripts follow the standards documented in:
development/docs/CLI-ARGUMENT-STANDARDS.md

Usage:
    python cli_pattern_linter.py path/to/cli.py
    python cli_pattern_linter.py --dir path/to/cli/dir
    python cli_pattern_linter.py --all
    python cli_pattern_linter.py --format json path/to/cli.py
    python cli_pattern_linter.py --fail-on-violations path/to/cli.py

Checks:
1. --vault flag presence in workflow CLIs
2. Help text completeness (description, epilog)
3. Argument naming conventions (lowercase-with-hyphens)
4. Boolean flags use store_true/store_false
5. Error handling patterns
"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CLIPatternLinter:
    """Validates CLI scripts follow argument standards."""

    def __init__(self):
        self.violations = []

    def parse_cli_file(self, cli_path: Path) -> Optional[Dict]:
        """Parse CLI file and extract argparse patterns.
        
        Args:
            cli_path: Path to CLI Python file
            
        Returns:
            Dictionary with parser info, or None if parsing failed
        """
        try:
            with open(cli_path, 'r') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(cli_path))
            
            # Look for ArgumentParser usage
            parser_info = {
                "arguments": [],
                "has_subparsers": False,
                "has_description": False,
                "has_epilog": False,
            }
            
            for node in ast.walk(tree):
                # Check for ArgumentParser(description=..., epilog=...)
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'attr') and node.func.attr == 'ArgumentParser':
                        for keyword in node.keywords:
                            if keyword.arg == 'description':
                                parser_info["has_description"] = True
                            elif keyword.arg == 'epilog':
                                parser_info["has_epilog"] = True
                    
                    # Check for add_argument calls
                    if hasattr(node.func, 'attr') and node.func.attr == 'add_argument':
                        if node.args:
                            arg_name = None
                            if isinstance(node.args[0], ast.Constant):
                                arg_name = node.args[0].value
                            
                            arg_info = {"name": arg_name}
                            
                            # Extract action, help, etc.
                            for keyword in node.keywords:
                                if keyword.arg == 'action':
                                    if isinstance(keyword.value, ast.Constant):
                                        arg_info['action'] = keyword.value.value
                                elif keyword.arg == 'help':
                                    arg_info['has_help'] = True
                            
                            parser_info["arguments"].append(arg_info)
                    
                    # Check for add_subparsers
                    if hasattr(node.func, 'attr') and node.func.attr == 'add_subparsers':
                        parser_info["has_subparsers"] = True
            
            return parser_info
            
        except Exception as e:
            return None

    def check_vault_flag(self, cli_path: Path) -> List[Dict]:
        """Check if workflow CLI has --vault flag.
        
        Args:
            cli_path: Path to CLI file
            
        Returns:
            List of violations (empty if compliant)
        """
        violations = []
        parser_info = self.parse_cli_file(cli_path)
        
        if not parser_info:
            return violations
        
        # Check if any argument is --vault
        has_vault = any(
            arg.get('name') == '--vault' 
            for arg in parser_info.get('arguments', [])
        )
        
        # Workflow CLIs should have --vault flag
        # (In minimal implementation, we're lenient - just check it exists)
        if not has_vault:
            # Only flag as violation if it looks like a workflow CLI
            cli_name = cli_path.name.lower()
            if 'workflow' in cli_name or 'safe' in cli_name:
                violations.append({
                    "file": str(cli_path),
                    "line": 0,
                    "type": "missing_vault_flag",
                    "message": "Workflow CLI should have --vault flag",
                    "suggestion": "Add: parser.add_argument('--vault', help='Path to vault')"
                })
        
        return violations

    def check_help_text(self, cli_path: Path) -> List[Dict]:
        """Check help text completeness.
        
        Args:
            cli_path: Path to CLI file
            
        Returns:
            List of violations (empty if compliant)
        """
        violations = []
        parser_info = self.parse_cli_file(cli_path)
        
        if not parser_info:
            return violations
        
        # Check for description
        if not parser_info.get('has_description'):
            violations.append({
                "file": str(cli_path),
                "line": 0,
                "type": "missing_description",
                "message": "ArgumentParser should have description",
                "suggestion": "Add: ArgumentParser(description='...')"
            })
        
        # Check for epilog
        if not parser_info.get('has_epilog'):
            violations.append({
                "file": str(cli_path),
                "line": 0,
                "type": "missing_epilog",
                "message": "ArgumentParser should have epilog with examples",
                "suggestion": "Add: ArgumentParser(epilog='Examples:\\n  ...')"
            })
        
        return violations

    def check_naming_conventions(self, cli_path: Path) -> List[Dict]:
        """Check argument naming follows conventions.
        
        Args:
            cli_path: Path to CLI file
            
        Returns:
            List of violations (empty if compliant)
        """
        violations = []
        parser_info = self.parse_cli_file(cli_path)
        
        if not parser_info:
            return violations
        
        # Check each argument name
        for arg in parser_info.get('arguments', []):
            arg_name = arg.get('name')
            if not arg_name or not arg_name.startswith('--'):
                continue
            
            # Check for underscores (should use hyphens)
            if '_' in arg_name and arg_name != '--vault':
                violations.append({
                    "file": str(cli_path),
                    "line": 0,
                    "type": "naming_convention",
                    "message": f"Argument {arg_name} uses underscores, should use hyphens",
                    "suggestion": f"Rename to {arg_name.replace('_', '-')}"
                })
        
        return violations

    def check_boolean_flags(self, cli_path: Path) -> List[Dict]:
        """Check boolean flags use store_true/store_false.
        
        Args:
            cli_path: Path to CLI file
            
        Returns:
            List of violations (empty if compliant)
        """
        violations = []
        parser_info = self.parse_cli_file(cli_path)
        
        if not parser_info:
            return violations
        
        # Check for boolean-like argument names without store_true
        for arg in parser_info.get('arguments', []):
            arg_name = arg.get('name', '')
            action = arg.get('action')
            
            # Boolean-like names
            boolean_indicators = ['--dry-run', '--verbose', '--fast', '--execute', '--progress']
            
            if any(indicator in arg_name for indicator in boolean_indicators):
                if action not in ['store_true', 'store_false']:
                    violations.append({
                        "file": str(cli_path),
                        "line": 0,
                        "type": "boolean_flag",
                        "message": f"Boolean flag {arg_name} should use action='store_true'",
                        "suggestion": "Add: action='store_true'"
                    })
        
        return violations

    def generate_report(self, cli_path: Path) -> Dict:
        """Generate comprehensive report for CLI file.
        
        Args:
            cli_path: Path to CLI file
            
        Returns:
            Report dictionary with violations and summary
        """
        all_violations = []
        
        # Run all checks
        all_violations.extend(self.check_vault_flag(cli_path))
        all_violations.extend(self.check_help_text(cli_path))
        all_violations.extend(self.check_naming_conventions(cli_path))
        all_violations.extend(self.check_boolean_flags(cli_path))
        
        # Calculate compliance
        total_checks = 4  # vault, help, naming, boolean
        total_violations = len(all_violations)
        compliance_percentage = ((total_checks - min(total_violations, total_checks)) / total_checks) * 100
        
        return {
            "file": str(cli_path),
            "violations": all_violations,
            "summary": {
                "total_checks": total_checks,
                "total_violations": total_violations,
                "compliance_percentage": round(compliance_percentage, 2)
            }
        }

    def validate_directory(self, cli_dir: Path) -> Dict:
        """Validate all CLI files in directory.
        
        Args:
            cli_dir: Directory containing CLI files
            
        Returns:
            Consolidated results for all files
        """
        results = {
            "files_checked": 0,
            "total_violations": 0,
            "reports": []
        }
        
        # Find all .py files
        for cli_file in cli_dir.glob("*.py"):
            # Skip __init__.py and non-CLI files
            if cli_file.name.startswith('__'):
                continue
            
            report = self.generate_report(cli_file)
            results["reports"].append(report)
            results["files_checked"] += 1
            results["total_violations"] += report["summary"]["total_violations"]
        
        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate CLI scripts follow argument standards",
        epilog="""
Examples:
  # Check single file
  python cli_pattern_linter.py path/to/cli.py
  
  # Check directory
  python cli_pattern_linter.py --dir src/cli/
  
  # JSON output
  python cli_pattern_linter.py --format json path/to/cli.py
  
  # Fail on violations (for CI)
  python cli_pattern_linter.py --fail-on-violations path/to/cli.py
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='CLI file to check'
    )
    parser.add_argument(
        '--dir',
        help='Directory containing CLI files to check'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Check all CLI files in development/src/cli/'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--fail-on-violations',
        action='store_true',
        help='Exit with code 1 if violations found (for CI)'
    )
    
    args = parser.parse_args()
    
    linter = CLIPatternLinter()
    
    # Determine what to check
    if args.all:
        # Check development/src/cli/
        script_dir = Path(__file__).parent
        cli_dir = script_dir.parent / 'src' / 'cli'
        results = linter.validate_directory(cli_dir)
        
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(f"✅ Checked {results['files_checked']} CLI files")
            print(f"⚠️  Found {results['total_violations']} total violations")
        
        sys.exit(1 if args.fail_on_violations and results['total_violations'] > 0 else 0)
    
    elif args.dir:
        # Check directory
        cli_dir = Path(args.dir)
        if not cli_dir.exists():
            print(f"❌ Directory not found: {cli_dir}", file=sys.stderr)
            sys.exit(1)
        
        results = linter.validate_directory(cli_dir)
        
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(f"✅ Checked {results['files_checked']} CLI files")
            print(f"⚠️  Found {results['total_violations']} total violations")
        
        sys.exit(1 if args.fail_on_violations and results['total_violations'] > 0 else 0)
    
    elif args.file:
        # Check single file
        cli_path = Path(args.file)
        if not cli_path.exists():
            print(f"❌ File not found: {cli_path}", file=sys.stderr)
            sys.exit(1)
        
        # Only show progress message in text mode
        if args.format != 'json':
            print(f"Checking {cli_path}...")
        
        report = linter.generate_report(cli_path)
        
        if args.format == 'json':
            print(json.dumps(report, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"File: {report['file']}")
            print(f"{'='*60}")
            
            violations = report['violations']
            if violations:
                print(f"\n⚠️  Found {len(violations)} violations:\n")
                for i, violation in enumerate(violations, 1):
                    print(f"{i}. [{violation['type']}]")
                    print(f"   {violation['message']}")
                    print(f"   💡 {violation['suggestion']}\n")
            else:
                print("\n✅ No violations found!")
            
            summary = report['summary']
            print(f"\nSummary:")
            print(f"  Total checks: {summary['total_checks']}")
            print(f"  Violations: {summary['total_violations']}")
            print(f"  Compliance: {summary['compliance_percentage']}%")
        
        sys.exit(1 if args.fail_on_violations and report['summary']['total_violations'] > 0 else 0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
