"""
Image Link Manager - Core Image Link Management

Manages image link parsing, validation, and updates for directory moves.
Part of TDD Iteration 10: Image Linking System (GREEN Phase)
"""
import re
from pathlib import Path
from typing import List, Dict, Optional
import logging

from .image_link_parser import ImageLinkParser

logger = logging.getLogger(__name__)


class ImageLinkManager:
    """
    Core image link management for preservation across workflows.
    
    Features:
    - Parse both Markdown and Wiki syntax
    - Update links when notes move between directories
    - Validate image references (detect broken links)
    - Calculate relative paths automatically
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize manager.
        
        Args:
            base_path: Optional knowledge base path for absolute path resolution
        """
        self.base_path = Path(base_path) if base_path else None
        self.parser = ImageLinkParser()
    
    def parse_image_links(self, content: str) -> List[Dict]:
        """
        Extract all image references from content.
        
        Delegates to ImageLinkParser for actual parsing.
        
        Args:
            content: Markdown note content
            
        Returns:
            List of image link dicts (see ImageLinkParser.parse_image_links)
        """
        return self.parser.parse_image_links(content)
    
    def update_image_links_for_move(
        self,
        content: str,
        source_path: Path,
        dest_path: Path
    ) -> str:
        """
        Rewrite image links to work from new location.
        
        Calculates relative paths automatically to maintain correctness
        when moving between directories (e.g., Inbox/ → Fleeting Notes/).
        
        Args:
            content: Original note content
            source_path: Current note path
            dest_path: Destination note path
            
        Returns:
            Updated content with rewritten image links
        """
        # Parse all image links
        image_links = self.parse_image_links(content)
        
        if not image_links:
            logger.debug("No image links found to update")
            return content
        
        # Update content with new paths
        updated_content = content
        
        # Process in reverse order to maintain string positions
        for link in reversed(image_links):
            if link["type"] == "markdown":
                # Update markdown links with recalculated relative paths
                old_path = link["path"]
                new_path = self._recalculate_relative_path(
                    old_path, source_path, dest_path
                )
                
                # Replace the path portion only
                old_link = link["raw_match"]
                new_link = f'![{link["alt_text"]}]({new_path})'
                
                updated_content = updated_content.replace(old_link, new_link, 1)
                logger.debug(f"Updated markdown link: {old_link} → {new_link}")
            
            # Wiki links don't need path updates (they're just filenames)
            # They rely on Obsidian's auto-resolution
        
        return updated_content
    
    def validate_image_links(
        self,
        note_path: Path,
        content: str
    ) -> List[Dict]:
        """
        Detect broken image references.
        
        Args:
            note_path: Path to note file
            content: Note content to validate
            
        Returns:
            List of broken link dicts with keys:
            - note_path: Path to note with broken link
            - image_path: Referenced image path (relative or wiki)
            - line_number: Line number of broken link
            - link_type: "markdown" or "wiki"
            - exists: False (all entries are broken links)
        """
        broken_links = []
        image_links = self.parse_image_links(content)
        
        for link in image_links:
            if link["type"] == "markdown":
                # Resolve markdown path relative to note
                image_path_str = link["path"]
                
                # Calculate absolute path for validation
                if image_path_str.startswith("../"):
                    # Relative path - resolve from note's directory
                    note_dir = note_path.parent
                    image_abs_path = (note_dir / image_path_str).resolve()
                else:
                    # Absolute or same-directory path
                    image_abs_path = Path(image_path_str)
                
                # Check if image exists
                if not image_abs_path.exists():
                    broken_links.append({
                        "note_path": str(note_path),
                        "image_path": image_path_str,
                        "line_number": link["line_number"],
                        "link_type": "markdown",
                        "exists": False
                    })
            
            elif link["type"] == "wiki":
                # For wiki links, check in attachments/ directory
                # This is a simplified check - full resolution would need vault scanning
                if self.base_path:
                    attachments_dir = self.base_path / "attachments"
                    # Search for file in all month folders
                    found = False
                    if attachments_dir.exists():
                        for month_folder in attachments_dir.iterdir():
                            if month_folder.is_dir():
                                image_file = month_folder / link["filename"]
                                if image_file.exists():
                                    found = True
                                    break
                    
                    if not found:
                        broken_links.append({
                            "note_path": str(note_path),
                            "image_path": link["filename"],
                            "line_number": link["line_number"],
                            "link_type": "wiki",
                            "exists": False
                        })
        
        return broken_links
    
    def _recalculate_relative_path(
        self,
        old_relative_path: str,
        source_note_path: Path,
        dest_note_path: Path
    ) -> str:
        """
        Recalculate relative path for new note location.
        
        Args:
            old_relative_path: Original relative path from source note
            source_note_path: Original note path
            dest_note_path: New note path
            
        Returns:
            New relative path from destination note to same image
        """
        # For relative paths that point to attachments/, keep them simple
        # Most notes will be at same depth (Inbox/, Fleeting Notes/, etc)
        # so ../attachments/ will work for all
        
        if old_relative_path.startswith("../"):
            # Already a relative path - check if directories are at same depth
            source_depth = len(source_note_path.parent.parts)
            dest_depth = len(dest_note_path.parent.parts)
            
            if source_depth == dest_depth:
                # Same depth - path stays the same
                return old_relative_path
            else:
                # Different depth - adjust the number of ../
                # Count current ../ in path
                parts = old_relative_path.split("/")
                up_count = sum(1 for p in parts if p == "..")
                remaining_parts = [p for p in parts if p != ".."]
                
                # Calculate new depth difference
                depth_diff = dest_depth - source_depth
                new_up_count = up_count - depth_diff
                
                # Rebuild path
                new_up_parts = [".."] * max(1, new_up_count)
                return "/".join(new_up_parts + remaining_parts)
        else:
            # Absolute or local path - return as-is
            return old_relative_path
