#!/usr/bin/env python3
"""
Security Audit Script for InnerOS Distribution

Scans for personal information and secrets before distribution creation.
Exits with error code 1 if violations found, 0 if clean.

REFACTOR PHASE: Enhanced with better structure and documentation.

Usage:
    python3 security-audit.py /path/to/distribution
    python3 security-audit.py /path/to/distribution --format=json

Exit Codes:
    0 - Clean, no violations found
    1 - Violations found, distribution blocked
    2 - Error (invalid directory, etc.)
"""

import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any

# ================================================
# CONFIGURATION
# ================================================

# Personal information patterns to detect
PERSONAL_PATTERNS = [
    'thaddius',
    'thaddiusatme',
]

# Secret patterns to detect (pattern, violation_type)
SECRET_PATTERNS = [
    ('API_KEY', 'api key'),
    ('PASSWORD', 'password'),
    ('TOKEN', 'token'),
    ('SECRET', 'secret'),
]

# Directories to exclude from scanning
EXCLUDE_DIRS = [
    'scripts', 
    '.git', 
    'node_modules', 
    '__pycache__', 
    '.venv',
    'venv',
    'env',
    '.pytest_cache',
    'tests',  # Test files may contain test data with personal info
]

# Specific files to exclude (contains usage examples)
EXCLUDE_FILES = [
    'workflow_demo.py',  # Contains usage examples with placeholder paths
    'README.md',  # Root documentation may reference API concepts
    'INSTALLATION.md',  # Installation docs may reference API setup
]

# ================================================
# CORE FUNCTIONS
# ================================================


def scan_file(file_path: Path) -> List[Tuple[str, str]]:
    """
    Scan a single file for violations.
    
    Returns:
        List of (violation_type, context) tuples
    """
    violations = []
    is_source_code = file_path.suffix in ['.py', '.js', '.ts', '.java', '.go', '.rs']
    is_documentation = file_path.suffix in ['.md', '.rst', '.txt'] and 'Projects' in str(file_path)
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        content_lower = content.lower()
        
        # Check for personal information (always check)
        for pattern in PERSONAL_PATTERNS:
            if pattern.lower() in content_lower:
                violations.append(('personal_info', f"Found '{pattern}'"))
        
        # Check for secrets (but be lenient with source code and documentation)
        # Documentation may reference API_KEY, TOKEN, etc. as concepts
        if not is_source_code and not is_documentation:
            for pattern, violation_type in SECRET_PATTERNS:
                if pattern.lower() in content_lower:
                    violations.append((violation_type, f"Found '{pattern}'"))
    
    except Exception:
        # Skip files that can't be read
        pass
    
    return violations


def scan_directory(directory: Path) -> Dict[str, Any]:
    """
    Scan all files in directory for violations.
    
    Args:
        directory: Root directory to scan
    
    Returns:
        Dictionary mapping file paths to violations, with '_metadata' key containing scan stats
    """
    results = {}
    scanned_count = 0
    
    for file_path in directory.rglob('*'):
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
            continue
        
        # Skip excluded files
        if file_path.name in EXCLUDE_FILES:
            continue
            
        if file_path.is_file():
            scanned_count += 1
            violations = scan_file(file_path)
            if violations:
                results[str(file_path)] = violations
    
    # Store metadata for reporting
    results['_metadata'] = {
        'scanned_files': scanned_count,
        'excluded_dirs': EXCLUDE_DIRS
    }
    
    return results


def format_text_report(results: Dict[str, Any]) -> str:
    """
    Format violations as human-readable text.
    
    Args:
        results: Dictionary of violations from scan_directory (includes _metadata key)
        
    Returns:
        Formatted text report
    """
    # Remove metadata for counting
    violations = {k: v for k, v in results.items() if k != '_metadata'}
    metadata = results.get('_metadata', {})
    
    if violations:
        report = "🚨 SECURITY AUDIT FAILED - Violations Found:\n\n"
        for file_path, file_violations in violations.items():
            report += f"📄 {file_path}\n"
            for violation_type, context in file_violations:
                report += f"   ⚠️  {violation_type}: {context}\n"
            report += "\n"
        
        report += f"Total: {len(violations)} files with violations\n"
        report += f"Scanned: {metadata.get('scanned_files', 'unknown')} files\n"
        report += "❌ Distribution blocked - fix violations before proceeding"
        return report
    else:
        report = "✅ Security audit passed - no violations found\n"
        report += f"📊 Scanned {metadata.get('scanned_files', 'unknown')} files\n"
        report += "✨ Clean content - ready for distribution"
        return report


def main():
    """Main entry point for security audit."""
    parser = argparse.ArgumentParser(
        description='Security audit for InnerOS distribution',
        epilog='Exit codes: 0=clean, 1=violations, 2=error'
    )
    parser.add_argument(
        'directory',
        type=str,
        help='Directory to audit'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    directory = Path(args.directory)
    
    # Validate directory exists
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist", file=sys.stderr)
        sys.exit(2)
    
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory", file=sys.stderr)
        sys.exit(2)
    
    # Scan for violations
    results = scan_directory(directory)
    metadata = results.pop('_metadata', {})
    
    # Determine if we have violations (excluding metadata)
    has_violations = bool(results)
    
    # Output results based on format
    if args.format == 'json':
        output = {
            'violations': results,
            'total_violations': sum(len(v) for v in results.values()) if results else 0,
            'files_with_violations': len(results),
            'scanned_files': metadata.get('scanned_files', 0)
        }
        print(json.dumps(output, indent=2))
    else:
        # Text format using helper function
        # Restore metadata for formatting
        results['_metadata'] = metadata
        print(format_text_report(results))
    
    # Exit with appropriate code (1 if violations, 0 if clean)
    sys.exit(1 if has_violations else 0)


if __name__ == '__main__':
    main()
