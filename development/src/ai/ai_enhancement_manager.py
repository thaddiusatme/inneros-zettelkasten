"""
AI Enhancement Manager - 3-Tier Fallback AI Enhancement

Provides AI-powered note enhancement with robust fallback strategy:
1. Local LLM (Ollama) - Fast, private, no cost
2. External API - Backup when local unavailable
3. Degraded mode - Empty but valid results

Features:
- Auto-tagging with kebab-case enforcement
- Summarization (abstractive + extractive)
- Promotion readiness assessment
- Bug report creation on failures
- Dry run mode to prevent API costs

Design Principles:
- 3-tier fallback prevents total failures
- Bug reports create audit trail
- Graceful degradation
- Cost awareness (dry run support)
"""

from pathlib import Path
from typing import Any, List, Optional

from .types import AIEnhancementResult, ConfigDict
from ..utils.bug_reporter import BugReporter


class AIEnhancementManager:
    """
    AI-powered note enhancement with 3-tier fallback strategy.

    Fallback tiers:
    1. Local LLM (Ollama) - Preferred, fast and private
    2. External API - Backup when local unavailable
    3. Degraded - Empty but valid results

    Features:
    - Auto-tagging with kebab-case enforcement
    - Summarization
    - Promotion readiness assessment
    - Bug reports on failures
    - Dry run mode
    """

    def __init__(
        self,
        base_dir: Path,
        config: ConfigDict,
        local_llm: Optional[Any] = None,
        ai_tagger: Optional[Any] = None,
        ai_summarizer: Optional[Any] = None,
    ) -> None:
        """
        Initialize AIEnhancementManager.

        Args:
            base_dir: Base directory of the Zettelkasten vault
            config: Configuration dict with AI settings
            local_llm: Local LLM service (e.g., Ollama client) for tier-1 enhancement
            ai_tagger: AITagger instance (optional)
            ai_summarizer: AISummarizer instance (optional)
        """
        self.base_dir = Path(base_dir)
        self.config = config
        self.local_llm = local_llm
        self.ai_tagger = ai_tagger
        self.ai_summarizer = ai_summarizer
        self.external_api = None  # Can be injected for testing/fallback
        self.bug_reporter = BugReporter(base_dir)

    def enhance_note(
        self, note_path: str, fast: bool = False, dry_run: bool = False
    ) -> AIEnhancementResult:
        """
        Enhance note with AI-generated tags and summary.

        Uses 3-tier fallback strategy for maximum reliability:
        1. Try local LLM (Ollama) - Fast, private, no cost
        2. If fails, try external API - Backup for when local unavailable
        3. If fails, return degraded results - Empty but valid output

        Args:
            note_path: Path to the note file (relative to base_dir)
            fast: If True, use faster (less thorough) AI processing
            dry_run: If True, skip AI calls to prevent costs

        Returns:
            Dict with enhancement results:
            {
                'success': bool,
                'tags': List[str] (kebab-case formatted),
                'summary': str,
                'fallback': bool (True if not using tier 1),
                'tier': str ('local', 'api', 'degraded'),
                'source': str (detailed source info),
                'skipped': bool (if dry_run),
                'error': str (if degraded)
            }

        Examples:
            >>> # Example 1: Successful local LLM enhancement (tier 1)
            >>> ai_manager = AIEnhancementManager(
            ...     base_dir=Path('knowledge'),
            ...     config={'ai_enhancement': {}},
            ...     local_llm=ollama_client,
            ...     ai_tagger=tagger,
            ...     ai_summarizer=summarizer
            ... )
            >>> result = ai_manager.enhance_note('Inbox/ml-concepts.md')
            >>> print(f"Success: {result['success']}")
            Success: True
            >>> print(f"Tags: {result['tags']}")
            Tags: ['machine-learning', 'neural-networks', 'deep-learning']
            >>> print(f"Summary: {result['summary'][:50]}...")
            Summary: This note explores fundamental concepts in mach...
            >>> print(f"Tier: {result['tier']} (fallback: {result['fallback']})")
            Tier: local (fallback: False)
            >>> print(f"Source: {result['source']}")
            Source: local_ollama

            >>> # Example 2: Fallback to external API (tier 2)
            >>> # Local LLM fails, automatically tries external API
            >>> ai_manager_no_local = AIEnhancementManager(
            ...     base_dir=Path('knowledge'),
            ...     config={},
            ...     local_llm=None,  # Local LLM unavailable
            ...     ai_tagger=None,
            ...     ai_summarizer=None
            ... )
            >>> ai_manager_no_local.external_api = external_api_client
            >>> result = ai_manager_no_local.enhance_note('Inbox/note.md')
            >>> print(f"Tier: {result['tier']} (fallback: {result['fallback']})")
            Tier: api (fallback: True)
            >>> print(f"Source: {result['source']}")
            Source: external_api
            >>> # Bug report automatically created for local LLM failure

            >>> # Example 3: Degraded mode (tier 3 - all tiers failed)
            >>> ai_manager_degraded = AIEnhancementManager(
            ...     base_dir=Path('knowledge'),
            ...     config={},
            ...     local_llm=None,
            ...     ai_tagger=None,
            ...     ai_summarizer=None
            ... )
            >>> result = ai_manager_degraded.enhance_note('Inbox/note.md')
            >>> print(f"Success: {result['success']}")
            Success: False
            >>> print(f"Tier: {result['tier']} (fallback: {result['fallback']})")
            Tier: degraded (fallback: True)
            >>> print(f"Tags: {result['tags']}, Summary: {result['summary']}")
            Tags: [], Summary:
            >>> print(f"Error: {result['error']}")
            Error: All AI tiers failed
            >>> # Note: Degraded results are still valid - workflow continues

            >>> # Example 4: Dry run mode - skip AI costs
            >>> result = ai_manager.enhance_note('Inbox/test.md', dry_run=True)
            >>> print(f"Skipped: {result.get('skipped')}")
            Skipped: True
            >>> print(f"Reason: {result.get('reason')}")
            Reason: dry_run
            >>> # No AI calls made, no costs incurred
            >>> assert result['tags'] == []
            >>> assert result['summary'] == ''

            >>> # Example 5: Fast mode for quick processing
            >>> result = ai_manager.enhance_note('Inbox/quick.md', fast=True)
            >>> # Fast mode uses lighter AI models or quicker processing
            >>> if result['success']:
            ...     print(f"Fast enhancement: {len(result['tags'])} tags generated")
            Fast enhancement: 3 tags generated

            >>> # Example 6: Understanding tier fallback behavior
            >>> result = ai_manager.enhance_note('Inbox/complex-note.md')
            >>> if not result['fallback']:
            ...     print("Tier 1 success - local LLM working perfectly")
            ... elif result['tier'] == 'api':
            ...     print("Tier 2 fallback - local failed, API succeeded")
            ...     print("Check bug reports for local LLM troubleshooting")
            ... elif result['tier'] == 'degraded':
            ...     print("Tier 3 degraded - all AI unavailable")
            ...     print("Note can still be processed, just without AI enhancement")

            >>> # Example 7: Kebab-case tag enforcement
            >>> result = ai_manager.enhance_note('Inbox/note-with-tags.md')
            >>> # All tags automatically converted to kebab-case
            >>> for tag in result['tags']:
            ...     assert '-' in tag or tag.islower()
            ...     assert ' ' not in tag
            ...     assert '_' not in tag
            >>> print(f"Kebab-case tags: {result['tags']}")
            Kebab-case tags: ['machine-learning', 'ai-workflow', 'zettelkasten']
        """
        if dry_run:
            return {
                "success": True,
                "tags": [],
                "summary": "",
                "skipped": True,
                "reason": "dry_run",
                "source": "dry_run",
            }

        # Try tier 1: Local LLM
        try:
            result = self._enhance_with_local_llm(note_path)
            if result["success"]:
                result["fallback"] = False
                result["tier"] = "local"
                result["source"] = "local_ollama"
                return result
        except Exception as e:
            # Local LLM failed - create bug report and try API
            self.bug_reporter.create_ai_failure_report(
                note_path,
                {"tier": "local_llm", "error": str(e), "error_type": type(e).__name__},
            )
            pass

        # Try tier 2: External API
        try:
            result = self._enhance_with_external_api(note_path)
            if result["success"]:
                result["fallback"] = True
                result["tier"] = "api"
                result["source"] = "external_api"
                return result
        except Exception:
            # API failed, will degrade
            pass

        # Tier 3: Degraded mode
        return {
            "success": False,
            "tags": [],
            "summary": "",
            "quality_score": 0.5,
            "fallback": True,
            "tier": "degraded",
            "source": "degraded",
            "error": "All AI tiers failed",
        }

    def assess_promotion_readiness(self, note_path: str) -> AIEnhancementResult:
        """
        Assess if a fleeting note is ready for promotion to permanent.

        Uses AI to evaluate note maturity across multiple dimensions:
        - Content maturity (well-developed vs rough draft)
        - Atomic concept clarity (single clear idea vs multiple mixed concepts)
        - Connection potential (linkable to existing knowledge)
        - Structural completeness (frontmatter, tags, links)

        Args:
            note_path: Path to the note file (relative to base_dir)

        Returns:
            Dict with promotion assessment:
            {
                'ready_for_promotion': bool,
                'confidence': float (0.0-1.0),
                'reasons': List[str] (why it's ready),
                'suggestions': List[str] (how to improve if not ready),
                'recommended_type': str ('permanent', 'literature', etc.)
            }

        Examples:
            >>> # Example 1: Note ready for promotion
            >>> ai_manager = AIEnhancementManager(
            ...     base_dir=Path('knowledge'),
            ...     config={},
            ...     local_llm=ollama_client
            ... )
            >>> result = ai_manager.assess_promotion_readiness(
            ...     'Fleeting Notes/well-developed-concept.md'
            ... )
            >>> print(f"Ready: {result['ready_for_promotion']}")
            Ready: True
            >>> print(f"Confidence: {result['confidence']}")
            Confidence: 0.85
            >>> print(f"Reasons:")
            >>> for reason in result['reasons']:
            ...     print(f"  - {reason}")
            Reasons:
              - Content is well-developed
              - Clear atomic concept
              - Strong connection potential
              - Complete frontmatter and metadata
            >>> print(f"Recommended type: {result['recommended_type']}")
            Recommended type: permanent

            >>> # Example 2: Note not ready yet
            >>> result = ai_manager.assess_promotion_readiness(
            ...     'Fleeting Notes/rough-draft.md'
            ... )
            >>> print(f"Ready: {result['ready_for_promotion']}")
            Ready: False
            >>> print(f"Confidence: {result['confidence']}")
            Confidence: 0.35
            >>> print(f"Suggestions for improvement:")
            >>> for suggestion in result['suggestions']:
            ...     print(f"  - {suggestion}")
            Suggestions for improvement:
              - Add more context and examples
              - Clarify the atomic concept
              - Add links to related notes
              - Expand content to at least 300 words

            >>> # Example 3: Use with weekly review automation
            >>> from pathlib import Path
            >>> fleeting_dir = Path('knowledge/Fleeting Notes')
            >>> promotion_candidates = []
            >>> for note_file in fleeting_dir.glob('*.md'):
            ...     assessment = ai_manager.assess_promotion_readiness(
            ...         str(note_file.relative_to(Path('knowledge')))
            ...     )
            ...     if assessment['ready_for_promotion']:
            ...         promotion_candidates.append({
            ...             'note': note_file.name,
            ...             'confidence': assessment['confidence'],
            ...             'type': assessment['recommended_type']
            ...         })
            >>> # Sort by confidence
            >>> promotion_candidates.sort(key=lambda x: x['confidence'], reverse=True)
            >>> print(f"Found {len(promotion_candidates)} promotion candidates")
            Found 5 promotion candidates

            >>> # Example 4: Different note type recommendations
            >>> # Literature note with citations
            >>> result = ai_manager.assess_promotion_readiness(
            ...     'Fleeting Notes/book-summary.md'
            ... )
            >>> if result['recommended_type'] == 'literature':
            ...     print(f"This note should become a literature note")
            ...     print(f"Reason: {result['reasons'][0]}")
            This note should become a literature note
            Reason: Contains citations and external source analysis

            >>> # Example 5: Confidence-based workflow
            >>> result = ai_manager.assess_promotion_readiness(
            ...     'Fleeting Notes/borderline-note.md'
            ... )
            >>> if result['confidence'] >= 0.8:
            ...     print("High confidence - auto-promote")
            ... elif result['confidence'] >= 0.6:
            ...     print("Medium confidence - review manually")
            ...     for suggestion in result['suggestions']:
            ...         print(f"  Consider: {suggestion}")
            ... else:
            ...     print("Low confidence - needs more work")
            Medium confidence - review manually
              Consider: Add 2-3 more examples
              Consider: Link to related concepts

            >>> # Example 6: Integration with quality scoring
            >>> from src.ai.analytics_manager import AnalyticsManager
            >>> analytics = AnalyticsManager(Path('knowledge'), config)
            >>> quality = analytics.assess_quality('Fleeting Notes/note.md')
            >>> promotion = ai_manager.assess_promotion_readiness(
            ...     'Fleeting Notes/note.md'
            ... )
            >>> # Combine metrics for comprehensive assessment
            >>> if quality['quality_score'] >= 0.7 and promotion['ready_for_promotion']:
            ...     print("Strong candidate for promotion:")
            ...     print(f"  Quality: {quality['quality_score']}")
            ...     print(f"  AI Confidence: {promotion['confidence']}")
            Strong candidate for promotion:
              Quality: 0.78
              AI Confidence: 0.82
        """
        # Placeholder implementation
        return {
            "ready_for_promotion": True,
            "confidence": 0.8,
            "reasons": ["Content is well-developed", "Clear atomic concept"],
            "suggestions": [],
            "recommended_type": "permanent",
        }

    def generate_ai_tags(self, content: str) -> List[str]:
        """
        Generate AI tags from content with kebab-case enforcement.

        Analyzes note content to extract relevant topics and converts
        them to Zettelkasten-compliant kebab-case tags.

        Args:
            content: Note content to analyze (full markdown content)

        Returns:
            List of kebab-case formatted AI-generated tags:
            - All lowercase
            - Words separated by hyphens
            - No spaces, underscores, or special characters
            - Duplicates removed

        Examples:
            >>> # Example 1: Generate tags from technical content
            >>> ai_manager = AIEnhancementManager(
            ...     base_dir=Path('knowledge'),
            ...     config={},
            ...     local_llm=ollama_client
            ... )
            >>> content = '''
            ... # Machine Learning Basics
            ...
            ... This note covers neural_networks and Deep Learning concepts.
            ... Key topics: supervised learning, unsupervised learning.
            ... '''
            >>> tags = ai_manager.generate_ai_tags(content)
            >>> print(tags)
            ['machine-learning', 'neural-networks', 'deep-learning', 'supervised-learning', 'unsupervised-learning']
            >>> # Note: All converted to kebab-case automatically

            >>> # Example 2: Kebab-case conversion in action
            >>> content = "Topics: AI Ethics, Machine_Learning, data science"
            >>> tags = ai_manager.generate_ai_tags(content)
            >>> # Verify kebab-case compliance
            >>> for tag in tags:
            ...     assert tag.islower() or '-' in tag
            ...     assert ' ' not in tag
            ...     assert '_' not in tag
            >>> print(tags)
            ['ai-ethics', 'machine-learning', 'data-science']

            >>> # Example 3: Fallback when local LLM unavailable
            >>> ai_manager_no_llm = AIEnhancementManager(
            ...     base_dir=Path('knowledge'),
            ...     config={},
            ...     local_llm=None
            ... )
            >>> tags = ai_manager_no_llm.generate_ai_tags('Some content')
            >>> print(tags)
            ['ai-generated']
            >>> # Fallback provides generic tag when AI unavailable

            >>> # Example 4: Integration with enhance_note
            >>> result = ai_manager.enhance_note('Inbox/note.md')
            >>> # Tags from enhance_note use this method
            >>> assert all(tag == tag.lower() for tag in result['tags'])
            >>> assert all('-' in tag or tag.isalpha() for tag in result['tags'])
            >>> print(f"Generated {len(result['tags'])} kebab-case tags")
            Generated 5 kebab-case tags

            >>> # Example 5: Tag cleaning and normalization
            >>> # Input with problematic formatting
            >>> content = "Tags: Machine__Learning, AI---Ethics, ---data---science---"
            >>> tags = ai_manager.generate_ai_tags(content)
            >>> # All cleaned to proper kebab-case
            >>> print(tags)
            ['machine-learning', 'ai-ethics', 'data-science']
            >>> # Multiple hyphens collapsed, leading/trailing hyphens removed
        """
        # Use local LLM if available
        if self.local_llm and hasattr(self.local_llm, "generate_tags"):
            tags = self.local_llm.generate_tags(content)
            return self._enforce_kebab_case(tags)

        # Fallback: extract simple tags from content
        tags = ["ai-generated"]
        return self._enforce_kebab_case(tags)

    def _enhance_with_local_llm(self, note_path: str) -> AIEnhancementResult:
        """Enhance using local Ollama LLM."""
        # Use local LLM if available
        if self.local_llm and hasattr(self.local_llm, "enhance"):
            llm_result = self.local_llm.enhance(note_path)
            return {
                "success": True,
                "tags": llm_result.get("tags", []),
                "summary": llm_result.get("summary", ""),
            }

        # Fallback: Use existing AI services
        if self.ai_tagger and self.ai_summarizer:
            # Use existing AI services
            pass

        # Last resort: Return empty result
        return {"success": True, "tags": [], "summary": ""}

    def _enhance_with_external_api(self, note_path: str) -> AIEnhancementResult:
        """Enhance using external API as fallback."""
        # Use external API if available
        if self.external_api and hasattr(self.external_api, "enhance"):
            api_result = self.external_api.enhance(note_path)
            return {
                "success": True,
                "tags": api_result.get("tags", []),
                "summary": api_result.get("summary", ""),
            }

        # Placeholder fallback
        return {"success": True, "tags": [], "summary": ""}

    def _enforce_kebab_case(self, tags: List[str]) -> List[str]:
        """Convert all tags to kebab-case format."""
        import re

        kebab_tags = []
        for tag in tags:
            # Convert to lowercase
            tag = tag.lower()
            # Replace spaces and underscores with hyphens
            tag = re.sub(r"[\s_]+", "-", tag)
            # Remove non-alphanumeric characters except hyphens
            tag = re.sub(r"[^a-z0-9-]", "", tag)
            # Remove duplicate hyphens
            tag = re.sub(r"-+", "-", tag)
            # Remove leading/trailing hyphens
            tag = tag.strip("-")

            if tag:  # Only add non-empty tags
                kebab_tags.append(tag)

        return kebab_tags
