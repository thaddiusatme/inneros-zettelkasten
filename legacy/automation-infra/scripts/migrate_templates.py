#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Template Migration Script

Description:
This script migrates legacy Obsidian templates to a standardized YAML frontmatter format.
It preserves Templater script blocks while converting custom metadata formats to a valid schema.

Features:
- Parses legacy templates to separate Templater scripts, metadata, and content.
- Extracts key-value pairs from custom markdown formats.
- Generates standardized YAML frontmatter.
- Preserves original Templater functionality.
- Creates timestamped backups of original templates before modification.
- Supports a dry-run mode to preview changes without applying them.
- Logs all operations for review.

Usage:
python3 migrate_templates.py [options]

Options:
  --dry-run     Preview changes without modifying files.
  --help        Show this help message.
"""

import argparse
import os
import sys

# Add the parent directory of 'scripts' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.template_migrator import TemplateMigrator

# Constants
TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Templates'))
BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backups'))

def main():
    """Main function to drive the template migration process."""
    parser = argparse.ArgumentParser(description="Migrate legacy Obsidian templates to standardized YAML frontmatter.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files.")
    args = parser.parse_args()

    print("Starting template migration...")
    print(f"Templates directory: {TEMPLATES_DIR}")
    print(f"Dry run mode: {'Enabled' if args.dry_run else 'Disabled'}")

    if not os.path.isdir(TEMPLATES_DIR):
        print(f"Error: Templates directory not found at '{TEMPLATES_DIR}'")
        sys.exit(1)

    migrator = TemplateMigrator(TEMPLATES_DIR, BACKUP_DIR, dry_run=args.dry_run)
    migrator.run()

    print("\nMigration process completed.")
    print(f"- Total templates processed: {migrator.processed_count}")
    print(f"- Templates successfully migrated: {migrator.migrated_count}")
    print(f"- Templates skipped (already compliant): {migrator.skipped_count}")
    if migrator.errors:
        print(f"- Errors encountered: {len(migrator.errors)}")
        for error in migrator.errors:
            print(f"  - {error}")

if __name__ == "__main__":
    main()
