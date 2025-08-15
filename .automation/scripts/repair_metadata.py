#!/usr/bin/env python3
"""
InnerOS Metadata Auto-Repair Script

Automatically repairs metadata issues in markdown files according to the schema defined in the project manifest.
This script creates backups before making changes and generates detailed reports of all modifications.

Usage:
    python repair_metadata.py [options] [path]

Options:
    --file          Repair a single markdown file
    --dir           Repair all markdown files in a directory
    --all           Repair all markdown files in the InnerOS system
    --dry-run       Show what would be fixed without making changes
    --no-backup     Skip creating backups (not recommended)
    --report        Generate a detailed report of all changes
"""

import os
import sys
import re
import yaml
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Import validation functions from existing script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from validate_metadata import (
    load_config, extract_frontmatter, parse_frontmatter, 
    validate_metadata, REQUIRED_FIELDS, TYPE_SPECIFIC_FIELDS,
    VALID_TYPES, VALID_STATUSES, VALID_VISIBILITIES
)

# Ensure the development package (src) is importable for centralized utilities
_script_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(os.path.dirname(_script_dir))
_dev_path = os.path.join(_repo_root, 'development')
if _dev_path not in sys.path:
    sys.path.insert(0, _dev_path)

# Centralized tag sanitizer
from src.utils.tags import sanitize_tags

class MetadataRepairer:
    """Handles automatic repair of metadata issues in markdown files."""
    
    def __init__(self, backup_dir: Optional[str] = None, dry_run: bool = False):
        self.backup_dir = backup_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'backups',
            datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        self.dry_run = dry_run
        self.report = {
            'files_processed': 0,
            'files_repaired': 0,
            'files_skipped': 0,
            'errors': [],
            'repairs': []
        }
        
        if not self.dry_run and not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def backup_file(self, file_path: str) -> str:
        """Create a backup of the file before making changes."""
        if self.dry_run:
            return ""
            
        relative_path = os.path.relpath(file_path, start=self.get_inneros_root())
        backup_path = os.path.join(self.backup_dir, relative_path)
        backup_dir = os.path.dirname(backup_path)
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def get_inneros_root(self) -> str:
        """Get the root directory of the InnerOS system."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        automation_dir = os.path.dirname(script_dir)
        return os.path.dirname(automation_dir)
    
    def extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """Extract metadata from notes using old template format."""
        metadata = {}
        
        # Extract type
        type_match = re.search(r'\*\*Type\*\*:\s*(.*?)(?:\n|$)', content)
        if type_match:
            type_text = type_match.group(1).strip()
            # Clean up type (remove emojis and extra text)
            for valid_type in VALID_TYPES:
                if valid_type.lower() in type_text.lower():
                    metadata['type'] = valid_type
                    break
        
        # Extract created date
        created_match = re.search(r'\*\*Created\*\*:\s*(.*?)(?:\n|$)', content)
        if created_match:
            created_text = created_match.group(1).strip()
            # Try to parse and normalize the date
            metadata['created'] = self.normalize_date(created_text)
        
        # Extract tags
        tags_match = re.search(r'\*\*Tags\*\*:\s*(.*?)(?:\n|$)', content)
        if tags_match:
            tags_text = tags_match.group(1).strip()
            metadata['tags'] = self.normalize_tags(tags_text)
        
        # Extract status from content if present
        status_match = re.search(r'\*\*Status\*\*:\s*(.*?)(?:\n|$)', content)
        if status_match:
            status_text = status_match.group(1).strip().lower()
            if status_text in VALID_STATUSES:
                metadata['status'] = status_text
        
        return metadata
    
    def normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format."""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Try various date formats
        date_formats = [
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%m/%d/%Y',
            '%d/%m/%Y'
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return current date
        return datetime.now().strftime('%Y-%m-%d')
    
    def normalize_tags(self, tags_input: Any) -> List[str]:
        """Normalize tags using the centralized sanitizer.

        Accepts strings or iterables and returns a deduplicated, lowercase
        list of tags without leading '#'.
        """
        return sanitize_tags(tags_input)
    
    def clean_tag(self, tag: str) -> str:
        """Deprecated: kept for backward compatibility; uses sanitize_tags."""
        cleaned = sanitize_tags([tag])
        return cleaned[0] if cleaned else ""
    
    def generate_default_metadata(self, file_path: str, existing_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate default metadata for a note."""
        metadata = existing_metadata or {}
        
        # Add missing required fields
        if 'type' not in metadata:
            # Try to infer type from file path
            file_name = os.path.basename(file_path).lower()
            if 'moc' in file_name:
                metadata['type'] = 'MOC'
            elif 'permanent' in file_path.lower():
                metadata['type'] = 'permanent'
            elif 'fleeting' in file_path.lower():
                metadata['type'] = 'fleeting'
            elif 'literature' in file_path.lower():
                metadata['type'] = 'literature'
            else:
                metadata['type'] = 'permanent'  # Default type
        
        if 'created' not in metadata:
            # Use file creation time
            try:
                stat = os.stat(file_path)
                created_time = datetime.fromtimestamp(stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_mtime)
                metadata['created'] = created_time.strftime('%Y-%m-%d')
            except:
                metadata['created'] = datetime.now().strftime('%Y-%m-%d')
        
        if 'status' not in metadata:
            metadata['status'] = 'inbox'  # Default status
        
        # Add type-specific required fields
        note_type = metadata.get('type', 'permanent')
        if note_type in TYPE_SPECIFIC_FIELDS:
            for field in TYPE_SPECIFIC_FIELDS[note_type]:
                if field not in metadata:
                    if field == 'tags':
                        metadata['tags'] = []
        
        return metadata
    
    def create_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """Create properly formatted YAML frontmatter."""
        # Ensure proper ordering of fields
        ordered_metadata = {}
        
        # Add fields in a logical order
        field_order = ['type', 'created', 'modified', 'status', 'visibility', 'tags']
        for field in field_order:
            if field in metadata:
                ordered_metadata[field] = metadata[field]
        
        # Add any remaining fields
        for key, value in metadata.items():
            if key not in ordered_metadata:
                ordered_metadata[key] = value
        
        # Convert to YAML
        yaml_str = yaml.dump(ordered_metadata, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return f"---\n{yaml_str}---\n"
    
    def repair_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Repair metadata issues in a single file."""
        self.report['files_processed'] += 1
        repairs_made = []
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Check for existing frontmatter
            frontmatter = extract_frontmatter(file_path)
            
            if frontmatter:
                # Parse existing frontmatter
                metadata = parse_frontmatter(frontmatter)
                
                # Validate and collect errors
                errors = validate_metadata(metadata, file_path)
                
                if errors:
                    # Fix the metadata
                    fixed_metadata = self.fix_metadata(metadata, errors, file_path, content)
                    
                    # Replace frontmatter
                    new_frontmatter = self.create_frontmatter(fixed_metadata)
                    
                    # Replace in content
                    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                    if frontmatter_match:
                        content = content[:frontmatter_match.start()] + new_frontmatter + content[frontmatter_match.end():]
                        repairs_made.append("Fixed existing frontmatter")
            else:
                # No frontmatter found - need to add it
                # First try to extract metadata from old format
                extracted_metadata = self.extract_metadata_from_content(content)
                
                # Generate complete metadata
                metadata = self.generate_default_metadata(file_path, extracted_metadata)
                
                # Create frontmatter
                new_frontmatter = self.create_frontmatter(metadata)
                
                # Add to beginning of file
                content = new_frontmatter + "\n" + content
                repairs_made.append("Added missing frontmatter")
                
                # Remove old-style metadata if present
                old_metadata_pattern = r'^\*\*Type\*\*:.*?\n(?:\*\*Created\*\*:.*?\n)?(?:\*\*Tags\*\*:.*?\n)?(?:---\n)?'
                content = re.sub(old_metadata_pattern, '', content, flags=re.MULTILINE)
                if content != original_content:
                    repairs_made.append("Removed old-style metadata")
            
            # Only write if changes were made
            if content != original_content:
                if not self.dry_run:
                    # Create backup
                    self.backup_file(file_path)
                    
                    # Write repaired content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.report['files_repaired'] += 1
                self.report['repairs'].append({
                    'file': file_path,
                    'repairs': repairs_made
                })
                
                return True, repairs_made
            else:
                self.report['files_skipped'] += 1
                return False, []
                
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.report['errors'].append(error_msg)
            return False, [error_msg]
    
    def fix_metadata(self, metadata: Dict[str, Any], errors: List[str], file_path: str, content: str) -> Dict[str, Any]:
        """Fix specific metadata issues based on validation errors."""
        fixed = metadata.copy()
        
        for error in errors:
            if "Missing required field: " in error:
                field = error.split("Missing required field: ")[1]
                if field == 'type':
                    fixed['type'] = 'permanent'  # Default
                elif field == 'created':
                    fixed['created'] = datetime.now().strftime('%Y-%m-%d')
                elif field == 'status':
                    fixed['status'] = 'inbox'
                elif field == 'tags':
                    fixed['tags'] = []
            
            elif "Invalid type:" in error:
                # Try to extract valid type from existing value
                current_type = str(metadata.get('type', '')).lower()
                for valid_type in VALID_TYPES:
                    if valid_type in current_type:
                        fixed['type'] = valid_type
                        break
                else:
                    fixed['type'] = 'permanent'  # Default
            
            elif "Invalid created date format:" in error:
                # Fix date format
                if 'created' in metadata:
                    fixed['created'] = self.normalize_date(str(metadata['created']))
            
            elif "Created date must be a string" in error:
                # Convert datetime object to string
                if 'created' in metadata and hasattr(metadata['created'], 'strftime'):
                    fixed['created'] = metadata['created'].strftime('%Y-%m-%d')
                else:
                    fixed['created'] = datetime.now().strftime('%Y-%m-%d')
            
            elif "Invalid tags:" in error:
                # Fix tags format
                if 'tags' in metadata:
                    fixed['tags'] = self.normalize_tags(metadata['tags'])
            
            elif "Invalid status:" in error:
                fixed['status'] = 'inbox'  # Default
            
            elif "Invalid visibility:" in error:
                fixed['visibility'] = 'private'  # Default
        
        # Add modified date
        fixed['modified'] = datetime.now().strftime('%Y-%m-%d')
        
        return fixed
    
    def generate_report(self) -> str:
        """Generate a detailed report of all repairs."""
        report_lines = [
            "# InnerOS Metadata Repair Report",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\n## Summary",
            f"- Files processed: {self.report['files_processed']}",
            f"- Files repaired: {self.report['files_repaired']}",
            f"- Files skipped: {self.report['files_skipped']}",
            f"- Errors: {len(self.report['errors'])}"
        ]
        
        if self.report['repairs']:
            report_lines.append("\n## Repairs Made")
            for repair in self.report['repairs']:
                report_lines.append(f"\n### {repair['file']}")
                for fix in repair['repairs']:
                    report_lines.append(f"- {fix}")
        
        if self.report['errors']:
            report_lines.append("\n## Errors")
            for error in self.report['errors']:
                report_lines.append(f"- {error}")
        
        if not self.dry_run:
            report_lines.append(f"\n## Backups")
            report_lines.append(f"All original files backed up to: {self.backup_dir}")
        
        return "\n".join(report_lines)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Repair metadata issues in InnerOS markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('path', nargs='?', help='Path to file or directory')
    parser.add_argument('--file', action='store_true', help='Repair a single file')
    parser.add_argument('--dir', action='store_true', help='Repair all files in a directory')
    parser.add_argument('--all', action='store_true', help='Repair all files in InnerOS')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without making changes')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backups (not recommended)')
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    # Initialize repairer
    repairer = MetadataRepairer(
        backup_dir=None if args.no_backup else None,
        dry_run=args.dry_run
    )
    
    # Determine what to repair
    if args.all:
        # Repair all files in InnerOS
        inneros_root = repairer.get_inneros_root()
        
        # Define directories to search
        search_dirs = [
            'Permanent Notes',
            'Fleeting Notes',
            'Literature Notes',
            'Projects',
            'Areas',
            'Resources'
        ]
        
        for dir_name in search_dirs:
            dir_path = os.path.join(inneros_root, dir_name)
            if os.path.exists(dir_path):
                print(f"\nProcessing directory: {dir_name}")
                for root, dirs, files in os.walk(dir_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if file.endswith('.md') and not file.startswith('.'):
                            file_path = os.path.join(root, file)
                            success, repairs = repairer.repair_file(file_path)
                            if success:
                                print(f"✅ Repaired: {os.path.relpath(file_path, inneros_root)}")
                                for repair in repairs:
                                    print(f"   - {repair}")
                            elif repairs:  # Has errors
                                print(f"❌ Error: {os.path.relpath(file_path, inneros_root)}")
                                for error in repairs:
                                    print(f"   - {error}")
    
    elif args.dir and args.path:
        # Repair all files in specified directory
        if not os.path.isdir(args.path):
            print(f"Error: {args.path} is not a directory")
            sys.exit(1)
        
        for root, dirs, files in os.walk(args.path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith('.md') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    success, repairs = repairer.repair_file(file_path)
                    if success:
                        print(f"✅ Repaired: {file}")
                        for repair in repairs:
                            print(f"   - {repair}")
    
    elif args.path:
        # Repair single file
        if not os.path.isfile(args.path):
            print(f"Error: {args.path} is not a file")
            sys.exit(1)
        
        success, repairs = repairer.repair_file(args.path)
        if success:
            print(f"✅ Repaired: {args.path}")
            for repair in repairs:
                print(f"   - {repair}")
        elif not repairs:
            print(f"ℹ️  No repairs needed for: {args.path}")
    
    else:
        parser.print_help()
        sys.exit(1)
    
    # Generate report if requested
    if args.report:
        report = repairer.generate_report()
        
        # Save report to file
        report_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'reports'
        )
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        report_path = os.path.join(
            report_dir,
            f"repair_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nReport saved to: {report_path}")
        
        # Also print summary
        print("\n" + "="*50)
        print("REPAIR SUMMARY")
        print("="*50)
        print(f"Files processed: {repairer.report['files_processed']}")
        print(f"Files repaired: {repairer.report['files_repaired']}")
        print(f"Files skipped: {repairer.report['files_skipped']}")
        print(f"Errors: {len(repairer.report['errors'])}")
        
        if args.dry_run:
            print("\n⚠️  This was a dry run - no files were actually modified")


if __name__ == "__main__":
    main()
