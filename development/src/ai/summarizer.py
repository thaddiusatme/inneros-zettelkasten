"""
AI-powered note summarization for long content.
Provides both abstractive (LLM-based) and extractive summarization.
"""

import re
from typing import List, Dict, Any, Optional
from collections import Counter
from .ollama_client import OllamaClient


class AISummarizer:
    """Generates summaries for long notes using AI analysis."""

    def __init__(self, min_length: int = 500, max_summary_ratio: float = 0.3, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI summarizer with configuration.
        
        Args:
            min_length: Minimum word count to trigger summarization
            max_summary_ratio: Maximum ratio of summary length to original length
            config: Optional configuration for Ollama client
        """
        self.ollama_client = OllamaClient(config=config)
        self.min_length = min_length
        self.max_summary_ratio = max_summary_ratio

    def should_summarize(self, content: str) -> bool:
        """
        Determine if content is long enough to warrant summarization.
        
        Args:
            content: Note content to evaluate
            
        Returns:
            bool: True if content should be summarized
        """
        if not content or not content.strip():
            return False

        processed_content = self._strip_yaml_frontmatter(content)
        word_count = self._count_words(processed_content)

        return word_count >= self.min_length

    def generate_summary(self, content: str, summary_type: str = "abstractive") -> Optional[str]:
        """
        Generate a summary for the given content.
        
        Args:
            content: Note content to summarize
            summary_type: Type of summary ("abstractive" or "extractive")
            
        Returns:
            Generated summary or None if content is too short or API fails
        """
        if not self.should_summarize(content):
            return None

        # Strip YAML frontmatter for processing
        processed_content = self._strip_yaml_frontmatter(content)

        try:
            if summary_type == "extractive":
                return self.generate_extractive_summary(content)
            else:
                return self._generate_ollama_summary(processed_content)
        except Exception:
            # Graceful fallback - return None if summarization fails
            return None

    def generate_extractive_summary(self, content: str, num_sentences: int = 3) -> Optional[str]:
        """
        Generate extractive summary by selecting key sentences.
        
        Args:
            content: Note content to summarize
            num_sentences: Number of sentences to include in summary
            
        Returns:
            Extractive summary or None if content is too short
        """
        # For extractive summaries, use a lower threshold (just need enough sentences)
        processed_content = self._strip_yaml_frontmatter(content)
        if not processed_content or not processed_content.strip():
            return None

        # Check if we have enough content for meaningful extraction
        word_count = self._count_words(processed_content)
        if word_count < 50:  # Much lower threshold for extractive
            return None
        sentences = self._split_into_sentences(processed_content)

        if len(sentences) <= num_sentences:
            return processed_content.strip()

        # Score sentences based on word frequency and position
        sentence_scores = self._score_sentences(sentences)

        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]

        # Sort selected sentences by original order
        selected_indices = sorted([sentences.index(sent) for sent, _ in top_sentences])
        summary_sentences = [sentences[i] for i in selected_indices]

        return " ".join(summary_sentences).strip()

    def _generate_ollama_summary(self, content: str) -> str:
        """
        Generate summary using Ollama API.
        
        Args:
            content: Content to summarize
            
        Returns:
            Generated summary
            
        Raises:
            Exception: If Ollama service is unavailable or API call fails
        """
        if not self.ollama_client.health_check():
            raise Exception("Ollama service is not available")

        processed_content = self._strip_yaml_frontmatter(content)
        word_count = self._count_words(processed_content)
        target_length = max(50, int(word_count * self.max_summary_ratio))

        system_prompt = f"""You are an expert at creating concise, informative summaries of academic and technical content.

Your task is to create a summary of approximately {target_length} words that:
1. Captures the main ideas and key points
2. Maintains the original tone and style
3. Preserves important technical terms and concepts
4. Is coherent and well-structured
5. Focuses on the most valuable information

Please provide only the summary without any additional commentary or formatting."""

        user_prompt = f"Please summarize the following content:\n\n{processed_content}"

        try:
            summary = self.ollama_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            return summary.strip()
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    def _strip_yaml_frontmatter(self, content: str) -> str:
        """
        Remove YAML frontmatter from content.
        
        Args:
            content: Content that may contain YAML frontmatter
            
        Returns:
            Content without YAML frontmatter
        """
        # Pattern to match YAML frontmatter
        yaml_pattern = r'^---\s*\n.*?\n---\s*\n'
        return re.sub(yaml_pattern, '', content, flags=re.DOTALL).strip()

    def _count_words(self, text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words
        """
        if not text or not text.strip():
            return 0
        return len(text.split())

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on periods, exclamation marks, and question marks
        # followed by whitespace or end of string
        sentence_pattern = r'[.!?]+\s+'
        sentences = re.split(sentence_pattern, text)

        # Clean up and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _score_sentences(self, sentences: List[str]) -> Dict[str, float]:
        """
        Score sentences based on word frequency and position.
        
        Args:
            sentences: List of sentences to score
            
        Returns:
            Dictionary mapping sentences to scores
        """
        # Calculate word frequencies
        all_words = []
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            all_words.extend(words)

        word_freq = Counter(all_words)

        # Score each sentence
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = re.findall(r'\b\w+\b', sentence.lower())

            if not words:
                sentence_scores[sentence] = 0.0
                continue

            # Base score from word frequencies
            word_score = sum(word_freq[word] for word in words) / len(words)

            # Position bonus (earlier sentences get slight boost)
            position_bonus = 1.0 - (i / len(sentences)) * 0.2

            # Length penalty for very short or very long sentences
            length_penalty = 1.0
            if len(words) < 5:
                length_penalty = 0.5
            elif len(words) > 30:
                length_penalty = 0.8

            final_score = word_score * position_bonus * length_penalty
            sentence_scores[sentence] = final_score

        return sentence_scores
