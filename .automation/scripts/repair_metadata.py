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

# Import templater validator
from validate_metadata import has_templater_placeholders, find_templater_violations

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
        """Normalize date string, preserving time when present.

        Preferred outputs:
        - If input includes time: 'YYYY-MM-DD HH:%M'
        - Otherwise: 'YYYY-MM-DD'
        """
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M')
        
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
                # Preserve time precision when provided
                if fmt == '%Y-%m-%d %H:%M':
                    return date_obj.strftime('%Y-%m-%d %H:%M')
                else:
                    return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return current timestamp
        return datetime.now().strftime('%Y-%m-%d %H:%M')
    
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
        """Create properly formatted YAML frontmatter.

        Renders `tags` as an inline list (flow style) to align with Obsidian UI: `tags: [a, b]`.
        Other fields use standard block style for readability.
        """
        # Ensure proper ordering of fields (tags last)
        field_order = ['type', 'created', 'modified', 'status', 'visibility', 'tags']

        # Separate tags to control formatting
        tags_value = None
        if 'tags' in metadata:
            tags_value = metadata['tags']

        ordered_no_tags: Dict[str, Any] = {}
        for field in field_order:
            if field == 'tags':
                continue
            if field in metadata:
                ordered_no_tags[field] = metadata[field]
        # Add any remaining (non-tags) fields
        for key, value in metadata.items():
            if key not in ordered_no_tags and key != 'tags':
                ordered_no_tags[key] = value

        # Dump non-tags fields with normal YAML style
        yaml_str = yaml.dump(ordered_no_tags, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Build inline tags line if present and is a list; otherwise fall back to YAML dump for that field
        tags_line = ""
        if tags_value is not None:
            if isinstance(tags_value, list) and all(isinstance(t, str) for t in tags_value):
                # Sanitize tags to drop empties/punctuation-only tokens
                try:
                    from src.utils.tags import sanitize_tags as _sanitize
                    sanitized = _sanitize(tags_value)
                except Exception:
                    sanitized = [t for t in tags_value if isinstance(t, str) and t.strip()]

                # If no tags remain after sanitization, emit empty list
                if not sanitized:
                    tags_line = "tags: []\n"
                else:
                    def needs_quotes(s: str) -> bool:
                        # Quote if contains spaces or special YAML-significant chars
                        return bool(re.search(r"[^a-z0-9_\-:\./]", s))

                    def quote_tag(s: str) -> str:
                        if needs_quotes(s):
                            s_escaped = s.replace('"', '\\"')
                            return f'"{s_escaped}"'
                        return s

                    inline = ", ".join(quote_tag(t) for t in sanitized)
                    tags_line = f"tags: [{inline}]\n"
            else:
                # Fallback: dump via YAML if not a simple list of strings
                tags_yaml = yaml.dump({'tags': tags_value}, default_flow_style=False, allow_unicode=True, sort_keys=False)
                # Remove leading document markers if any and keep only the line(s) for tags
                tags_line = tags_yaml

        # Assemble frontmatter with tags last
        fm = "---\n" + yaml_str
        if tags_line:
            fm += tags_line
        fm += "---\n"
        return fm
    
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
                # Pre-sanitize templater placeholders in the raw frontmatter to avoid YAML parse failures
                placeholder_repairs_local: List[str] = []
                frontmatter_to_parse = frontmatter
                if "{{date:" in frontmatter:
                    try:
                        file_stat = os.stat(file_path)
                        ts = datetime.fromtimestamp(file_stat.st_mtime)
                    except (OSError, ValueError):
                        ts = datetime.now()
                    formatted_ts = ts.strftime("%Y-%m-%d %H:%M")
                    # Replace only the created line containing a templater placeholder
                    new_frontmatter = re.sub(
                        r"(?m)^(\s*created:\s*)\{\{date:[^}]+\}\s*$",
                        r"\1" + formatted_ts,
                        frontmatter,
                    )
                    if new_frontmatter != frontmatter:
                        frontmatter_to_parse = new_frontmatter
                        placeholder_repairs_local.append(
                            f"Fixed template placeholder in 'created' → {formatted_ts}"
                        )

                    # As a fallback, replace any remaining templater date tokens anywhere in YAML
                    # Example patterns: {{date:YYYY-MM-DD}} or {{date:YYYY-MM-DD HH:mm}}
                    if "{{date:" in frontmatter_to_parse:
                        new_frontmatter2 = re.sub(
                            r"\{\{date:[^}]+\}}",
                            formatted_ts,
                            frontmatter_to_parse,
                        )
                        if new_frontmatter2 != frontmatter_to_parse:
                            frontmatter_to_parse = new_frontmatter2
                            placeholder_repairs_local.append(
                                f"Replaced remaining templater date tokens in frontmatter → {formatted_ts}"
                            )

                # Parse existing (sanitized) frontmatter
                metadata = parse_frontmatter(frontmatter_to_parse)
                
                # Run a pre-template fix to capture any repairs (no-op if already sanitized)
                metadata, pre_template_repairs = self.fix_template_placeholders(metadata, file_path)
                if pre_template_repairs:
                    repairs_made.extend(pre_template_repairs)
                if placeholder_repairs_local:
                    repairs_made.extend(placeholder_repairs_local)
                
                # If any template-related changes were detected, persist them immediately
                if pre_template_repairs or placeholder_repairs_local:
                    new_frontmatter_after_template = self.create_frontmatter(metadata)
                    fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                    if fm_match:
                        content = content[:fm_match.start()] + new_frontmatter_after_template + content[fm_match.end():]
                        repairs_made.append("Applied template placeholder fixes to frontmatter")
                
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
    
    def fix_template_placeholders(self, metadata: Dict[str, Any], file_path: str) -> Tuple[Dict[str, Any], List[str]]:
        """Fix template placeholders in metadata, particularly {{date:...}} patterns.
        
        Args:
            metadata: The metadata dictionary to fix
            file_path: Path to the file for timestamp inference
            
        Returns:
            Tuple of (fixed_metadata, list_of_repairs_made)
        """
        fixed = metadata.copy()
        repairs = []
        
        # Check if 'created' field needs fixing
        created_value = metadata.get("created")
        
        # Fix template placeholders like {{date:YYYY-MM-DD HH:mm}} or missing created field
        if (created_value is None or 
            (isinstance(created_value, str) and "{{date:" in created_value)):
            
            # Try to get file creation/modification time
            try:
                file_stat = os.stat(file_path)
                # Use modification time as the best proxy for when note was created
                timestamp = datetime.fromtimestamp(file_stat.st_mtime)
            except (OSError, ValueError):
                # Fallback to current time if file operations fail
                timestamp = datetime.now()
            
            # Format in the required YYYY-MM-DD HH:MM format
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
            fixed["created"] = formatted_timestamp
            
            if created_value is None:
                repairs.append("Added missing 'created' field with file timestamp")
            else:
                repairs.append(f"Fixed template placeholder in 'created': {created_value} → {formatted_timestamp}")
        
        return fixed, repairs

    def fix_metadata(self, metadata: Dict[str, Any], errors: List[str], file_path: str, content: str) -> Dict[str, Any]:
        """Fix specific metadata issues based on validation errors."""
        fixed = metadata.copy()
        
        # First, check for and fix template placeholders
        fixed, template_repairs = self.fix_template_placeholders(fixed, file_path)
        
        for error in errors:
            if "Missing required field: " in error:
                field = error.split("Missing required field: ")[1]
                if field == 'type':
                    # Prefer 'fleeting' for Inbox or filenames starting with 'fleeting-'
                    try:
                        base = os.path.basename(file_path).lower()
                        if ('/inbox/' in file_path.lower()) or base.startswith('fleeting-'):
                            fixed['type'] = 'fleeting'
                        else:
                            fixed['type'] = 'permanent'  # Fallback default
                    except Exception:
                        fixed['type'] = 'permanent'
                elif field == 'created':
                    # Only add if not already fixed by template placeholder repair
                    if 'created' not in fixed:
                        fixed['created'] = datetime.now().strftime('%Y-%m-%d')
                elif field == 'status':
                    fixed['status'] = 'inbox'
                elif field == 'tags':
                    fixed['tags'] = []
            elif error.startswith("Missing required field for ") and ":" in error:
                # Handle type-specific missing field messages, e.g., "Missing required field for permanent: tags"
                try:
                    _, rest = error.split(" for ", 1)
                    type_and_field = rest.strip()
                    if ':' in type_and_field:
                        _, field = type_and_field.split(':', 1)
                        field = field.strip()
                        if field == 'tags':
                            fixed['tags'] = []
                except Exception:
                    pass
            
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
                # Fix date format - respect any previous template fix in 'fixed'
                if 'created' in fixed:
                    fixed['created'] = self.normalize_date(str(fixed['created']))
                elif 'created' in metadata:
                    fixed['created'] = self.normalize_date(str(metadata['created']))
            
            elif "Created date must be a string" in error:
                # Convert datetime object to string (preserve time)
                if 'created' in metadata and hasattr(metadata['created'], 'strftime'):
                    fixed['created'] = metadata['created'].strftime('%Y-%m-%d %H:%M')
                else:
                    fixed['created'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            elif "Invalid tags:" in error:
                # Fix tags format
                if 'tags' in metadata:
                    fixed['tags'] = self.normalize_tags(metadata['tags'])
            
            elif "Invalid status:" in error:
                fixed['status'] = 'inbox'  # Default
            
            elif "Invalid visibility:" in error:
                fixed['visibility'] = 'private'  # Default
            elif "Visibility must be a string" in error:
                # Coerce None/non-string to default visibility
                fixed['visibility'] = 'private'
        
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
    parser.add_argument('--validate-placeholders', action='store_true', help='Validate that no templater placeholders exist in YAML frontmatter')
    
    args = parser.parse_args()
    
    # Handle --validate-placeholders flag
    if args.validate_placeholders:
        exit_code = validate_templater_placeholders(args.path or 'knowledge')
        sys.exit(exit_code)
    
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


def validate_templater_placeholders(directory_path: str) -> int:
    """
    Scan directory for templater placeholders in YAML frontmatter.
    
    Args:
        directory_path: Path to directory to scan
        
    Returns:
        0 if no placeholders found, 1 if placeholders found
    """
    print(f"🔍 Scanning {directory_path} for templater placeholders in YAML...")
    
    if not os.path.exists(directory_path):
        print(f"❌ Error: Directory {directory_path} does not exist")
        return 1
    
    if not os.path.isdir(directory_path):
        print(f"❌ Error: {directory_path} is not a directory")
        return 1
    
    violations = []
    total_files = 0
    
    for root, dirs, files in os.walk(directory_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md') and not file.startswith('.'):
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Extract frontmatter
                    if content.startswith('---'):
                        end_idx = content.find('\n---', 4)
                        if end_idx != -1:
                            frontmatter = content[:end_idx + 4]
                            
                            if has_templater_placeholders(frontmatter):
                                # Find specific lines with placeholders for detailed reporting
                                file_violations = find_templater_violations(frontmatter)
                                for line_num, line_content in file_violations:
                                    violations.append({
                                        'file': os.path.relpath(file_path),
                                        'line': line_num,
                                        'content': line_content
                                    })
                                        
                except Exception as e:
                    print(f"⚠️  Warning: Could not read {file_path}: {e}")
    
    # Report results
    print(f"📊 Scanned {total_files} markdown files")
    
    if violations:
        print(f"\n❌ Found {len(violations)} templater placeholders in YAML:")
        for violation in violations:
            print(f"  {violation['file']}:{violation['line']} → {violation['content']}")
        
        print(f"\n💡 To fix these issues:")
        print(f"   1. Update Obsidian Templater settings (Settings → Templates)")  
        print(f"   2. Use tp.date.now(\"YYYY-MM-DD HH:mm\") syntax in templates")
        print(f"   3. Re-create notes from fixed templates")
        
        return 1
    else:
        print("✅ No templater placeholders found in YAML frontmatter")
        return 0


if __name__ == "__main__":
    main()
