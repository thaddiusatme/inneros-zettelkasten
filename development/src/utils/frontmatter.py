"""
Centralized frontmatter I/O utilities for InnerOS Zettelkasten.

This module provides robust, consistent YAML frontmatter parsing and building
with proper error handling and field ordering.
"""

import re
import yaml
from typing import Dict, Tuple, Any, Optional
from io import StringIO


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.
    
    Args:
        content: Raw markdown content potentially containing frontmatter
        
    Returns:
        Tuple of (metadata_dict, body_content)
        - metadata_dict: Parsed YAML frontmatter as dictionary (empty if none/invalid)
        - body_content: Remaining content after frontmatter removal
    """
    if not content or not isinstance(content, str):
        return {}, content or ""
    
    # Check for frontmatter delimiters
    if not content.strip().startswith('---'):
        return {}, content
    
    # Find closing delimiter
    lines = content.split('\n')
    if len(lines) < 2:
        return {}, content
    
    # Look for closing '---' delimiter
    closing_delimiter_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            closing_delimiter_idx = i
            break
    
    if closing_delimiter_idx is None:
        # No closing delimiter found - treat as no frontmatter
        return {}, content
    
    # Extract YAML content between delimiters
    yaml_lines = lines[1:closing_delimiter_idx]
    yaml_content = '\n'.join(yaml_lines)
    
    # Extract body content after frontmatter
    body_lines = lines[closing_delimiter_idx + 1:]
    body_content = '\n'.join(body_lines)
    
    # Parse YAML with error handling
    try:
        if not yaml_content.strip():
            metadata = {}
        else:
            metadata = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError:
        # Return empty metadata for malformed YAML, but preserve original content
        return {}, content
    
    return metadata, body_content


def build_frontmatter(metadata: Dict[str, Any], body: str) -> str:
    """
    Build markdown content with YAML frontmatter.
    
    Args:
        metadata: Dictionary of frontmatter fields
        body: Main content body
        
    Returns:
        Complete markdown content with frontmatter and body
    """
    if not metadata:
        return body
    
    # Define field ordering for consistency
    field_order = [
        'created',
        'type', 
        'status',
        'visibility',
        'tags',
        'source',
        'url',
        'saved_at',
        'claims',
        'quotes',
        'linked_notes',
        'quality_score',
        'ai_tags'
    ]
    
    # Create ordered metadata dict
    ordered_metadata = {}
    
    # Add fields in preferred order
    for field in field_order:
        if field in metadata:
            ordered_metadata[field] = metadata[field]
    
    # Add any remaining fields not in the order list
    for key, value in metadata.items():
        if key not in ordered_metadata:
            ordered_metadata[key] = value
    
    # Convert to YAML with consistent formatting
    yaml_stream = StringIO()
    yaml.dump(
        ordered_metadata,
        yaml_stream,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,  # Preserve our custom ordering
        width=80,
        indent=2
    )
    
    yaml_content = yaml_stream.getvalue()
    
    # Build complete content
    if yaml_content.strip():
        return f"---\n{yaml_content}---\n{body}"
    else:
        return body


def validate_frontmatter(metadata: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate frontmatter metadata for common issues.
    
    Args:
        metadata: Dictionary of frontmatter fields
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(metadata, dict):
        return False, "Metadata must be a dictionary"
    
    # Check required field types
    type_checks = {
        'created': str,
        'type': str,
        'status': str,
        'tags': list,
        'visibility': str
    }
    
    for field, expected_type in type_checks.items():
        if field in metadata and not isinstance(metadata[field], expected_type):
            return False, f"Field '{field}' must be of type {expected_type.__name__}"
    
    # Validate enum values
    valid_types = {'permanent', 'fleeting', 'literature', 'MOC'}
    if 'type' in metadata and metadata['type'] not in valid_types:
        return False, f"Field 'type' must be one of: {valid_types}"
    
    valid_statuses = {'inbox', 'promoted', 'draft', 'published', 'archived'}
    if 'status' in metadata and metadata['status'] not in valid_statuses:
        return False, f"Field 'status' must be one of: {valid_statuses}"
    
    valid_visibility = {'private', 'shared', 'team', 'public'}
    if 'visibility' in metadata and metadata['visibility'] not in valid_visibility:
        return False, f"Field 'visibility' must be one of: {valid_visibility}"
    
    return True, None


def update_frontmatter_field(content: str, field: str, value: Any) -> str:
    """
    Update a specific field in frontmatter content.
    
    Args:
        content: Original markdown content with frontmatter
        field: Field name to update
        value: New value for the field
        
    Returns:
        Updated content with modified frontmatter
    """
    metadata, body = parse_frontmatter(content)
    metadata[field] = value
    return build_frontmatter(metadata, body)


def remove_frontmatter_field(content: str, field: str) -> str:
    """
    Remove a specific field from frontmatter content.
    
    Args:
        content: Original markdown content with frontmatter
        field: Field name to remove
        
    Returns:
        Updated content with field removed from frontmatter
    """
    metadata, body = parse_frontmatter(content)
    if field in metadata:
        del metadata[field]
    return build_frontmatter(metadata, body)
