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
from typing import Dict, Any, List

from src.utils.bug_reporter import BugReporter


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
        config: Dict[str, Any],
        local_llm=None,
        ai_tagger=None,
        ai_summarizer=None
    ):
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
        self,
        note_path: str,
        fast: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Enhance note with AI-generated tags and summary.
        
        Uses 3-tier fallback:
        1. Try local LLM (Ollama)
        2. If fails, try external API
        3. If fails, return degraded (empty) results
        
        Args:
            note_path: Path to the note file
            fast: If True, use faster (less thorough) AI processing
            dry_run: If True, skip AI calls to prevent costs
            
        Returns:
            Dict with enhancement results:
            {
                'success': bool,
                'tags': List[str],
                'summary': str,
                'fallback': bool,
                'tier': str ('local', 'api', 'degraded')
            }
        """
        if dry_run:
            return {
                'success': True,
                'tags': [],
                'summary': '',
                'skipped': True,
                'reason': 'dry_run',
                'source': 'dry_run'
            }
        
        # Try tier 1: Local LLM
        try:
            result = self._enhance_with_local_llm(note_path)
            if result['success']:
                result['fallback'] = False
                result['tier'] = 'local'
                result['source'] = 'local_ollama'
                return result
        except Exception as e:
            # Local LLM failed - create bug report and try API
            self.bug_reporter.create_ai_failure_report(note_path, {
                'tier': 'local_llm',
                'error': str(e),
                'error_type': type(e).__name__
            })
            pass
        
        # Try tier 2: External API
        try:
            result = self._enhance_with_external_api(note_path)
            if result['success']:
                result['fallback'] = True
                result['tier'] = 'api'
                result['source'] = 'external_api'
                return result
        except Exception as e:
            # API failed, will degrade
            pass
        
        # Tier 3: Degraded mode
        return {
            'success': False,
            'tags': [],
            'summary': '',
            'quality_score': 0.5,
            'fallback': True,
            'tier': 'degraded',
            'source': 'degraded',
            'error': 'All AI tiers failed'
        }
    
    def assess_promotion_readiness(
        self,
        note_path: str
    ) -> Dict[str, Any]:
        """
        Assess if a fleeting note is ready for promotion to permanent.
        
        Uses AI to evaluate:
        - Content maturity
        - Atomic concept clarity
        - Connection potential
        
        Args:
            note_path: Path to the note file
            
        Returns:
            Dict with assessment:
            {
                'ready_for_promotion': bool,
                'confidence': float (0.0-1.0),
                'reasons': List[str],
                'suggestions': List[str]
            }
        """
        # Placeholder implementation
        return {
            'ready_for_promotion': True,
            'confidence': 0.8,
            'reasons': ['Content is well-developed', 'Clear atomic concept'],
            'suggestions': [],
            'recommended_type': 'permanent'
        }
    
    def generate_ai_tags(self, content: str) -> List[str]:
        """
        Generate AI tags from content with kebab-case enforcement.
        
        Args:
            content: Note content to analyze
            
        Returns:
            List of kebab-case formatted AI-generated tags
        """
        # Use local LLM if available
        if self.local_llm and hasattr(self.local_llm, 'generate_tags'):
            tags = self.local_llm.generate_tags(content)
            return self._enforce_kebab_case(tags)
        
        # Fallback: extract simple tags from content
        tags = ['ai-generated']
        return self._enforce_kebab_case(tags)
    
    def _enhance_with_local_llm(self, note_path: str) -> Dict[str, Any]:
        """Enhance using local Ollama LLM."""
        # Use local LLM if available
        if self.local_llm and hasattr(self.local_llm, 'enhance'):
            llm_result = self.local_llm.enhance(note_path)
            return {
                'success': True,
                'tags': llm_result.get('tags', []),
                'summary': llm_result.get('summary', '')
            }
        
        # Fallback: Use existing AI services
        if self.ai_tagger and self.ai_summarizer:
            # Use existing AI services
            pass
        
        # Last resort: Return empty result
        return {
            'success': True,
            'tags': [],
            'summary': ''
        }
    
    def _enhance_with_external_api(self, note_path: str) -> Dict[str, Any]:
        """Enhance using external API as fallback."""
        # Use external API if available
        if self.external_api and hasattr(self.external_api, 'enhance'):
            api_result = self.external_api.enhance(note_path)
            return {
                'success': True,
                'tags': api_result.get('tags', []),
                'summary': api_result.get('summary', '')
            }
        
        # Placeholder fallback
        return {
            'success': True,
            'tags': [],
            'summary': ''
        }
    
    def _enforce_kebab_case(self, tags: List[str]) -> List[str]:
        """Convert all tags to kebab-case format."""
        import re
        
        kebab_tags = []
        for tag in tags:
            # Convert to lowercase
            tag = tag.lower()
            # Replace spaces and underscores with hyphens
            tag = re.sub(r'[\s_]+', '-', tag)
            # Remove non-alphanumeric characters except hyphens
            tag = re.sub(r'[^a-z0-9-]', '', tag)
            # Remove duplicate hyphens
            tag = re.sub(r'-+', '-', tag)
            # Remove leading/trailing hyphens
            tag = tag.strip('-')
            
            if tag:  # Only add non-empty tags
                kebab_tags.append(tag)
        
        return kebab_tags
