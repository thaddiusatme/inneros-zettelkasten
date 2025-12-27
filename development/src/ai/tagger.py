"""
AI-powered automatic tag generation for notes.
Uses local LLM to extract relevant tags from note content.
"""

from typing import List, Dict, Any, Optional, Tuple
from .ollama_client import OllamaClient
from src.utils.tags import sanitize_tags


class AITagger:
    """Generates relevant tags for notes using AI analysis."""

    def __init__(
        self, min_confidence: float = 0.7, config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize AI tagger with configuration.

        Args:
            min_confidence: Minimum confidence threshold for tag inclusion
            config: Optional configuration for Ollama client
        """
        self.ollama_client = OllamaClient(config=config)
        self.min_confidence = min_confidence

    def generate_tags(
        self, content: str, min_tags: int = 3, max_tags: int = 8
    ) -> List[str]:
        """
        Generate relevant tags for given note content.

        Args:
            content: Note content to analyze
            min_tags: Minimum number of tags to return
            max_tags: Maximum number of tags to return

        Returns:
            List of unique, relevant tags
        """
        if not content or not content.strip():
            return []

        # Strip YAML frontmatter if present
        processed_content = self._strip_yaml_frontmatter(content)
        if not processed_content.strip():
            return []

        # Use real Ollama API for tag generation
        tags = self._generate_ollama_tags(processed_content)
        tags = sanitize_tags(tags)

        # Limit to max_tags
        return tags[:max_tags]

    def _generate_ollama_tags(self, content: str) -> List[str]:
        """
        Generate tags using real Ollama API with optimized prompt engineering.

        Args:
            content: Note content to analyze

        Returns:
            List of relevant, unique tags
        """
        if not content or not content.strip():
            return []

        try:
            # Prepare the prompt for tag extraction
            system_prompt = "You are an expert at extracting relevant tags from technical and academic content. Analyze the provided text and extract 3-8 highly relevant tags that capture the key concepts, topics, and themes.\n\nGuidelines:\n- Focus on specific, meaningful concepts\n- Use kebab-case for multi-word tags (e.g., 'machine-learning', 'quantum-computing')\n- Prioritize technical accuracy over generic terms\n- Include domain-specific terminology when relevant\n- Avoid overly broad or generic tags like 'technology' unless essential\n- Return only the tags, separated by commas\n\nExample response format: 'tag1, tag2, tag3, tag4'"

            user_prompt = f"""Extract relevant tags from this content:
            
            {content}
            
            Tags:"""

            # Generate tags via Ollama
            response = self.ollama_client.generate_completion(
                prompt=user_prompt, system_prompt=system_prompt, max_tokens=100
            )

            # Parse and sanitize the response (prevents prompt artifacts from becoming tags)
            return sanitize_tags(response)

        except Exception as e:
            # Fallback to mock tags if API fails
            print(f"Warning: Ollama API failed, using fallback: {e}")
            return sanitize_tags(self._generate_mock_tags(content))

    def _strip_yaml_frontmatter(self, content: str) -> str:
        """
        Strip YAML frontmatter from note content.

        Args:
            content: Raw note content

        Returns:
            Content without YAML frontmatter
        """
        if not content:
            return content

        lines = content.split("\n")
        if len(lines) >= 3 and lines[0].strip() == "---":
            # Find the closing ---
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    # Return content after the closing ---
                    return "\n".join(lines[i + 1 :])

        return content

    def _generate_mock_tags(self, content: str) -> List[str]:
        """
        Mock tag generation for fallback when API is unavailable.
        """
        content_lower = content.lower()
        tags = []

        # Simple keyword-based tagging for fallback
        keyword_map = {
            "machine learning": ["ai", "machine-learning"],
            "artificial intelligence": ["ai"],
            "python": ["programming", "python"],
            "neural": ["ai", "neural-networks"],
            "algorithm": ["algorithms", "computer-science"],
            "data": ["data-science", "analytics"],
            "learning": ["education", "ai"],
            "programming": ["programming"],
            "development": ["programming", "software"],
            "quantum": ["quantum-computing", "physics"],
            "cryptography": ["cryptography", "security"],
            "drug discovery": ["biotech", "pharmaceuticals"],
            "optimization": ["optimization", "algorithms"],
        }

        for keyword, keyword_tags in keyword_map.items():
            if keyword in content_lower:
                tags.extend(keyword_tags)

        # Add some generic tags based on content length
        if len(content) > 200:
            tags.extend(["detailed", "comprehensive"])

        return tags[:8]  # Limit to max tags

    def generate_tags_with_confidence(self, content: str) -> List[Tuple[str, float]]:
        """
        Generate tags with confidence scores.

        Args:
            content: Note content to analyze

        Returns:
            List of (tag, confidence) tuples
        """
        if not content or not content.strip():
            return []

        # Mock implementation with confidence scores
        tags = self._generate_mock_tags(content)
        confidence_tags = [(tag, 0.9 - (i * 0.1)) for i, tag in enumerate(tags)]

        # Filter by minimum confidence
        return [
            (tag, conf) for tag, conf in confidence_tags if conf >= self.min_confidence
        ]
