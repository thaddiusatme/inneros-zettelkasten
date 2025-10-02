"""
Image Link Parser - Foundation for Image Linking System

Parses both Markdown and Wiki-style image syntax from note content.
Part of TDD Iteration 10: Image Linking System (GREEN Phase)
"""
import re
from pathlib import Path
from typing import List, Dict, Optional


class ImageLinkParser:
    """
    Regex-based parser for Markdown and Wiki image syntax.
    
    Supports:
    - Markdown: ![alt text](path/to/image.png)
    - Wiki: ![[image.png]] or ![[image.png|200]]
    """
    
    # Markdown: ![alt text](path/to/image.png)
    MARKDOWN_PATTERN = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    # Wiki: ![[image.png]] or ![[image.png|200]]
    WIKI_PATTERN = r'!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
    
    def __init__(self):
        """Initialize parser with compiled regex patterns."""
        self.markdown_regex = re.compile(self.MARKDOWN_PATTERN)
        self.wiki_regex = re.compile(self.WIKI_PATTERN)
    
    def parse_image_links(self, content: str) -> List[Dict]:
        """
        Extract all image references from content (both syntaxes).
        
        Args:
            content: Markdown note content
            
        Returns:
            List of dicts with keys:
            - type: "markdown" or "wiki"
            - alt_text: Alt text (markdown) or None (wiki)
            - path: Full path (markdown) or None (wiki)
            - filename: Filename (wiki) or extracted from path (markdown)
            - width: Width annotation (wiki with |200) or None
            - line_number: Line number where link appears
            - raw_match: Original matched string
        """
        markdown_links = self.parse_markdown_links(content)
        wiki_links = self.parse_wiki_links(content)
        
        # Combine and sort by line number
        all_links = markdown_links + wiki_links
        all_links.sort(key=lambda x: x["line_number"])
        
        return all_links
    
    def parse_markdown_links(self, content: str) -> List[Dict]:
        """
        Extract markdown-style image links: ![alt text](path/to/image.png)
        
        Args:
            content: Markdown note content
            
        Returns:
            List of markdown image link dicts
        """
        links = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            for match in self.markdown_regex.finditer(line):
                alt_text = match.group(1)
                path = match.group(2)
                filename = Path(path).name
                
                links.append({
                    "type": "markdown",
                    "alt_text": alt_text,
                    "path": path,
                    "filename": filename,
                    "width": None,
                    "line_number": line_num,
                    "raw_match": match.group(0)
                })
        
        return links
    
    def parse_wiki_links(self, content: str) -> List[Dict]:
        """
        Extract wiki-style image links: ![[image.png]] or ![[image.png|200]]
        
        Args:
            content: Markdown note content
            
        Returns:
            List of wiki image link dicts
        """
        links = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            for match in self.wiki_regex.finditer(line):
                filename = match.group(1).strip()
                width = match.group(2).strip() if match.group(2) else None
                
                links.append({
                    "type": "wiki",
                    "alt_text": None,
                    "path": None,  # Wiki links don't specify full paths
                    "filename": filename,
                    "width": width,
                    "line_number": line_num,
                    "raw_match": match.group(0)
                })
        
        return links
    
    def count_image_links(self, content: str) -> Dict[str, int]:
        """
        Count image links by type.
        
        Args:
            content: Markdown note content
            
        Returns:
            Dict with counts: {"markdown": N, "wiki": M, "total": N+M}
        """
        links = self.parse_image_links(content)
        markdown_count = sum(1 for link in links if link["type"] == "markdown")
        wiki_count = sum(1 for link in links if link["type"] == "wiki")
        
        return {
            "markdown": markdown_count,
            "wiki": wiki_count,
            "total": len(links)
        }
