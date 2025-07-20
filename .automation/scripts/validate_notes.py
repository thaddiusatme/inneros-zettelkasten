#!/usr/bin/env python3
"""
InnerOS Note Validation CLI Tool

A command-line tool for validating metadata in markdown notes.
This tool provides a user-friendly interface for running the validation script
on individual files, directories, or the entire InnerOS system.

Usage:
    python validate_notes.py [options] [path]

Options:
    --all           Validate all markdown files in the InnerOS system
    --dir           Validate all markdown files in the specified directory
    --fix           Generate suggestions for fixing validation issues (non-destructive)
    --help          Show this help message and exit

Examples:
    python validate_notes.py path/to/note.md
    python validate_notes.py --dir "Permanent Notes"
    python validate_notes.py --all
    python validate_notes.py --fix path/to/note.md
"""

import os
import sys
import argparse
import glob
from typing import List, Dict, Optional, Tuple
from validate_metadata import extract_frontmatter, parse_frontmatter, validate_metadata

# Get the root directory of the InnerOS system
def get_inneros_root() -> str:
    """Get the root directory of the InnerOS system."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    automation_dir = os.path.dirname(script_dir)
    return os.path.dirname(automation_dir)

def validate_file(file_path: str, fix: bool = False) -> bool:
    """Validate a single markdown file."""
    print(f"Validating {os.path.basename(file_path)}...")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return False
    
    # Check if file is a markdown file
    if not file_path.endswith('.md'):
        print(f"Warning: {file_path} is not a markdown file, skipping validation")
        return True
    
    # Extract frontmatter
    frontmatter = extract_frontmatter(file_path)
    if not frontmatter:
        print(f"Error: No frontmatter found in {file_path}")
        return False
    
    # Parse frontmatter
    metadata = parse_frontmatter(frontmatter)
    
    # Validate metadata
    errors = validate_metadata(metadata, file_path)
    
    if errors:
        print(f"Validation failed for {file_path}:")
        for error in errors:
            print(f"  - {error}")
        
        if fix:
            print("\nSuggested fixes:")
            suggest_fixes(file_path, metadata, errors)
        
        return False
    else:
        print(f"✅ Validation passed for {file_path}")
        return True

def suggest_fixes(file_path: str, metadata: Dict, errors: List[str]) -> None:
    """Generate suggestions for fixing validation issues."""
    for error in errors:
        if "Missing required field" in error:
            field = error.split(": ")[1]
            if field == "type":
                print(f"  - Add 'type: permanent' to the frontmatter")
            elif field == "created":
                import datetime
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                print(f"  - Add 'created: {now}' to the frontmatter")
            elif field == "status":
                print(f"  - Add 'status: draft' to the frontmatter")
            elif field == "tags":
                print(f"  - Add 'tags: [\"#tag1\", \"#tag2\"]' to the frontmatter")
        elif "Invalid type" in error:
            print(f"  - Change type to one of: permanent, fleeting, literature, MOC")
        elif "Invalid status" in error:
            print(f"  - Change status to one of: inbox, promoted, draft, published")
        elif "Invalid visibility" in error:
            print(f"  - Change visibility to one of: private, shared, team")
        elif "Invalid created date format" in error:
            print(f"  - Use format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' for created date")

def validate_directory(dir_path: str, fix: bool = False) -> Tuple[int, int]:
    """Validate all markdown files in a directory."""
    if not os.path.exists(dir_path):
        print(f"Error: Directory {dir_path} does not exist")
        return 0, 0
    
    print(f"Validating markdown files in {dir_path}...")
    
    # Get all markdown files in the directory
    md_files = glob.glob(os.path.join(dir_path, "*.md"))
    
    # Validate each file
    passed = 0
    failed = 0
    for file_path in md_files:
        if validate_file(file_path, fix):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def validate_all(fix: bool = False) -> Tuple[int, int]:
    """Validate all markdown files in the InnerOS system."""
    inneros_root = get_inneros_root()
    
    print(f"Validating all markdown files in the InnerOS system...")
    
    # Get all markdown files in the InnerOS system
    md_files = []
    for root, _, files in os.walk(inneros_root):
        # Skip .git and .automation directories
        if ".git" in root or ".automation" in root:
            continue
        
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    # Validate each file
    passed = 0
    failed = 0
    for file_path in md_files:
        if validate_file(file_path, fix):
            passed += 1
        else:
            failed += 1
    
    return passed, failed

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Validate metadata in markdown notes.")
    parser.add_argument("path", nargs="?", help="Path to a markdown file or directory")
    parser.add_argument("--all", action="store_true", help="Validate all markdown files in the InnerOS system")
    parser.add_argument("--dir", action="store_true", help="Validate all markdown files in the specified directory")
    parser.add_argument("--fix", action="store_true", help="Generate suggestions for fixing validation issues")
    
    args = parser.parse_args()
    
    # Show help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Validate all markdown files in the InnerOS system
    if args.all:
        passed, failed = validate_all(args.fix)
        print(f"\nValidation complete: {passed} passed, {failed} failed")
        sys.exit(1 if failed > 0 else 0)
    
    # Validate all markdown files in the specified directory
    if args.dir and args.path:
        passed, failed = validate_directory(args.path, args.fix)
        print(f"\nValidation complete: {passed} passed, {failed} failed")
        sys.exit(1 if failed > 0 else 0)
    
    # Validate a single markdown file
    if args.path:
        if os.path.isdir(args.path):
            if not args.dir:
                print(f"Error: {args.path} is a directory. Use --dir to validate all files in the directory.")
                sys.exit(1)
        else:
            success = validate_file(args.path, args.fix)
            sys.exit(0 if success else 1)
    
    # Show help if no valid arguments are provided
    parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
