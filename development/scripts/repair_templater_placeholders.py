#!/usr/bin/env python3
"""
Bulk Repair Script for Templater Placeholders

This script scans the knowledge vault for files with unprocessed templater placeholders
and repairs them using the WorkflowManager's template processing capabilities.

Usage:
    python3 scripts/repair_templater_placeholders.py [knowledge_path] [--dry-run] [--verbose]

Examples:
    # Dry run on default knowledge directory
    python3 scripts/repair_templater_placeholders.py --dry-run
    
    # Repair all files in specific directory
    python3 scripts/repair_templater_placeholders.py /path/to/knowledge --verbose
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import re

# Add development directory to path for imports
development_dir = Path(__file__).parent.parent
sys.path.insert(0, str(development_dir / "src"))
sys.path.insert(0, str(development_dir))

from src.ai.workflow_manager import WorkflowManager
from src.utils.frontmatter import parse_frontmatter


def find_templater_placeholders(file_path: Path) -> List[str]:
    """
    Scan a file for templater placeholders in the created field.
    
    Args:
        file_path: Path to the markdown file to scan
        
    Returns:
        List of detected placeholder patterns
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for templater patterns in the raw content (before YAML parsing)
        placeholder_patterns = []
        
        # Common templater patterns
        patterns = [
            r'created:\s*{{date:.*?}}',
            r'created:\s*{{date}}',
            r'created:\s*<%\s*tp\.date\.now\(.*?\)\s*%>',
            r'created:\s*<%\s*tp\.file\.creation_date\(.*?\)\s*%>'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            placeholder_patterns.extend(matches)
        
        return placeholder_patterns
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def scan_vault_for_placeholders(vault_path: Path, verbose: bool = False) -> List[Tuple[Path, List[str]]]:
    """
    Scan entire vault for files with templater placeholders.
    
    Args:
        vault_path: Root path of the knowledge vault
        verbose: If True, print progress information
        
    Returns:
        List of tuples (file_path, list_of_placeholders)
    """
    files_with_placeholders = []
    
    # Scan all markdown files
    md_files = list(vault_path.rglob("*.md"))
    total_files = len(md_files)
    
    if verbose:
        print(f"Scanning {total_files} markdown files for templater placeholders...")
    
    for i, md_file in enumerate(md_files):
        if verbose and (i + 1) % 50 == 0:
            print(f"Progress: {i + 1}/{total_files} files scanned")
        
        placeholders = find_templater_placeholders(md_file)
        if placeholders:
            files_with_placeholders.append((md_file, placeholders))
            if verbose:
                print(f"Found placeholders in {md_file.relative_to(vault_path)}: {placeholders}")
    
    return files_with_placeholders


def repair_files(vault_path: Path, files_to_repair: List[Tuple[Path, List[str]]], 
                dry_run: bool = False, verbose: bool = False) -> Dict:
    """
    Repair files with templater placeholders using WorkflowManager.
    
    Args:
        vault_path: Root path of the knowledge vault
        files_to_repair: List of (file_path, placeholders) tuples
        dry_run: If True, don't write changes to disk
        verbose: If True, print detailed progress
        
    Returns:
        Dictionary with repair statistics
    """
    workflow = WorkflowManager(str(vault_path))
    
    stats = {
        "total_files": len(files_to_repair),
        "repaired": 0,
        "failed": 0,
        "errors": []
    }
    
    if verbose:
        print(f"{'[DRY RUN] ' if dry_run else ''}Repairing {stats['total_files']} files...")
    
    for file_path, placeholders in files_to_repair:
        try:
            if verbose:
                rel_path = file_path.relative_to(vault_path)
                print(f"Processing {rel_path}...")
            
            # Process the file using WorkflowManager
            result = workflow.process_inbox_note(str(file_path), dry_run=dry_run, fast=True)
            
            if result.get("template_fixed", False):
                stats["repaired"] += 1
                if verbose:
                    print(f"  ✅ Template placeholders fixed")
            else:
                if verbose:
                    print(f"  ⚠️  No template changes made")
            
            if result.get("file_update_error"):
                stats["failed"] += 1
                error_msg = f"{file_path}: {result['file_update_error']}"
                stats["errors"].append(error_msg)
                if verbose:
                    print(f"  ❌ Error: {result['file_update_error']}")
                    
        except Exception as e:
            stats["failed"] += 1
            error_msg = f"{file_path}: {str(e)}"
            stats["errors"].append(error_msg)
            if verbose:
                print(f"  ❌ Exception: {e}")
    
    return stats


def main():
    """Main entry point for the bulk repair script."""
    parser = argparse.ArgumentParser(
        description="Bulk repair templater placeholders in knowledge vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "vault_path", 
        nargs="?",
        default="../../knowledge",
        help="Path to knowledge vault (default: ../../knowledge)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Show what would be repaired without making changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Show detailed progress information"
    )
    
    args = parser.parse_args()
    
    # Resolve vault path
    script_dir = Path(__file__).parent
    vault_path = Path(script_dir / args.vault_path).resolve()
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Templater Placeholder Repair")
    print(f"Vault path: {vault_path}")
    print()
    
    # Scan for files with placeholders
    files_with_placeholders = scan_vault_for_placeholders(vault_path, args.verbose)
    
    if not files_with_placeholders:
        print("✅ No templater placeholders found! All files are properly formatted.")
        return
    
    print(f"Found {len(files_with_placeholders)} files with templater placeholders:")
    for file_path, placeholders in files_with_placeholders:
        rel_path = file_path.relative_to(vault_path)
        print(f"  - {rel_path}: {len(placeholders)} placeholder(s)")
    
    print()
    
    if args.dry_run:
        print("DRY RUN: Would repair the above files. Use without --dry-run to apply changes.")
        return
    
    # Confirm before proceeding
    response = input("Proceed with repairs? [y/N]: ").strip().lower()
    if response not in ('y', 'yes'):
        print("Aborted.")
        return
    
    # Perform repairs
    print()
    stats = repair_files(vault_path, files_with_placeholders, args.dry_run, args.verbose)
    
    # Print summary
    print()
    print("=== REPAIR SUMMARY ===")
    print(f"Total files processed: {stats['total_files']}")
    print(f"Successfully repaired: {stats['repaired']}")
    print(f"Failed: {stats['failed']}")
    
    if stats['errors']:
        print("\nErrors:")
        for error in stats['errors']:
            print(f"  ❌ {error}")
    
    if stats['repaired'] > 0:
        print(f"\n✅ Successfully repaired {stats['repaired']} files!")
    
    if stats['failed'] > 0:
        print(f"\n⚠️  {stats['failed']} files had errors. Please review manually.")


if __name__ == "__main__":
    main()
