#!/usr/bin/env python3
"""
InnerOS Metadata Validation Script

Validates YAML frontmatter in markdown files according to the schema defined in the project manifest.
This script is non-destructive and only reports validation errors without modifying files.

Usage:
    python validate_metadata.py <path_to_markdown_file>
"""

import sys
import os
import re
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

# Load configuration
def load_config():
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config',
        'metadata_config.yaml'
    )
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Warning: Could not load config file: {e}")
        print("Using default configuration values")
        return {}

# Load configuration
config = load_config()

# Tags configuration (align with Obsidian properties by default)
TAGS_CFG = config.get('tags', {}) if isinstance(config, dict) else {}
TAGS_REQUIRE_PREFIX = bool(TAGS_CFG.get('require_prefix', False))
TAGS_ALLOWED_PREFIXES = set(TAGS_CFG.get('allow_prefixes', ['#', '@']))

# Define schema based on the configuration or use defaults
VALID_TYPES = set(config.get('valid_types', ["permanent", "fleeting", "literature", "MOC"]))
VALID_STATUSES = set(config.get('valid_statuses', ["inbox", "promoted", "draft", "published"]))
VALID_VISIBILITIES = set(config.get('valid_visibilities', ["private", "shared", "team"]))

# Required fields for all note types
REQUIRED_FIELDS = set(config.get('required_fields', ["type", "created", "status"]))

# Type-specific required fields
TYPE_SPECIFIC_FIELDS = config.get('type_specific_fields', {
    "permanent": ["tags"],
    "fleeting": ["tags"],
    "literature": ["tags"],
    "MOC": ["tags"]
})

# Convert lists to sets for faster lookups
for note_type in TYPE_SPECIFIC_FIELDS:
    if isinstance(TYPE_SPECIFIC_FIELDS[note_type], list):
        TYPE_SPECIFIC_FIELDS[note_type] = set(TYPE_SPECIFIC_FIELDS[note_type])

def extract_frontmatter(file_path: str) -> Optional[str]:
    """Extract YAML frontmatter from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Look for YAML frontmatter between --- markers
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            return frontmatter_match.group(1)
            
        # Also check for frontmatter in the form of key-value pairs without --- markers
        # This is for notes using the older template format
        metadata_match = re.search(r'^\*\*Type\*\*:.*?\*\*Created\*\*:.*?\*\*Tags\*\*:.*?\n---', content, re.DOTALL)
        if metadata_match:
            # Convert the older format to a YAML-like dictionary for validation
            metadata_text = metadata_match.group(0)
            
            # Extract type
            type_match = re.search(r'\*\*Type\*\*:\s*(.*?)\n', metadata_text)
            note_type = type_match.group(1).strip() if type_match else None
            
            # Extract created date
            created_match = re.search(r'\*\*Created\*\*:\s*(.*?)\n', metadata_text)
            created = created_match.group(1).strip() if created_match else None
            
            # Extract tags
            tags_match = re.search(r'\*\*Tags\*\*:\s*(.*?)\n', metadata_text)
            tags = tags_match.group(1).strip() if tags_match else None
            
            # Create a YAML-like string
            yaml_like = f"type: {note_type}\ncreated: {created}\ntags: {tags}\nstatus: inbox"
            return yaml_like
            
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def parse_frontmatter(frontmatter: str) -> Dict:
    """Parse YAML frontmatter into a dictionary."""
    try:
        metadata = yaml.safe_load(frontmatter)
        return metadata if metadata else {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML frontmatter: {e}")
        return {}

def validate_created_date(date_str: str) -> bool:
    """Validate the created date format."""
    date_formats = config.get("date_formats", [
        "%Y-%m-%d %H:%M",  # YYYY-MM-DD HH:MM
        "%Y-%m-%d",        # YYYY-MM-DD
    ])
    
    for date_format in date_formats:
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            continue
    
    return False

def validate_tags(tags) -> Tuple[bool, str]:
    """Validate tags format."""
    if isinstance(tags, list):
        # Check if all tags are strings
        for tag in tags:
            if not isinstance(tag, str):
                return False, f"Tag {tag} is not a string"
            # Respect configuration: only warn when prefixes are required
            if TAGS_REQUIRE_PREFIX:
                if not any(tag.startswith(p) for p in TAGS_ALLOWED_PREFIXES):
                    allowed = ", ".join(sorted(TAGS_ALLOWED_PREFIXES))
                    print(f"Warning: Tag '{tag}' should start with one of: {allowed}")
        return True, ""
    elif isinstance(tags, str):
        # For string format, check if it's a comma-separated list or space-separated list
        if ',' in tags:
            tag_list = [t.strip() for t in tags.split(',')]
        else:
            tag_list = tags.split()
            
        for tag in tag_list:
            if TAGS_REQUIRE_PREFIX:
                if not any(tag.startswith(p) for p in TAGS_ALLOWED_PREFIXES):
                    allowed = ", ".join(sorted(TAGS_ALLOWED_PREFIXES))
                    print(f"Warning: Tag '{tag}' should start with one of: {allowed}")
        return True, ""
    else:
        return False, "Tags should be a list or a string"

def validate_metadata(metadata: Dict, file_path: str) -> List[str]:
    """Validate metadata against the schema."""
    errors = []
    
    # Check for required fields
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
    
    # If type is missing, we can't do type-specific validation
    if "type" not in metadata:
        return errors
    
    # Validate type
    note_type = metadata["type"]
    if isinstance(note_type, str):
        # Extract type from string that might contain emoji and other text
        type_lower = note_type.lower()
        found_type = None
        for valid_type in VALID_TYPES:
            if valid_type in type_lower:
                found_type = valid_type
                break
        
        if not found_type:
            errors.append(f"Invalid type: {note_type}. Must be one of: {', '.join(VALID_TYPES)}")
        else:
            note_type = found_type
    else:
        errors.append(f"Type must be a string, got {type(note_type)}")
        return errors  # Can't continue type-specific validation
    
    # Validate created date
    if "created" in metadata:
        created = metadata["created"]
        if isinstance(created, str):
            if not validate_created_date(created):
                errors.append(f"Invalid created date format: {created}. Expected YYYY-MM-DD or YYYY-MM-DD HH:MM")
        else:
            errors.append(f"Created date must be a string, got {type(created)}")
    
    # Validate status
    if "status" in metadata:
        status = metadata["status"]
        if isinstance(status, str):
            if status.lower() not in VALID_STATUSES:
                errors.append(f"Invalid status: {status}. Must be one of: {', '.join(VALID_STATUSES)}")
        else:
            errors.append(f"Status must be a string, got {type(status)}")
    
    # Validate visibility if present
    if "visibility" in metadata:
        visibility = metadata["visibility"]
        if isinstance(visibility, str):
            if visibility.lower() not in VALID_VISIBILITIES:
                errors.append(f"Invalid visibility: {visibility}. Must be one of: {', '.join(VALID_VISIBILITIES)}")
        else:
            errors.append(f"Visibility must be a string, got {type(visibility)}")
    
    # Validate tags if present
    if "tags" in metadata:
        tags_valid, tags_error = validate_tags(metadata["tags"])
        if not tags_valid:
            errors.append(f"Invalid tags: {tags_error}")
    
    # Check for type-specific required fields
    if note_type in TYPE_SPECIFIC_FIELDS:
        for field in TYPE_SPECIFIC_FIELDS[note_type]:
            if field not in metadata:
                errors.append(f"Missing required field for {note_type}: {field}")
    
    return errors

def main():
    """Main function to validate a markdown file."""
    if len(sys.argv) != 2:
        print("Usage: python validate_metadata.py <path_to_markdown_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)
    
    if not file_path.endswith('.md'):
        print(f"Warning: {file_path} is not a markdown file, skipping validation")
        sys.exit(0)
    
    frontmatter = extract_frontmatter(file_path)
    if not frontmatter:
        print(f"Error: No frontmatter found in {file_path}")
        sys.exit(1)
    
    metadata = parse_frontmatter(frontmatter)
    errors = validate_metadata(metadata, file_path)
    
    if errors:
        print(f"Validation failed for {file_path}:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"Validation passed for {file_path}")
        sys.exit(0)


# Centralized templater placeholder patterns
TEMPLATER_PATTERNS = [
    r'\{\{date:[^}]+\}\}',  # {{date:YYYY-MM-DD HH:mm}}
    r'\{\{[^}]+\}\}',       # {{anything}}
    r'<%[^%]+%>',           # <% anything %>
    r'<%=[^%]+%>',          # <%= anything %>
    r'<%\*[^%]*%>',         # <%* multi-line comments %>
]

# Compiled regex for performance
TEMPLATER_REGEX = re.compile('|'.join(TEMPLATER_PATTERNS))


def has_templater_placeholders(frontmatter: Optional[str]) -> bool:
    """
    Check if frontmatter contains templater placeholder tokens.
    
    Detects:
    - {{date:...}} tokens
    - {{...}} tokens (generic)
    - <%...%> EJS-style tokens
    - <%=...%> EJS-style output tokens
    - <%*...%> EJS-style comment tokens
    
    Args:
        frontmatter: Raw frontmatter text or None
        
    Returns:
        True if templater placeholders are found, False otherwise
    """
    if not frontmatter:
        return False
    
    return bool(TEMPLATER_REGEX.search(frontmatter))


def find_templater_violations(frontmatter: str) -> List[Tuple[int, str]]:
    """
    Find all templater violations in frontmatter with line numbers.
    
    Args:
        frontmatter: Raw frontmatter text
        
    Returns:
        List of tuples (line_number, line_content) with violations
    """
    violations = []
    if not frontmatter:
        return violations
    
    lines = frontmatter.split('\n')
    for i, line in enumerate(lines, 1):
        if TEMPLATER_REGEX.search(line):
            violations.append((i, line.strip()))
    
    return violations


if __name__ == "__main__":
    main()
