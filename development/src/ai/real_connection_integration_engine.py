#!/usr/bin/env python3
"""
Real Connection Integration Engine - TDD Iteration 3 REFACTOR Phase
Production-ready orchestrator for real connection discovery integration
"""

import time
from typing import List, Dict, Optional
from pathlib import Path

from .connections import AIConnections
from .link_suggestion_engine import LinkSuggestionEngine, LinkSuggestion
from .connection_integration_utils import (
    SimilarityResultConverter, 
    RealNoteLoader, 
    PerformanceMonitor,
    RealConnectionProcessor
)


class RealConnectionIntegrationEngine:
    """
    Production-ready engine that orchestrates real connection discovery 
    integration with link suggestion generation
    """
    
    def __init__(self, vault_path: str, similarity_threshold: float = 0.6, 
                 quality_threshold: float = 0.5, max_suggestions: int = 10):
        """
        Initialize integration engine
        
        Args:
            vault_path: Path to vault directory
            similarity_threshold: Minimum similarity for connections
            quality_threshold: Minimum quality for suggestions
            max_suggestions: Maximum suggestions to return
        """
        self.vault_path = vault_path
        self.similarity_threshold = similarity_threshold
        self.quality_threshold = quality_threshold
        self.max_suggestions = max_suggestions
        
        # Initialize core components
        self.note_loader = RealNoteLoader(vault_path)
        self.ai_connections = AIConnections(
            similarity_threshold=similarity_threshold,
            max_suggestions=max_suggestions * 2  # Get more candidates for filtering
        )
        self.suggestion_engine = LinkSuggestionEngine(
            vault_path=vault_path,
            quality_threshold=quality_threshold,
            max_suggestions=max_suggestions
        )
        self.performance_monitor = PerformanceMonitor(target_time=2.0)
    
    def generate_suggestions_for_note(self, target_filename: str, 
                                    min_quality: float = None) -> List[LinkSuggestion]:
        """
        Generate high-quality link suggestions for a target note using real connection discovery
        
        Args:
            target_filename: Name of target note file
            min_quality: Optional minimum quality override
            
        Returns:
            List of LinkSuggestion objects sorted by quality
        """
        min_qual = min_quality or self.quality_threshold
        
        with self.performance_monitor.measure("total_processing"):
            # Load target note and corpus
            with self.performance_monitor.measure("note_loading"):
                target_content = self.note_loader.load_note_content(target_filename)
                if not target_content.strip():
                    return []
                
                corpus = self.note_loader.load_corpus_excluding(target_filename)
                if not corpus:
                    return []
            
            # Perform connection discovery
            with self.performance_monitor.measure("connection_discovery"):
                similarity_results = self.ai_connections.find_similar_notes(
                    target_content, corpus
                )
            
            # Convert to connection objects
            with self.performance_monitor.measure("format_conversion"):
                connection_objects = SimilarityResultConverter.convert_to_connections(
                    similarity_results, target_filename, self.vault_path
                )
            
            # Generate link suggestions
            with self.performance_monitor.measure("suggestion_generation"):
                suggestions = self.suggestion_engine.generate_link_suggestions(
                    target_note=target_filename,
                    connections=connection_objects,
                    min_quality=min_qual,
                    max_results=self.max_suggestions
                )
        
        return suggestions
    
    def batch_process_notes(self, note_filenames: List[str], 
                          min_quality: float = None) -> Dict[str, List[LinkSuggestion]]:
        """
        Process multiple notes for link suggestions in batch
        
        Args:
            note_filenames: List of note filenames to process
            min_quality: Optional minimum quality threshold
            
        Returns:
            Dictionary mapping note filenames to their suggestions
        """
        results = {}
        
        with self.performance_monitor.measure("batch_processing"):
            for filename in note_filenames:
                try:
                    suggestions = self.generate_suggestions_for_note(filename, min_quality)
                    results[filename] = suggestions
                except Exception:
                    # Skip notes that can't be processed
                    results[filename] = []
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics from last operation"""
        return self.performance_monitor.get_metrics()
    
    def validate_performance_targets(self) -> Dict[str, bool]:
        """
        Validate that performance targets are being met
        
        Returns:
            Dictionary indicating which targets are met
        """
        metrics = self.get_performance_metrics()
        return {
            "total_processing_under_2s": metrics.get("total_processing", 999) < 2.0,
            "note_loading_efficient": metrics.get("note_loading", 999) < 0.5,
            "connection_discovery_fast": metrics.get("connection_discovery", 999) < 1.5,
            "suggestion_generation_quick": metrics.get("suggestion_generation", 999) < 0.5
        }


class CLIIntegrationOrchestrator:
    """
    Orchestrates real connection integration for CLI commands with enhanced error handling
    """
    
    def __init__(self, vault_path: str):
        """Initialize CLI orchestrator"""
        self.vault_path = vault_path
        self.integration_engine = None
    
    def initialize_engine(self, similarity_threshold: float = 0.6, 
                         quality_threshold: float = 0.5, max_suggestions: int = 10) -> bool:
        """
        Initialize integration engine with error handling
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.integration_engine = RealConnectionIntegrationEngine(
                vault_path=self.vault_path,
                similarity_threshold=similarity_threshold,
                quality_threshold=quality_threshold,
                max_suggestions=max_suggestions
            )
            return True
        except Exception:
            return False
    
    def process_cli_request(self, target_filename: str, min_quality: float, 
                          max_results: int) -> Optional[List[LinkSuggestion]]:
        """
        Process CLI request with comprehensive error handling
        
        Args:
            target_filename: Target note filename
            min_quality: Minimum quality threshold
            max_results: Maximum results to return
            
        Returns:
            List of suggestions or None if processing failed
        """
        if not self.integration_engine:
            if not self.initialize_engine(quality_threshold=min_quality, max_suggestions=max_results):
                return None
        
        try:
            suggestions = self.integration_engine.generate_suggestions_for_note(
                target_filename, min_quality
            )
            
            # Limit results
            return suggestions[:max_results]
            
        except FileNotFoundError:
            # Target file or vault directory doesn't exist
            return None
        except Exception:
            # Other processing errors
            return None
    
    def get_processing_summary(self) -> Optional[Dict[str, any]]:
        """
        Get summary of last processing operation
        
        Returns:
            Summary dictionary or None if no processing done
        """
        if not self.integration_engine:
            return None
        
        metrics = self.integration_engine.get_performance_metrics()
        targets = self.integration_engine.validate_performance_targets()
        
        return {
            "performance_metrics": metrics,
            "targets_met": targets,
            "processing_time": metrics.get("total_processing", 0),
            "performance_grade": "excellent" if all(targets.values()) else "good" if sum(targets.values()) >= 2 else "needs_optimization"
        }


class ProductionOptimizedProcessor:
    """
    Production-optimized processor with caching and batch processing capabilities
    """
    
    def __init__(self, vault_path: str):
        """Initialize optimized processor"""
        self.vault_path = vault_path
        self.corpus_cache = None
        self.cache_timestamp = None
        self.engine = RealConnectionIntegrationEngine(vault_path)
    
    def get_cached_corpus(self, force_refresh: bool = False) -> Dict[str, str]:
        """
        Get corpus with intelligent caching
        
        Args:
            force_refresh: Force cache refresh
            
        Returns:
            Cached or fresh corpus
        """
        current_time = time.time()
        
        # Refresh cache if it's older than 5 minutes or forced
        if (force_refresh or 
            self.corpus_cache is None or 
            self.cache_timestamp is None or 
            current_time - self.cache_timestamp > 300):
            
            self.corpus_cache = self.engine.note_loader.load_full_corpus()
            self.cache_timestamp = current_time
        
        return self.corpus_cache
    
    def process_with_caching(self, target_filename: str, min_quality: float = 0.5) -> List[LinkSuggestion]:
        """
        Process with optimized caching for better performance
        
        Args:
            target_filename: Target note filename
            min_quality: Minimum quality threshold
            
        Returns:
            List of link suggestions
        """
        # Use cached corpus for better performance
        corpus = self.get_cached_corpus()
        
        # Remove target from corpus if present
        corpus_excluding_target = {k: v for k, v in corpus.items() 
                                 if k != target_filename}
        
        # Load target content
        target_content = self.engine.note_loader.load_note_content(target_filename)
        if not target_content.strip():
            return []
        
        # Perform optimized connection discovery
        similarity_results = self.engine.ai_connections.find_similar_notes(
            target_content, corpus_excluding_target
        )
        
        # Convert and generate suggestions
        connections = SimilarityResultConverter.convert_to_connections(
            similarity_results, target_filename, self.vault_path
        )
        
        return self.engine.suggestion_engine.generate_link_suggestions(
            target_note=target_filename,
            connections=connections,
            min_quality=min_quality
        )
