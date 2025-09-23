#!/usr/bin/env python3
"""
Zettelkasten Capture Utilities
Enhanced utilities for Zettelkasten-optimized knowledge capture
"""

from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from typing import Dict, List, Optional, Any
import tempfile


class ZettelkastenCaptureEnhancer:
    """Enhanced capture processing optimized for Zettelkasten methodology"""
    
    def __init__(self, inbox_dir: Optional[str] = None):
        """Initialize Zettelkasten capture enhancer
        
        Args:
            inbox_dir: Directory for saving capture notes
        """
        self.inbox_dir = inbox_dir or "/tmp/zettelkasten_captures"
        Path(self.inbox_dir).mkdir(parents=True, exist_ok=True)
    
    def create_clickable_file_link(self, file_path: str, link_text: str = "Open File") -> str:
        """Create a clickable file:// link with proper URL encoding
        
        Args:
            file_path: Path to the file
            link_text: Display text for the link
            
        Returns:
            Markdown-formatted clickable link
        """
        encoded_path = quote(file_path)
        return f"[{link_text}](file://{encoded_path})"
    
    def create_finder_link(self, file_path: str, link_text: str = "Show in Finder") -> str:
        """Create a clickable link to show file in Finder/Explorer
        
        Args:
            file_path: Path to the file
            link_text: Display text for the link
            
        Returns:
            Markdown-formatted directory link
        """
        dir_path = str(Path(file_path).parent)
        encoded_dir = quote(dir_path)
        return f"[{link_text}](file://{encoded_dir}/)"
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format
        
        Args:
            size_bytes: File size in bytes
            
        Returns:
            Formatted size string (e.g., "1.2 MB", "543.7 KB")
        """
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes} bytes"
    
    def generate_zettelkasten_yaml(
        self, 
        timestamp: datetime, 
        capture_type: str = "screenshot_only",
        additional_fields: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate Zettelkasten-optimized YAML frontmatter
        
        Args:
            timestamp: Creation timestamp
            capture_type: Type of capture (screenshot_only, paired, etc.)
            additional_fields: Additional YAML fields to include
            
        Returns:
            YAML frontmatter string
        """
        yaml_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
        
        yaml_fields = {
            "type": "fleeting",
            "created": yaml_timestamp,
            "status": "inbox",
            "tags": [
                "capture",
                "samsung-s23",
                capture_type
            ],
            "source": "capture",
            "device": "Samsung S23",
            "capture_type": capture_type
        }
        
        # Add additional fields if provided
        if additional_fields:
            yaml_fields.update(additional_fields)
        
        # Generate YAML string
        yaml_lines = ["---"]
        
        for key, value in yaml_fields.items():
            if isinstance(value, list):
                yaml_lines.append(f"{key}:")
                for item in value:
                    yaml_lines.append(f"  - {item}")
            else:
                yaml_lines.append(f"{key}: {value}")
        
        yaml_lines.append("---")
        return "\n".join(yaml_lines)
    
    def create_enhanced_screenshot_section(
        self, 
        screenshot_data: Dict[str, Any], 
        include_clickable_links: bool = True
    ) -> str:
        """Create enhanced screenshot section with clickable links
        
        Args:
            screenshot_data: Screenshot metadata
            include_clickable_links: Whether to include clickable links
            
        Returns:
            Formatted screenshot section
        """
        file_path = screenshot_data.get('path', 'N/A')
        size_str = self.format_file_size(screenshot_data.get('size', 0))
        
        section = f"""## Screenshot Reference

- **File**: {screenshot_data['filename']}
- **Size**: {size_str}
- **Timestamp**: {screenshot_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
- **Path**: `{file_path}`"""
        
        if include_clickable_links and file_path != 'N/A':
            screenshot_link = self.create_clickable_file_link(file_path, "📸 Open Screenshot")
            finder_link = self.create_finder_link(file_path, "📂 Show in Finder")
            section += f"\n- **Actions**: {screenshot_link} | {finder_link}"
        
        return section
    
    def create_voice_section(
        self, 
        voice_data: Optional[Dict[str, Any]] = None, 
        include_clickable_links: bool = True
    ) -> str:
        """Create voice note section (with or without actual voice data)
        
        Args:
            voice_data: Voice note metadata (None if no voice note)
            include_clickable_links: Whether to include clickable links
            
        Returns:
            Formatted voice section
        """
        if not voice_data:
            return """## Voice Note Reference

- **Status**: No matching voice note found within 2-minute window
- **Note**: Voice notes must be recorded within 2 minutes of screenshot for automatic pairing
- **Tip**: Use the 3-A Formula (Atomic, Associate, Advance) for optimal voice content"""
        
        file_path = voice_data.get('path', 'N/A')
        size_str = self.format_file_size(voice_data.get('size', 0))
        
        section = f"""## Voice Note Reference

- **File**: {voice_data['filename']}
- **Size**: {size_str}
- **Timestamp**: {voice_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
- **Path**: `{file_path}`"""
        
        if include_clickable_links and file_path != 'N/A':
            voice_link = self.create_clickable_file_link(file_path, "🎤 Play Voice Note")
            finder_link = self.create_finder_link(file_path, "📂 Show in Finder")
            section += f"\n- **Actions**: {voice_link} | {finder_link}"
        
        return section
    
    def create_zettelkasten_processing_section(self) -> str:
        """Create Zettelkasten-specific processing section
        
        Returns:
            Formatted processing section with Zettelkasten methodology
        """
        return """## Zettelkasten Processing

*Apply the 3-A Formula for optimal knowledge development*

### Atomic Concept Extraction
- [ ] Identify the single, core idea in this capture
- [ ] Extract the atomic concept that could become a permanent note
- [ ] Define the concept clearly and concisely

### Association & Connection
- [ ] How does this connect to existing notes in my system?
- [ ] What relationships exist (builds on, contradicts, bridges, examples)?
- [ ] Which specific notes should this link to?
- [ ] What patterns or themes does this contribute to?

### Advancement & Development
- [ ] How does this advance my thinking on related topics?
- [ ] What questions does this raise for further investigation?
- [ ] Is this ready for promotion to permanent note?
- [ ] What additional development does this concept need?

### Context & Synthesis
- [ ] What was the original context when I captured this?
- [ ] What is my personal interpretation or insight?
- [ ] How does this challenge or support my existing models?
- [ ] What are the implications for my broader understanding?"""
    
    def add_ai_enhancements_to_content(
        self, 
        content: str, 
        ai_result: Dict[str, Any]
    ) -> str:
        """Add AI processing results to capture note content
        
        Args:
            content: Original markdown content
            ai_result: AI processing results
            
        Returns:
            Enhanced content with AI metadata and suggestions
        """
        lines = content.split('\n')
        yaml_end = -1
        
        # Find end of YAML frontmatter
        for i, line in enumerate(lines):
            if line.strip() == '---' and i > 0:
                yaml_end = i
                break
        
        if yaml_end > 0:
            # Insert AI metadata before closing ---
            ai_metadata = [
                f"ai_quality_score: {ai_result.get('quality_score', 'N/A')}",
                f"ai_processing_method: {ai_result.get('processing_method', 'unknown')}",
                f"ai_processed_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "ai_tags:",
            ]
            
            # Add AI tags
            for tag in ai_result.get('ai_tags', []):
                ai_metadata.append(f"  - {tag}")
            
            # Insert AI metadata
            enhanced_lines = lines[:yaml_end] + ai_metadata + lines[yaml_end:]
            content = '\n'.join(enhanced_lines)
        
        # Add AI recommendations section
        recommendations = ai_result.get('recommendations', [])
        if recommendations:
            content += "\n\n## AI Enhancement Suggestions\n\n"
            content += "*Based on AI analysis of your capture content*\n\n"
            
            for i, rec in enumerate(recommendations, 1):
                content += f"{i}. {rec}\n"
            
            # Add Zettelkasten-specific AI insights
            quality_score = ai_result.get('quality_score', 0)
            if quality_score >= 0.7:
                content += f"\n**Promotion Readiness**: High quality score ({quality_score:.2f}) - ready for permanent note development\n"
            elif quality_score >= 0.4:
                content += f"\n**Development Needed**: Medium quality score ({quality_score:.2f}) - needs more examples or connections\n"
            else:
                content += f"\n**Enhancement Required**: Low quality score ({quality_score:.2f}) - requires significant development\n"
        
        return content
    
    def save_enhanced_capture_note(
        self, 
        content: str, 
        filename: str, 
        ai_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """Save enhanced capture note to file system
        
        Args:
            content: Markdown content
            filename: Target filename
            ai_result: Optional AI processing results
            
        Returns:
            Path to saved file
        """
        # Enhance with AI results if available
        if ai_result:
            content = self.add_ai_enhancements_to_content(content, ai_result)
        
        # Determine file path
        file_path = Path(self.inbox_dir) / filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    def create_complete_zettelkasten_capture(
        self, 
        screenshot_data: Dict[str, Any],
        voice_data: Optional[Dict[str, Any]] = None,
        description: str = "knowledge-capture",
        ai_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Create a complete Zettelkasten-optimized capture note
        
        Args:
            screenshot_data: Screenshot metadata
            voice_data: Optional voice note metadata
            description: Description for filename generation
            ai_result: Optional AI processing results
            
        Returns:
            Dict with filename, file_path, and markdown_content
        """
        timestamp = screenshot_data['timestamp']
        date_str = timestamp.strftime("%Y%m%d-%H%M")
        clean_desc = description.replace(' ', '-').lower()
        filename = f"capture-{date_str}-{clean_desc}.md"
        
        # Generate YAML frontmatter
        capture_type = "paired" if voice_data else "screenshot_only"
        additional_fields = {}
        
        if voice_data:
            time_gap = abs((voice_data['timestamp'] - screenshot_data['timestamp']).total_seconds())
            additional_fields['time_gap_seconds'] = int(time_gap)
        
        yaml_content = self.generate_zettelkasten_yaml(
            timestamp, 
            capture_type, 
            additional_fields
        )
        
        # Generate content sections
        title = "# Screenshot + Voice Capture" if voice_data else "# Screenshot Capture"
        subtitle = "Knowledge capture from Samsung S23 screenshot and voice note pair." if voice_data else "Knowledge capture from Samsung S23 screenshot."
        
        screenshot_section = self.create_enhanced_screenshot_section(screenshot_data)
        voice_section = self.create_voice_section(voice_data)
        
        # Metadata section
        metadata_section = f"""## Capture Metadata

- **Device**: Samsung S23 (detected from filename patterns)
- **Capture Session**: {timestamp.strftime('%Y-%m-%d %H:%M')}
- **Capture Type**: {'Screenshot + Voice Note' if voice_data else 'Screenshot only (no matching voice note within 2-minute window)'}"""
        
        if voice_data:
            time_gap = abs((voice_data['timestamp'] - screenshot_data['timestamp']).total_seconds())
            metadata_section += f"\n- **Time Gap**: {int(time_gap)} seconds between screenshot and voice note"
        
        # Combine all sections
        processing_section = self.create_zettelkasten_processing_section()
        
        markdown_content = f"""{yaml_content}
{title}

{subtitle}

{screenshot_section}

{voice_section}

{metadata_section}

{processing_section}

"""
        
        return {
            'filename': filename,
            'file_path': f"{self.inbox_dir}/{filename}",
            'markdown_content': markdown_content
        }


class ZettelkastenVoicePromptHelper:
    """Helper for Zettelkasten-optimized voice prompt processing"""
    
    @staticmethod
    def extract_zettelkasten_concepts(voice_content: str) -> Dict[str, List[str]]:
        """Extract Zettelkasten concepts from voice content
        
        Args:
            voice_content: Transcribed voice note content
            
        Returns:
            Dict with extracted concepts, connections, and questions
        """
        # This would be enhanced with NLP processing in a full implementation
        # For now, return structure for testing
        return {
            "atomic_concepts": [],
            "connections": [],
            "research_questions": [],
            "development_needs": []
        }
    
    @staticmethod
    def assess_permanence_potential(voice_content: str) -> float:
        """Assess potential for promotion to permanent note
        
        Args:
            voice_content: Transcribed voice note content
            
        Returns:
            Score from 0.0 to 1.0 indicating permanence potential
        """
        # Placeholder implementation - would use AI analysis
        return 0.75
    
    @staticmethod
    def generate_connection_suggestions(voice_content: str, existing_notes: List[str]) -> List[Dict[str, str]]:
        """Generate suggestions for connecting to existing notes
        
        Args:
            voice_content: Transcribed voice note content
            existing_notes: List of existing note titles
            
        Returns:
            List of connection suggestions with type and rationale
        """
        # Placeholder implementation
        return [
            {
                "note_title": "example-note",
                "connection_type": "builds_on",
                "rationale": "Similar concept with additional dimension"
            }
        ]
