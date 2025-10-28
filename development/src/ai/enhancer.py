"""
AI-powered content enhancement and note improvement suggestions.

This module provides intelligent analysis and suggestions for improving note quality,
structure, and completeness using Ollama LLM integration.
"""

import re
import json
from typing import Dict, List, Any
from .ollama_client import OllamaClient


class AIEnhancer:
    """
    AI-powered content enhancement system for zettelkasten notes.

    Provides intelligent analysis and suggestions for:
    - Note quality assessment
    - Missing content identification
    - Structural improvements
    - Link suggestions
    - Content enhancement recommendations
    """

    def __init__(
        self, model_name: str = "llama3:latest", min_quality_score: float = 0.6
    ):
        """
        Initialize the AI enhancer with Ollama client.

        Args:
            model_name: Name of the Ollama model to use
            min_quality_score: Minimum quality score threshold (0-1)
        """
        self.ollama_client = OllamaClient(config={"model": model_name})
        self.min_quality_score = min_quality_score

    def analyze_note_quality(self, content: str) -> Dict[str, Any]:
        """
        Analyze note quality and provide detailed assessment.

        Args:
            content: The note content to analyze

        Returns:
            Dictionary containing quality score, suggestions, and missing elements
        """
        if not content or not content.strip():
            return {
                "quality_score": 0.0,
                "suggestions": ["Add meaningful content to the note"],
                "missing_elements": [
                    {
                        "type": "content",
                        "description": "Note appears to be empty or minimal",
                    }
                ],
            }

        # Strip YAML frontmatter for analysis
        content_to_analyze = self._strip_yaml_frontmatter(content)

        try:
            return self._generate_ollama_analysis(content_to_analyze)
        except Exception:
            # Fallback to basic analysis if API fails
            return self._basic_quality_analysis(content_to_analyze)

    def suggest_missing_links(self, content: str) -> List[str]:
        """
        Suggest relevant internal links based on note content.

        Args:
            content: The note content to analyze

        Returns:
            List of suggested wiki-style links [[note-name]]
        """
        content_to_analyze = self._strip_yaml_frontmatter(content)

        try:
            return self._generate_link_suggestions(content_to_analyze)
        except Exception:
            # Return empty list on failure
            return []

    def identify_content_gaps(self, content: str) -> List[Dict[str, str]]:
        """
        Identify missing content sections or explanations.

        Args:
            content: The note content to analyze

        Returns:
            List of dictionaries with gap type and description
        """
        analysis = self.analyze_note_quality(content)
        return analysis.get("missing_elements", [])

    def suggest_improved_structure(self, content: str) -> Dict[str, Any]:
        """
        Suggest better note structure and organization.

        Args:
            content: The note content to analyze

        Returns:
            Dictionary with recommended structure and reasoning
        """
        content_to_analyze = self._strip_yaml_frontmatter(content)

        try:
            result = self._generate_structure_suggestions(content_to_analyze)
            # Validate structure to avoid flaky outputs from LLMs
            if not isinstance(result, dict):
                return self._basic_structure_suggestion(content_to_analyze)
            if "recommended_structure" not in result or not isinstance(
                result.get("recommended_structure"), list
            ):
                return self._basic_structure_suggestion(content_to_analyze)
            if "reasoning" not in result:
                # Provide default reasoning if missing
                result["reasoning"] = (
                    "Suggested based on standard technical note organization"
                )
            return result
        except Exception:
            # Fallback to basic structure suggestion
            return self._basic_structure_suggestion(content_to_analyze)

    def enhance_note(self, content: str) -> Dict[str, Any]:
        """
        Comprehensive note enhancement with all available suggestions.

        Args:
            content: The note content to enhance

        Returns:
            Complete enhancement report with all suggestions
        """
        quality_analysis = self.analyze_note_quality(content)
        link_suggestions = self.suggest_missing_links(content)
        structure_suggestions = self.suggest_improved_structure(content)

        return {
            "quality_score": quality_analysis["quality_score"],
            "suggestions": quality_analysis["suggestions"],
            "missing_elements": quality_analysis["missing_elements"],
            "link_suggestions": link_suggestions,
            "structure_suggestions": structure_suggestions,
            "enhanced_content": None,  # Future: could include AI-rewritten content
        }

    def _strip_yaml_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content for analysis."""
        yaml_pattern = r"^---\s*\n(.*?)\n---\s*\n"
        match = re.match(yaml_pattern, content, re.DOTALL)
        if match:
            return content[match.end() :]
        return content

    def _generate_ollama_analysis(self, content: str) -> Dict[str, Any]:
        """Generate quality analysis using Ollama LLM."""
        prompt = f"""
        Analyze this zettelkasten note for quality, completeness, and improvement opportunities.
        
        Content to analyze:
        {content}
        
        Provide a JSON response with:
        1. "quality_score": A score from 0-1 (0 = poor, 1 = excellent)
        2. "suggestions": List of specific improvement suggestions
        3. "missing_elements": List of missing content types with descriptions
        
        Consider:
        - Completeness of explanation
        - Structure and organization
        - Linking opportunities
        - Technical depth
        - Practical examples
        - Clarity and conciseness
        
        Response format:
        {{
            "quality_score": 0.85,
            "suggestions": [
                "Add practical examples",
                "Include links to related concepts",
                "Expand on technical details"
            ],
            "missing_elements": [
                {{"type": "examples", "description": "Missing concrete examples"}},
                {{"type": "links", "description": "No internal links to related notes"}}
            ]
        }}
        """

        response = self.ollama_client.generate(prompt)

        try:
            # Extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._basic_quality_analysis(content)
        except (json.JSONDecodeError, ValueError):
            return self._basic_quality_analysis(content)

    def _generate_link_suggestions(self, content: str) -> List[str]:
        """Generate link suggestions using Ollama LLM."""
        prompt = f"""
        Based on this note content, suggest relevant internal wiki-style links [[note-name]] that would improve connectivity in a zettelkasten system.
        
        Content:
        {content}
        
        Return only a JSON array of suggested links like:
        ["[[machine-learning]]", "[[neural-networks]]", "[[data-preprocessing]]"]
        
        Focus on:
        - Related technical concepts
        - Prerequisites or dependencies
        - Applications or extensions
        - Contrasting or complementary ideas
        """

        response = self.ollama_client.generate(prompt)

        try:
            # Extract JSON array from response
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            if json_match:
                links = json.loads(json_match.group())
                # Ensure proper wiki link format
                return [
                    link if link.startswith("[[") else f"[[{link}]]" for link in links
                ]
            return []
        except (json.JSONDecodeError, ValueError):
            return []

    def _generate_structure_suggestions(self, content: str) -> Dict[str, Any]:
        """Generate structure improvement suggestions using Ollama LLM."""
        prompt = f"""
        Analyze the structure and organization of this note and suggest improvements.
        
        Content:
        {content}
        
        Provide a JSON response with:
        {{
            "recommended_structure": ["Heading 1", "Heading 2", "Heading 3"],
            "reasoning": "Brief explanation of why this structure would be better"
        }}
        
        Consider:
        - Logical flow of information
        - Use of headings and sections
        - Balance between overview and detail
        - Reader-friendly organization
        """

        response = self.ollama_client.generate(prompt)

        try:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return self._basic_structure_suggestion(content)
        except (json.JSONDecodeError, ValueError):
            return self._basic_structure_suggestion(content)

    def _basic_quality_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback basic quality analysis when API fails."""
        content_lower = content.lower().strip()

        # Simple heuristics for quality assessment
        has_heading = bool(re.search(r"^#+\s+.+$", content, re.MULTILINE))
        has_sections = bool(re.search(r"^##+\s+.+$", content, re.MULTILINE))
        has_lists = bool(re.search(r"^\s*[-*+]\s+.+$", content, re.MULTILINE))
        has_links = bool(re.search(r"\[\[.+?\]\]", content))
        word_count = len(content.split())

        # Calculate basic quality score
        score = 0.0
        suggestions = []
        missing_elements = []

        if word_count > 50:
            score += 0.2
        else:
            suggestions.append("Expand the content with more detail")
            missing_elements.append(
                {"type": "content", "description": "Content appears too brief"}
            )

        if has_heading:
            score += 0.2
        else:
            suggestions.append("Add a clear main heading")
            missing_elements.append(
                {"type": "structure", "description": "Missing main heading"}
            )

        if has_sections:
            score += 0.2
        else:
            suggestions.append("Break content into logical sections")
            missing_elements.append(
                {"type": "structure", "description": "Content lacks clear sections"}
            )

        if has_lists:
            score += 0.2
        else:
            suggestions.append("Consider using bullet points for clarity")

        if has_links:
            score += 0.2
        else:
            suggestions.append("Add internal links to related notes")
            missing_elements.append(
                {"type": "links", "description": "No internal links found"}
            )

        return {
            "quality_score": min(score, 1.0),
            "suggestions": suggestions,
            "missing_elements": missing_elements,
        }

    def _basic_structure_suggestion(self, content: str) -> Dict[str, Any]:
        """Fallback basic structure suggestion when API fails."""
        return {
            "recommended_structure": [
                "# Main Topic",
                "## Overview",
                "## Key Concepts",
                "## Practical Applications",
                "## Related Notes",
                "## References",
            ],
            "reasoning": "Standard zettelkasten note structure for comprehensive coverage",
        }
