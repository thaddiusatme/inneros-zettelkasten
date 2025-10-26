#!/usr/bin/env python3
"""
Connection Integration Utilities - TDD Iteration 3 GREEN Phase
Utilities for integrating AIConnections with LinkSuggestionEngine and CLI workflow
"""

import os
import time
import glob
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ConnectionObject:
    """Mock connection object format expected by LinkSuggestionEngine"""
    target_file: str
    similarity_score: float
    source_file: str = ""
    content_overlap: str = ""


class SimilarityResultConverter:
    """Converts AIConnections similarity results to LinkSuggestionEngine connection objects"""

    @staticmethod
    def convert_to_connections(similarity_results: List[Tuple[str, float]],
                             target_note: str, vault_path: str) -> List[ConnectionObject]:
        """
        Convert AIConnections similarity results to connection objects
        
        Args:
            similarity_results: List of (filename, similarity_score) tuples from AIConnections
            target_note: The source note being analyzed
            vault_path: Path to vault directory
            
        Returns:
            List of ConnectionObject instances compatible with LinkSuggestionEngine
        """
        connections = []

        for filename, similarity in similarity_results:
            connection = ConnectionObject(
                target_file=filename,
                similarity_score=similarity,
                source_file=target_note,
                content_overlap=""  # Could be enhanced with actual content analysis
            )
            connections.append(connection)

        return connections

    @staticmethod
    def convert_batch(similarity_results: List[Tuple[str, float]],
                     target_note: str, vault_path: str) -> List[ConnectionObject]:
        """Batch conversion with same interface as convert_to_connections"""
        return SimilarityResultConverter.convert_to_connections(
            similarity_results, target_note, vault_path
        )


class RealNoteLoader:
    """Loads and processes real notes from the file system"""

    def __init__(self, vault_path: str):
        """
        Initialize note loader
        
        Args:
            vault_path: Path to the vault/knowledge directory
        """
        self.vault_path = vault_path

    def load_note_content(self, filename: str) -> str:
        """
        Load content of a specific note
        
        Args:
            filename: Name of the note file to load
            
        Returns:
            Note content as string
        """
        file_path = os.path.join(self.vault_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
        except Exception:
            return ""

    def load_corpus_excluding(self, exclude_filename: str) -> Dict[str, str]:
        """
        Load all notes in corpus except the specified file
        
        Args:
            exclude_filename: Filename to exclude from corpus
            
        Returns:
            Dictionary mapping filenames to content
        """
        corpus = {}

        # Find all markdown files in vault
        md_pattern = os.path.join(self.vault_path, "**/*.md")
        md_files = glob.glob(md_pattern, recursive=True)

        for file_path in md_files:
            filename = os.path.basename(file_path)

            # Skip the excluded file
            if filename == exclude_filename:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    corpus[filename] = f.read()
            except Exception:
                # Skip files that can't be read
                continue

        return corpus

    def load_full_corpus(self) -> Dict[str, str]:
        """
        Load all notes in the vault
        
        Returns:
            Dictionary mapping filenames to content
        """
        return self.load_corpus_excluding("")  # Don't exclude any files


class PerformanceMonitor:
    """Monitors performance of connection discovery operations"""

    def __init__(self, target_time: float = 2.0):
        """
        Initialize performance monitor
        
        Args:
            target_time: Target time in seconds for operations
        """
        self.target_time = target_time
        self.metrics = {}
        self.current_operation = None
        self.start_time = None

    def measure(self, operation_name: str):
        """
        Context manager for measuring operation time
        
        Args:
            operation_name: Name of the operation being measured
        """
        return self._PerformanceMeasurement(self, operation_name)

    def get_metrics(self) -> Dict[str, float]:
        """
        Get all recorded metrics
        
        Returns:
            Dictionary mapping operation names to execution times
        """
        return self.metrics.copy()

    def is_within_target(self, operation_name: str) -> bool:
        """
        Check if operation was within target time
        
        Args:
            operation_name: Name of operation to check
            
        Returns:
            True if operation was within target time
        """
        return self.metrics.get(operation_name, float('inf')) <= self.target_time

    def _record_metric(self, operation_name: str, execution_time: float):
        """Record execution time for an operation"""
        self.metrics[operation_name] = execution_time

    class _PerformanceMeasurement:
        """Context manager for performance measurement"""

        def __init__(self, monitor: 'PerformanceMonitor', operation_name: str):
            self.monitor = monitor
            self.operation_name = operation_name
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time is not None:
                execution_time = time.time() - self.start_time
                self.monitor._record_metric(self.operation_name, execution_time)


class ConnectionQualityAnalyzer:
    """Analyzes quality of connections for realistic scoring"""

    @staticmethod
    def analyze_connection_quality(content1: str, content2: str) -> 'QualityScore':
        """
        Analyze connection quality between two pieces of content
        
        Args:
            content1: First content string
            content2: Second content string
            
        Returns:
            QualityScore object with score, confidence, and explanation
        """
        # Import here to avoid circular imports
        from .link_suggestion_utils import QualityScore

        # Simple implementation for GREEN phase
        # Calculate word overlap as basic similarity metric
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return QualityScore(0.0, "low", "Empty content")

        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))

        if union == 0:
            score = 0.0
        else:
            score = overlap / union

        # Determine confidence level
        if score >= 0.7:
            confidence = "high"
            explanation = f"Strong content overlap ({overlap} shared words)"
        elif score >= 0.4:
            confidence = "medium"
            explanation = f"Moderate content overlap ({overlap} shared words)"
        else:
            confidence = "low"
            explanation = f"Limited content overlap ({overlap} shared words)"

        return QualityScore(score, confidence, explanation)


class RealConnectionProcessor:
    """Main processor that integrates all components for real connection discovery"""

    def __init__(self, vault_path: str, similarity_threshold: float = 0.6):
        """
        Initialize real connection processor
        
        Args:
            vault_path: Path to vault directory
            similarity_threshold: Minimum similarity threshold for connections
        """
        self.vault_path = vault_path
        self.similarity_threshold = similarity_threshold
        self.note_loader = RealNoteLoader(vault_path)
        self.performance_monitor = PerformanceMonitor()

    def process_note_for_connections(self, target_filename: str) -> List[ConnectionObject]:
        """
        Process a note to find real connections
        
        Args:
            target_filename: Name of target note file
            
        Returns:
            List of ConnectionObject instances for similar notes
        """
        with self.performance_monitor.measure("load_notes"):
            target_content = self.note_loader.load_note_content(target_filename)
            corpus = self.note_loader.load_corpus_excluding(target_filename)

        if not target_content.strip() or not corpus:
            return []

        # Use AIConnections for real similarity analysis
        from .connections import AIConnections

        with self.performance_monitor.measure("similarity_analysis"):
            connections = AIConnections(
                similarity_threshold=self.similarity_threshold,
                max_suggestions=10
            )

            similarity_results = connections.find_similar_notes(target_content, corpus)

        # Convert to connection objects
        connection_objects = SimilarityResultConverter.convert_to_connections(
            similarity_results, target_filename, self.vault_path
        )

        return connection_objects

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics from last operation"""
        return self.performance_monitor.get_metrics()
