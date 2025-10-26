"""
Inbox Metadata Repair Engine

Detects and repairs missing frontmatter fields in Inbox notes.
Fixes notes blocked from auto-promotion due to missing 'type:' field.

TDD GREEN Phase: Minimal implementation to pass all 13 tests.
"""

import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class MetadataRepairEngine:
    """
    Detects and repairs missing frontmatter in Inbox notes.
    
    Addresses critical workflow blocker: 8 notes (21%) missing type field.
    """

    # Filename patterns for type inference
    LITERATURE_PATTERN = re.compile(r'^lit-\d{8}-\d{4}')
    FLEETING_PATTERN = re.compile(r'^(fleeting|capture|prompt)-\d{8}-\d{4}')

    # Content indicators for literature notes
    LITERATURE_INDICATORS = ['source:', 'author:', 'url:', 'published:']

    def __init__(self, inbox_dir: str, dry_run: bool = True):
        """
        Initialize metadata repair engine.
        
        Args:
            inbox_dir: Path to Inbox directory
            dry_run: If True, preview repairs without modifying files
        """
        self.inbox_dir = Path(inbox_dir)
        self.dry_run = dry_run

    def detect_missing_metadata(self, note_path: str | Path) -> List[str]:
        """
        Detect missing required frontmatter fields.
        
        Args:
            note_path: Path to note file
            
        Returns:
            List of missing field names (e.g., ['type', 'created'])
        """
        note_path = Path(note_path)
        content = note_path.read_text()

        # Check if note has frontmatter
        if not content.startswith('---'):
            # No frontmatter at all - missing both type and created
            return ['type', 'created']

        # Parse frontmatter
        missing_fields = []

        # Extract frontmatter section
        parts = content.split('---', 2)
        if len(parts) < 3:
            # Malformed frontmatter
            return ['type', 'created']

        frontmatter = parts[1]

        # Check for required fields
        if 'type:' not in frontmatter:
            missing_fields.append('type')
        if 'created:' not in frontmatter:
            missing_fields.append('created')

        return missing_fields

    def infer_note_type(self, note_path: str | Path) -> str:
        """
        Infer note type from filename pattern and content.
        
        Args:
            note_path: Path to note file
            
        Returns:
            Inferred type: 'literature', 'fleeting', or 'permanent'
        """
        note_path = Path(note_path)
        filename = note_path.name

        # Pattern-based inference (filename)
        if self.LITERATURE_PATTERN.match(filename):
            return 'literature'

        if self.FLEETING_PATTERN.match(filename):
            return 'fleeting'

        # Content-based inference for ambiguous names
        try:
            content = note_path.read_text().lower()

            # Check for literature indicators in content
            for indicator in self.LITERATURE_INDICATORS:
                if indicator in content:
                    return 'literature'
        except Exception:
            pass  # If can't read content, use default

        # Default to fleeting (safest assumption)
        return 'fleeting'

    def repair_note_metadata(self, note_path: str | Path) -> Dict:
        """
        Repair missing metadata in note.
        
        Args:
            note_path: Path to note file
            
        Returns:
            Dict with repair results:
            - 'would_add': Fields that would be added (dry-run)
            - 'added': Fields that were added (execute)
        """
        note_path = Path(note_path)
        missing_fields = self.detect_missing_metadata(str(note_path))

        if not missing_fields:
            return {'would_add': {}, 'added': {}}

        # Infer values for missing fields
        repairs = {}
        if 'type' in missing_fields:
            repairs['type'] = self.infer_note_type(str(note_path))
        if 'created' in missing_fields:
            repairs['created'] = datetime.now().strftime('%Y-%m-%d %H:%M')

        # Dry-run mode: just return what would be added
        if self.dry_run:
            return {'would_add': repairs}

        # Execute mode: actually modify the file
        self._add_frontmatter_fields(note_path, repairs)

        return {'added': repairs}

    def _add_frontmatter_fields(self, note_path: Path, fields: Dict[str, str]):
        """
        Add missing fields to note's frontmatter.
        
        Preserves existing fields and maintains frontmatter structure.
        
        Args:
            note_path: Path to note file
            fields: Dict of field_name -> value to add
        """
        content = note_path.read_text()

        # Case 1: Note has no frontmatter
        if not content.startswith('---'):
            # Create new frontmatter block
            frontmatter_lines = ['---']
            for field_name, value in fields.items():
                frontmatter_lines.append(f'{field_name}: {value}')
            frontmatter_lines.append('---')
            frontmatter_lines.append('')  # Blank line after frontmatter

            new_content = '\n'.join(frontmatter_lines) + content
            note_path.write_text(new_content)
            return

        # Case 2: Note has existing frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            # Malformed frontmatter - treat as no frontmatter
            frontmatter_lines = ['---']
            for field_name, value in fields.items():
                frontmatter_lines.append(f'{field_name}: {value}')
            frontmatter_lines.append('---')
            frontmatter_lines.append('')

            new_content = '\n'.join(frontmatter_lines) + content
            note_path.write_text(new_content)
            return

        # Parse existing frontmatter
        frontmatter = parts[1]
        body = parts[2]

        # Add missing fields to frontmatter
        frontmatter_lines = frontmatter.strip().split('\n')
        for field_name, value in fields.items():
            frontmatter_lines.append(f'{field_name}: {value}')

        # Reconstruct file content
        new_frontmatter = '\n'.join(frontmatter_lines)
        new_content = f'---\n{new_frontmatter}\n---{body}'

        note_path.write_text(new_content)
