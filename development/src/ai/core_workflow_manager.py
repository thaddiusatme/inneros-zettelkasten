"""
Core Workflow Manager - Orchestrates Analytics, AI Enhancement, and Connection Discovery

This manager coordinates the workflow of processing notes through three specialized managers:
1. AnalyticsManager - Pure metrics calculation (quality scoring, orphaned/stale detection)
2. AIEnhancementManager - AI-powered enhancement with 3-tier fallback
3. ConnectionManager - Semantic link discovery and suggestions

Design Principles:
- Exception-based error handling for clean orchestration
- Cost gating to prevent expensive AI operations on low-quality notes
- Bug report creation for failures requiring human review
- Graceful degradation on partial failures
- Dry run mode for testing/preview without side effects
"""

from pathlib import Path
from typing import Dict, Any, Optional

from src.utils.bug_reporter import BugReporter


class CoreWorkflowManager:
    """
    Orchestrates the complete workflow for processing notes.
    
    Coordinates three specialized managers:
    - AnalyticsManager: Quality assessment and metrics
    - AIEnhancementManager: AI-powered tagging and summarization
    - ConnectionManager: Semantic link discovery
    
    Implements:
    - Exception-based error handling
    - Cost gating (skip AI for low-quality notes)
    - Bug report creation on failures
    - Result validation with sensible defaults
    """
    
    def __init__(
        self,
        base_dir: Path,
        config: Dict[str, Any],
        analytics_manager,
        ai_enhancement_manager,
        connection_manager
    ):
        """
        Initialize CoreWorkflowManager with dependency injection.
        
        Args:
            base_dir: Base directory of the Zettelkasten vault
            config: Configuration dict with thresholds and settings
            analytics_manager: AnalyticsManager instance
            ai_enhancement_manager: AIEnhancementManager instance
            connection_manager: ConnectionManager instance
        """
        self.base_dir = Path(base_dir)
        self.config = config
        self.analytics = analytics_manager
        self.ai_enhancement = ai_enhancement_manager
        self.connections = connection_manager
        self.bug_reporter = BugReporter(base_dir)
        
    def process_inbox_note(
        self,
        note_path: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Process a note through the complete workflow.
        
        Workflow stages:
        1. Analytics assessment (quality, metadata)
        2. Cost gating check (skip AI if quality too low)
        3. AI enhancement (tagging, summarization) if quality gate passes
        4. Connection discovery (link suggestions)
        
        Args:
            note_path: Path to the note file
            dry_run: If True, prevent file writes and API costs
            
        Returns:
            Dict containing results from all managers with structure:
            {
                'success': bool,
                'analytics': {...},
                'ai_enhancement': {...},
                'connections': {...},
                'errors': [...],
                'dry_run': bool (if applicable)
            }
            
        Exception Handling:
        - ValueError from Analytics: Returns validation error
        - FileNotFoundError from Analytics: Returns not_found error
        - AI/Connection failures: Graceful degradation with error recording
        """
        # Analytics stage - raises exceptions on validation/file errors
        try:
            analytics_result = self.analytics.assess_quality(note_path, dry_run=dry_run)
        except ValueError as e:
            # Validation error - stop early
            return {
                'success': False,
                'analytics': {},
                'ai_enhancement': {},
                'connections': {},
                'errors': [{
                    'stage': 'analytics',
                    'type': 'validation',
                    'error': str(e)
                }],
                'warnings': []
            }
        except FileNotFoundError as e:
            # File not found - stop early
            return {
                'success': False,
                'analytics': {},
                'ai_enhancement': {},
                'connections': {},
                'errors': [{
                    'stage': 'analytics',
                    'type': 'not_found',
                    'error': str(e)
                }],
                'warnings': []
            }
        except Exception as e:
            # Generic Analytics error - continue with degraded result
            analytics_result = {
                'success': False,
                'quality_score': 0.0,
                'error': str(e)
            }
            analytics_error = {
                'stage': 'analytics',
                'type': 'exception',
                'error': str(e)
            }
        else:
            # Analytics succeeded
            analytics_error = None
        
        # Initialize result structure
        result = {
            'success': False if analytics_error else True,
            'analytics': analytics_result,
            'ai_enhancement': {},
            'connections': {},
            'errors': [analytics_error] if analytics_error else [],
            'warnings': []
        }
        
        # Add dry_run flag if applicable
        if dry_run:
            result['dry_run'] = True
        
        # Cost gating - skip AI if quality too low (but only if Analytics succeeded)
        quality_score = analytics_result.get('quality_score', 0.0)
        cost_gate_threshold = self.config.get('ai_enhancement', {}).get(
            'cost_gate_threshold', 0.3
        )
        
        # Only apply cost gating if Analytics succeeded
        analytics_succeeded = analytics_result.get('success', True)
        if analytics_succeeded and quality_score < cost_gate_threshold:
            # Skip AI enhancement due to low quality
            result['ai_enhancement'] = {
                'success': False,
                'skipped': True,
                'reason': 'quality_too_low',
                'quality_score': quality_score,
                'threshold': cost_gate_threshold,
                'tags': [],
                'summary': ''
            }
            result['warnings'].append(
                f'AI enhancement skipped: quality score {quality_score} below threshold {cost_gate_threshold}'
            )
        else:
            # Run AI enhancement
            try:
                ai_result = self.ai_enhancement.enhance_note(
                    note_path, 
                    fast=False, 
                    dry_run=dry_run
                )
                result['ai_enhancement'] = ai_result
                
                # Check for AI failures
                if not ai_result.get('success', False):
                    result['success'] = False
                    result['errors'].append({
                        'stage': 'ai_enhancement',
                        'type': 'enhancement_failed',
                        'error': 'AI enhancement failed with fallback'
                    })
                    # Note: Bug reporting handled by AIEnhancementManager
                    
            except Exception as e:
                # Graceful degradation on AI failure
                result['ai_enhancement'] = {
                    'success': False,
                    'error': str(e),
                    'tags': [],
                    'summary': ''
                }
                result['errors'].append({
                    'stage': 'ai_enhancement',
                    'type': 'exception',
                    'error': str(e)
                })
        
        # Connection discovery - runs independently
        try:
            connections_result = self.connections.discover_links(
                note_path, 
                dry_run=dry_run
            )
            # discover_links returns list directly
            result['connections'] = connections_result if connections_result else []
        except Exception as e:
            # Graceful degradation on connection failure
            result['connections'] = []
            result['errors'].append({
                'stage': 'connections',
                'type': 'exception',
                'error': str(e)
            })
        
        # Validate and apply sensible defaults
        result = self._validate_result(result)
        
        # Check for total workflow failure (multiple errors)
        if len(result['errors']) >= 3:
            result['warnings'].append('Total workflow failure - multiple systems failed')
            self.bug_reporter.create_workflow_failure_report(note_path, result)
        
        return result
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate result structure and apply sensible defaults.
        
        Ensures all expected keys are present with reasonable defaults.
        
        Args:
            result: Result dict to validate
            
        Returns:
            Validated result dict with defaults applied
        """
        # Ensure analytics has required fields
        if 'analytics' in result and result['analytics']:
            analytics = result['analytics']
            analytics.setdefault('quality_score', 0.5)
            analytics.setdefault('word_count', 0)
            analytics.setdefault('tag_count', 0)
            analytics.setdefault('link_count', 0)
        
        # Ensure ai_enhancement has success field
        if 'ai_enhancement' in result and result['ai_enhancement']:
            result['ai_enhancement'].setdefault('success', False)
        
        # Ensure connections is a list
        if 'connections' not in result or result['connections'] is None:
            result['connections'] = []
        
        return result
