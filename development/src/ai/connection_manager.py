"""
Connection Manager - Semantic Link Discovery and Suggestions

Provides intelligent link suggestions using semantic similarity and embeddings.
Runs independently of Analytics for parallel execution.

Features:
- Semantic similarity using embeddings
- Link prediction with relevance ranking
- Feedback collection for learning
- Bidirectional link analysis
- Dry run mode for safe preview

Design Principles:
- NO Analytics dependencies (enables parallel execution)
- Embedding-based semantic similarity (not just keywords)
- User feedback loop for continuous improvement
- Graceful handling of missing embeddings
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.ai.types import ConnectionResult, ConfigDict, LinkFeedback


class ConnectionManager:
    """
    Semantic link discovery and suggestion manager.
    
    Uses embeddings for intelligent link predictions based on semantic similarity.
    Collects user feedback (accept/reject) to improve future suggestions.
    
    NO Analytics dependencies - can run in parallel with AnalyticsManager.
    """
    
    def __init__(
        self,
        base_dir: Path,
        config: ConfigDict,
        embeddings_service: Optional[Any] = None
    ) -> None:
        """
        Initialize ConnectionManager.
        
        Args:
            base_dir: Base directory of the Zettelkasten vault
            config: Configuration dict with similarity thresholds
            embeddings_service: Embeddings service for semantic similarity (optional)
        """
        self.base_dir = Path(base_dir)
        self.config = config
        self.embeddings = embeddings_service
        self.feedback_history = []
    
    def discover_links(
        self,
        note_path: str,
        dry_run: bool = False
    ) -> ConnectionResult:
        """
        Discover potential link suggestions for a note.
        
        Uses semantic similarity via embeddings to find conceptually related notes
        in the knowledge graph. Returns ranked suggestions based on relevance.
        
        Args:
            note_path: Path to the note file (relative to base_dir)
            dry_run: If True, don't write link suggestions to file
            
        Returns:
            List of link suggestions ranked by relevance score:
            [{
                'target': str (note path to link to),
                'score': float (0.0-1.0 similarity score),
                'reason': str (why this link is suggested)
            }]
            Returns empty list if embeddings service unavailable or errors occur.
            
        Examples:
            >>> # Example 1: Basic link discovery
            >>> connection_mgr = ConnectionManager(
            ...     base_dir=Path('knowledge'),
            ...     config={'connections': {'similarity_threshold': 0.7, 'max_suggestions': 5}},
            ...     embeddings_service=embeddings_client
            ... )
            >>> suggestions = connection_mgr.discover_links('Inbox/machine-learning.md')
            >>> print(f"Found {len(suggestions)} link suggestions")
            Found 3 link suggestions
            >>> for suggestion in suggestions:
            ...     print(f"→ [[{suggestion['target']}]] (score: {suggestion['score']:.2f})")
            ...     print(f"  Reason: {suggestion['reason']}")
            → [[Permanent Notes/neural-networks.md]] (score: 0.85)
              Reason: semantic_similarity
            → [[Permanent Notes/deep-learning.md]] (score: 0.78)
              Reason: semantic_similarity
            → [[Literature Notes/ai-fundamentals.md]] (score: 0.72)
              Reason: semantic_similarity
            
            >>> # Example 2: No embeddings service available
            >>> connection_mgr_no_embed = ConnectionManager(
            ...     base_dir=Path('knowledge'),
            ...     config={},
            ...     embeddings_service=None
            ... )
            >>> suggestions = connection_mgr_no_embed.discover_links('Inbox/note.md')
            >>> print(f"Suggestions: {suggestions}")
            Suggestions: []
            >>> # Returns empty list gracefully when embeddings unavailable
            
            >>> # Example 3: Dry run mode
            >>> suggestions = connection_mgr.discover_links(
            ...     'Inbox/test-note.md',
            ...     dry_run=True
            ... )
            >>> # Suggestions discovered but not written to file
            >>> print(f"Preview: {len(suggestions)} links would be suggested")
            Preview: 2 links would be suggested
            
            >>> # Example 4: Filtering by quality threshold
            >>> # Only high-quality connections (>0.7 similarity) are returned
            >>> suggestions = connection_mgr.discover_links('Inbox/specific-topic.md')
            >>> high_quality = [s for s in suggestions if s['score'] >= 0.8]
            >>> medium_quality = [s for s in suggestions if 0.7 <= s['score'] < 0.8]
            >>> print(f"High quality (≥0.8): {len(high_quality)} suggestions")
            >>> print(f"Medium quality (0.7-0.8): {len(medium_quality)} suggestions")
            High quality (≥0.8): 2 suggestions
            Medium quality (0.7-0.8): 1 suggestions
            
            >>> # Example 5: Using suggestions for automatic linking
            >>> suggestions = connection_mgr.discover_links('Inbox/new-note.md')
            >>> for suggestion in suggestions:
            ...     if suggestion['score'] >= 0.9:  # Very high confidence
            ...         print(f"Auto-accept: [[{suggestion['target']}]]")
            ...     elif suggestion['score'] >= 0.7:  # Good confidence
            ...         print(f"Manual review: [[{suggestion['target']}]] ({suggestion['score']:.2f})")
            Auto-accept: [[Permanent Notes/core-concept.md]]
            Manual review: [[Literature Notes/related-work.md]] (0.75)
            
            >>> # Example 6: Integration with workflow
            >>> from pathlib import Path
            >>> inbox_dir = Path('knowledge/Inbox')
            >>> for note_file in inbox_dir.glob('*.md'):
            ...     suggestions = connection_mgr.discover_links(
            ...         str(note_file.relative_to(Path('knowledge')))
            ...     )
            ...     if suggestions:
            ...         print(f"{note_file.name}: {len(suggestions)} connections found")
            machine-learning-basics.md: 5 connections found
            productivity-system.md: 3 connections found
            
            >>> # Example 7: Error handling
            >>> # Gracefully handles missing notes or embedding errors
            >>> suggestions = connection_mgr.discover_links('NonExistent/note.md')
            >>> # Returns empty list rather than raising exception
            >>> assert suggestions == []
        """
        if not self.embeddings:
            return []
        
        try:
            # Get similar notes using embeddings
            similar_notes = self.embeddings.get_similar(note_path)
            
            # Filter and rank by threshold
            suggestions = self.predict_links(note_path, similar_notes)
            
            return suggestions
        except Exception as e:
            return []
    
    def predict_links(
        self,
        note_path: str,
        similar_notes: Optional[ConnectionResult] = None
    ) -> ConnectionResult:
        """
        Predict and rank link suggestions.
        
        Filters by similarity threshold and ranks by relevance score.
        Lower-level method used by discover_links() with explicit similar notes input.
        
        Args:
            note_path: Path to the source note (relative to base_dir)
            similar_notes: List of similar notes with scores (optional, will fetch if None):
                [{'note': str, 'score': float}] or [{'target': str, 'score': float}]
            
        Returns:
            List of link predictions ranked by score (descending):
            [{
                'target': str (note path),
                'score': float (0.0-1.0),
                'reason': str ('semantic_similarity')
            }]
            Limited to max_suggestions from config (default: 5).
            
        Examples:
            >>> # Example 1: Basic link prediction with provided similar notes
            >>> connection_mgr = ConnectionManager(
            ...     base_dir=Path('knowledge'),
            ...     config={
            ...         'connections': {
            ...             'similarity_threshold': 0.7,
            ...             'max_suggestions': 5
            ...         }
            ...     },
            ...     embeddings_service=embeddings_client
            ... )
            >>> # Manually provide similar notes
            >>> similar_notes = [
            ...     {'note': 'Permanent Notes/ai-concepts.md', 'score': 0.92},
            ...     {'note': 'Literature Notes/ml-paper.md', 'score': 0.85},
            ...     {'note': 'Fleeting Notes/rough-idea.md', 'score': 0.65},  # Below threshold
            ...     {'note': 'Permanent Notes/neural-nets.md', 'score': 0.78}
            ... ]
            >>> predictions = connection_mgr.predict_links(
            ...     'Inbox/new-ml-note.md',
            ...     similar_notes
            ... )
            >>> print(f"{len(predictions)} predictions after filtering")
            3 predictions after filtering
            >>> # Note: 0.65 score filtered out (below 0.7 threshold)
            >>> for pred in predictions:
            ...     print(f"{pred['target']}: {pred['score']:.2f}")
            Permanent Notes/ai-concepts.md: 0.92
            Literature Notes/ml-paper.md: 0.85
            Permanent Notes/neural-nets.md: 0.78
            
            >>> # Example 2: Automatic fetching when similar_notes not provided
            >>> predictions = connection_mgr.predict_links('Inbox/test-note.md')
            >>> # Automatically calls embeddings.get_similar() if similar_notes is None
            >>> print(f"Auto-fetched {len(predictions)} predictions")
            Auto-fetched 4 predictions
            
            >>> # Example 3: Custom threshold configuration
            >>> connection_mgr_strict = ConnectionManager(
            ...     base_dir=Path('knowledge'),
            ...     config={'connections': {'similarity_threshold': 0.8}},  # Stricter
            ...     embeddings_service=embeddings_client
            ... )
            >>> similar_notes = [
            ...     {'note': 'note1.md', 'score': 0.95},
            ...     {'note': 'note2.md', 'score': 0.82},
            ...     {'note': 'note3.md', 'score': 0.75}  # Below 0.8 threshold
            ... ]
            >>> predictions = connection_mgr_strict.predict_links(
            ...     'source.md',
            ...     similar_notes
            ... )
            >>> print(f"With 0.8 threshold: {len(predictions)} predictions")
            With 0.8 threshold: 2 predictions
            >>> # Only notes with score ≥0.8 included
            
            >>> # Example 4: Max suggestions limit
            >>> connection_mgr_limited = ConnectionManager(
            ...     base_dir=Path('knowledge'),
            ...     config={'connections': {'max_suggestions': 3}},
            ...     embeddings_service=embeddings_client
            ... )
            >>> similar_notes = [
            ...     {'note': f'note{i}.md', 'score': 0.9 - (i * 0.05)}
            ...     for i in range(10)  # 10 similar notes
            ... ]
            >>> predictions = connection_mgr_limited.predict_links(
            ...     'source.md',
            ...     similar_notes
            ... )
            >>> print(f"Limited to: {len(predictions)} predictions")
            Limited to: 3 predictions
            >>> # Top 3 by score returned
            >>> assert all(predictions[i]['score'] >= predictions[i+1]['score']
            ...            for i in range(len(predictions)-1))
            
            >>> # Example 5: Format compatibility (note vs target key)
            >>> # Handles both 'note' and 'target' keys for flexibility
            >>> similar_v1 = [{'note': 'file1.md', 'score': 0.8}]
            >>> similar_v2 = [{'target': 'file2.md', 'score': 0.8}]
            >>> pred1 = connection_mgr.predict_links('src.md', similar_v1)
            >>> pred2 = connection_mgr.predict_links('src.md', similar_v2)
            >>> assert pred1[0]['target'] == 'file1.md'
            >>> assert pred2[0]['target'] == 'file2.md'
            >>> # Output format always uses 'target' key
            
            >>> # Example 6: Empty results handling
            >>> # When no notes meet threshold
            >>> low_similarity = [
            ...     {'note': 'note1.md', 'score': 0.5},
            ...     {'note': 'note2.md', 'score': 0.6}
            ... ]
            >>> predictions = connection_mgr.predict_links(
            ...     'source.md',
            ...     low_similarity
            ... )
            >>> print(f"Below threshold: {predictions}")
            Below threshold: []
            >>> # Returns empty list when all scores below threshold
            
            >>> # Example 7: Ranking verification
            >>> similar_notes = [
            ...     {'note': 'low.md', 'score': 0.72},
            ...     {'note': 'high.md', 'score': 0.95},
            ...     {'note': 'medium.md', 'score': 0.83}
            ... ]
            >>> predictions = connection_mgr.predict_links('src.md', similar_notes)
            >>> # Verify descending score order
            >>> scores = [p['score'] for p in predictions]
            >>> print(f"Ranked scores: {scores}")
            Ranked scores: [0.95, 0.83, 0.72]
            >>> assert scores == sorted(scores, reverse=True)
        """
        if similar_notes is None:
            # Fetch similar notes if not provided
            if self.embeddings:
                similar_notes = self.embeddings.get_similar(note_path)
            else:
                similar_notes = []
        
        # Get threshold from config
        threshold = self.config.get('connections', {}).get(
            'similarity_threshold', 0.7
        )
        max_suggestions = self.config.get('connections', {}).get(
            'max_suggestions', 5
        )
        
        # Filter by threshold
        predictions = []
        for note in similar_notes:
            score = note.get('score', 0.0)
            # Handle both 'note' and 'target' keys for compatibility
            note_path = note.get('note', note.get('target', ''))
            if score >= threshold and note_path:
                predictions.append({
                    'target': note_path,
                    'score': score,
                    'reason': 'semantic_similarity'
                })
        
        # Sort by score descending
        predictions.sort(key=lambda x: x['score'], reverse=True)
        
        # Limit to max suggestions
        return predictions[:max_suggestions]
    
    def record_link_decision(
        self,
        source: str,
        target: str,
        accepted: bool,
        similarity_score: float,
        reason: Optional[str] = None
    ) -> None:
        """
        Record user decision on link suggestion for learning.
        
        Stores feedback in history for analyzing suggestion quality and
        improving future recommendations. Enables feedback loop for
        continuous system improvement.
        
        Args:
            source: Source note path (where link would be added)
            target: Target note path (what link points to)
            accepted: Whether user accepted the suggestion (True) or rejected (False)
            similarity_score: Similarity score of the suggestion (0.0-1.0)
            reason: Optional reason for decision (user-provided or system-generated)
            
        Examples:
            >>> # Example 1: Record accepted link suggestion
            >>> connection_mgr = ConnectionManager(
            ...     base_dir=Path('knowledge'),
            ...     config={},
            ...     embeddings_service=embeddings_client
            ... )
            >>> connection_mgr.record_link_decision(
            ...     source='Inbox/machine-learning.md',
            ...     target='Permanent Notes/neural-networks.md',
            ...     accepted=True,
            ...     similarity_score=0.92,
            ...     reason='Highly relevant connection'
            ... )
            >>> history = connection_mgr.get_feedback_history()
            >>> print(f"Recorded {len(history)} decisions")
            Recorded 1 decisions
            >>> print(f"Last decision: {'accepted' if history[-1]['accepted'] else 'rejected'}")
            Last decision: accepted
            
            >>> # Example 2: Record rejected link suggestion
            >>> connection_mgr.record_link_decision(
            ...     source='Inbox/productivity.md',
            ...     target='Permanent Notes/unrelated-topic.md',
            ...     accepted=False,
            ...     similarity_score=0.71,
            ...     reason='Not conceptually related despite similarity score'
            ... )
            >>> # Records rejection with explanation
            
            >>> # Example 3: Interactive workflow integration
            >>> suggestions = connection_mgr.discover_links('Inbox/new-note.md')
            >>> for suggestion in suggestions:
            ...     # User reviews suggestion
            ...     user_choice = input(f"Accept [[{suggestion['target']}]]? (y/n): ")
            ...     accepted = (user_choice.lower() == 'y')
            ...     connection_mgr.record_link_decision(
            ...         source='Inbox/new-note.md',
            ...         target=suggestion['target'],
            ...         accepted=accepted,
            ...         similarity_score=suggestion['score']
            ...     )
            ...     print(f"Feedback recorded: {'✓ accepted' if accepted else '✗ rejected'}")
            
            >>> # Example 4: Analyze acceptance patterns
            >>> history = connection_mgr.get_feedback_history()
            >>> accepted = [d for d in history if d['accepted']]
            >>> rejected = [d for d in history if not d['accepted']]
            >>> print(f"Acceptance rate: {len(accepted)}/{len(history)} ({len(accepted)/len(history)*100:.1f}%)")
            Acceptance rate: 7/10 (70.0%)
            >>> # Calculate average scores for accepted vs rejected
            >>> avg_accepted = sum(d['similarity_score'] for d in accepted) / len(accepted)
            >>> avg_rejected = sum(d['similarity_score'] for d in rejected) / len(rejected)
            >>> print(f"Avg score - Accepted: {avg_accepted:.2f}, Rejected: {avg_rejected:.2f}")
            Avg score - Accepted: 0.87, Rejected: 0.72
            
            >>> # Example 5: Quality threshold tuning
            >>> # Use feedback to determine optimal similarity threshold
            >>> history = connection_mgr.get_feedback_history()
            >>> false_positives = [d for d in history if not d['accepted'] and d['similarity_score'] >= 0.8]
            >>> if false_positives:
            ...     print(f"Warning: {len(false_positives)} high-score rejections")
            ...     print("Consider raising similarity threshold")
            Warning: 2 high-score rejections
            Consider raising similarity threshold
            
            >>> # Example 6: Reason-based analysis
            >>> history = connection_mgr.get_feedback_history()
            >>> rejection_reasons = {}
            >>> for decision in history:
            ...     if not decision['accepted'] and decision.get('reason'):
            ...         reason = decision['reason']
            ...         rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            >>> print("Common rejection reasons:")
            >>> for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True):
            ...     print(f"  - {reason}: {count} times")
            Common rejection reasons:
              - Not conceptually related: 3 times
              - Too general: 2 times
              - Already linked: 1 times
            
            >>> # Example 7: Timestamp tracking
            >>> connection_mgr.record_link_decision(
            ...     source='note1.md',
            ...     target='note2.md',
            ...     accepted=True,
            ...     similarity_score=0.85
            ... )
            >>> latest = connection_mgr.get_feedback_history()[-1]
            >>> print(f"Decision timestamp: {latest['timestamp']}")
            Decision timestamp: 2025-10-05T20:15:30.123456
            >>> # ISO format timestamp automatically recorded
        """
        decision = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'target': target,
            'accepted': accepted,
            'similarity_score': similarity_score,
            'reason': reason
        }
        
        self.feedback_history.append(decision)
    
    def get_feedback_history(self) -> List[LinkFeedback]:
        """
        Get history of user link decisions.
        
        Returns:
            List of feedback decisions
        """
        return self.feedback_history
    
    def analyze_bidirectional_links(self) -> Dict[str, Any]:
        """
        Analyze bidirectional link patterns.
        
        Identifies:
        - One-way links (A→B but not B→A)
        - Suggestions for backlinks
        
        Returns:
            Dict with bidirectional analysis:
            {
                'one_way_links': List[Dict],
                'suggestions': List[Dict]
            }
        """
        import re
        
        link_graph = {}
        
        # Build link graph
        for md_file in self.base_dir.rglob('*.md'):
            if '.git' in str(md_file):
                continue
            
            note_path = str(md_file.relative_to(self.base_dir))
            
            try:
                content = md_file.read_text(encoding='utf-8')
                outgoing = re.findall(r'\[\[(.*?)\]\]', content)
                link_graph[note_path] = outgoing
            except Exception:
                continue
        
        # Find one-way links
        one_way_links = []
        for source, targets in link_graph.items():
            for target in targets:
                # Check if target links back to source
                target_links = link_graph.get(target, [])
                if source not in target_links:
                    # Ensure target has .md extension
                    target_with_ext = target if target.endswith('.md') else f"{target}.md"
                    one_way_links.append({
                        'source': Path(source).name,
                        'target': target_with_ext,
                        'bidirectional': False,
                        'suggest_backlink': True
                    })
        
        return {
            'one_way_links': one_way_links,
            'count': len(one_way_links)
        }
