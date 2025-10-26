#!/usr/bin/env python3
"""
Real Connection CLI Utilities - TDD Iteration 3 REFACTOR Phase
Enhanced CLI utilities for real connection discovery integration
"""

import os
from typing import List, Optional, Dict, Any

from ai.real_connection_integration_engine import (
    CLIIntegrationOrchestrator,
    ProductionOptimizedProcessor
)
from ai.link_suggestion_engine import LinkSuggestion


class EnhancedConnectionCLIProcessor:
    """
    Enhanced CLI processor with comprehensive error handling and performance optimization
    """

    def __init__(self, vault_path: str):
        """Initialize enhanced processor"""
        self.vault_path = vault_path
        self.orchestrator = CLIIntegrationOrchestrator(vault_path)
        self.optimized_processor = ProductionOptimizedProcessor(vault_path)

    def validate_inputs(self, target_path: str, corpus_dir: str) -> Dict[str, Any]:
        """
        Validate CLI inputs with detailed error reporting
        
        Args:
            target_path: Path to target note
            corpus_dir: Path to corpus directory
            
        Returns:
            Validation result dictionary
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "target_filename": None
        }

        # Validate target file
        if not os.path.exists(target_path):
            validation["valid"] = False
            validation["errors"].append(f"Target file not found: {target_path}")
        elif not target_path.endswith('.md'):
            validation["warnings"].append("Target file doesn't have .md extension")
        else:
            validation["target_filename"] = os.path.basename(target_path)

        # Validate corpus directory
        if not os.path.exists(corpus_dir):
            validation["valid"] = False
            validation["errors"].append(f"Corpus directory not found: {corpus_dir}")
        elif not os.path.isdir(corpus_dir):
            validation["valid"] = False
            validation["errors"].append(f"Corpus path is not a directory: {corpus_dir}")

        return validation

    def process_suggest_links_command(self, target_path: str, corpus_dir: str,
                                    min_quality: float, max_results: int,
                                    use_optimization: bool = True) -> Optional[List[LinkSuggestion]]:
        """
        Process suggest-links command with enhanced error handling
        
        Args:
            target_path: Path to target note
            corpus_dir: Corpus directory path
            min_quality: Minimum quality threshold
            max_results: Maximum results to return
            use_optimization: Whether to use performance optimization
            
        Returns:
            List of suggestions or None if processing failed
        """
        # Validate inputs
        validation = self.validate_inputs(target_path, corpus_dir)

        if not validation["valid"]:
            return None

        target_filename = validation["target_filename"]

        # Process with appropriate method
        try:
            if use_optimization:
                suggestions = self.optimized_processor.process_with_caching(
                    target_filename, min_quality
                )
            else:
                suggestions = self.orchestrator.process_cli_request(
                    target_filename, min_quality, max_results
                )

            return suggestions[:max_results] if suggestions else []

        except Exception:
            return None

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from last operation"""
        return self.orchestrator.get_processing_summary() or {}


class ConnectionResultsFormatter:
    """
    Enhanced formatter for connection discovery results with rich output
    """

    @staticmethod
    def format_suggestions_summary(suggestions: List[LinkSuggestion],
                                 target_filename: str) -> str:
        """
        Format suggestions summary with enhanced metrics
        
        Args:
            suggestions: List of link suggestions
            target_filename: Name of target file
            
        Returns:
            Formatted summary string
        """
        if not suggestions:
            return f"ℹ️  No quality link suggestions found for '{target_filename}'"

        high_quality = [s for s in suggestions if s.confidence == "high"]
        medium_quality = [s for s in suggestions if s.confidence == "medium"]
        low_quality = [s for s in suggestions if s.confidence == "low"]

        avg_similarity = sum(s.similarity_score for s in suggestions) / len(suggestions)
        avg_quality = sum(s.quality_score for s in suggestions) / len(suggestions)

        summary_lines = [
            f"📊 Generated {len(suggestions)} link suggestions for '{target_filename}':",
            f"   🟢 {len(high_quality)} High Quality (confident recommendations)",
            f"   🟡 {len(medium_quality)} Medium Quality (good candidates)",
            f"   🔴 {len(low_quality)} Low Quality (review carefully)",
            "",
            f"📈 Average Similarity: {avg_similarity:.1%}",
            f"🎯 Average Quality Score: {avg_quality:.2f}",
            "-" * 60
        ]

        return "\n".join(summary_lines)

    @staticmethod
    def format_performance_report(performance_summary: Dict[str, Any]) -> str:
        """
        Format performance report with detailed metrics
        
        Args:
            performance_summary: Performance summary dictionary
            
        Returns:
            Formatted performance report
        """
        if not performance_summary:
            return "⚡ Performance metrics not available"

        metrics = performance_summary.get("performance_metrics", {})
        targets = performance_summary.get("targets_met", {})
        grade = performance_summary.get("performance_grade", "unknown")

        # Format grade with emoji
        grade_emoji = {
            "excellent": "🚀",
            "good": "✅",
            "needs_optimization": "⚠️"
        }.get(grade, "📊")

        report_lines = [
            f"⚡ Performance Report: {grade_emoji} {grade.title()}",
            f"   Total Processing: {metrics.get('total_processing', 0):.3f}s",
            f"   Note Loading: {metrics.get('note_loading', 0):.3f}s",
            f"   Connection Discovery: {metrics.get('connection_discovery', 0):.3f}s",
            f"   Suggestion Generation: {metrics.get('suggestion_generation', 0):.3f}s",
            ""
        ]

        # Add target status
        target_status = []
        for target, met in targets.items():
            status = "✅" if met else "❌"
            target_status.append(f"   {status} {target.replace('_', ' ').title()}")

        if target_status:
            report_lines.extend(["🎯 Performance Targets:"] + target_status)

        return "\n".join(report_lines)

    @staticmethod
    def format_error_message(error_type: str, details: str = "") -> str:
        """
        Format user-friendly error messages
        
        Args:
            error_type: Type of error
            details: Additional error details
            
        Returns:
            Formatted error message
        """
        error_messages = {
            "file_not_found": "❌ Target file not found",
            "directory_not_found": "❌ Corpus directory not found",
            "no_connections": "ℹ️  No similar notes found in corpus",
            "processing_error": "⚠️  Error processing connections",
            "invalid_format": "❌ Invalid file format"
        }

        base_message = error_messages.get(error_type, f"❌ Error: {error_type}")

        if details:
            return f"{base_message}: {details}"
        return base_message


class RealConnectionCLIHelper:
    """
    Helper class for integrating real connection discovery with existing CLI infrastructure
    """

    @staticmethod
    def create_enhanced_processor(vault_path: str) -> EnhancedConnectionCLIProcessor:
        """
        Create enhanced processor with validation
        
        Args:
            vault_path: Path to vault directory
            
        Returns:
            EnhancedConnectionCLIProcessor instance
        """
        return EnhancedConnectionCLIProcessor(vault_path)

    @staticmethod
    def process_and_format_results(processor: EnhancedConnectionCLIProcessor,
                                 target_path: str, corpus_dir: str,
                                 min_quality: float, max_results: int,
                                 show_performance: bool = True) -> Dict[str, Any]:
        """
        Process command and format results in one operation
        
        Args:
            processor: Enhanced processor instance
            target_path: Target file path
            corpus_dir: Corpus directory
            min_quality: Minimum quality threshold
            max_results: Maximum results
            show_performance: Whether to include performance report
            
        Returns:
            Dictionary with suggestions and formatted output
        """
        # Process suggestions
        suggestions = processor.process_suggest_links_command(
            target_path, corpus_dir, min_quality, max_results
        )

        target_filename = os.path.basename(target_path)

        # Format results
        if suggestions is None:
            return {
                "suggestions": [],
                "summary": ConnectionResultsFormatter.format_error_message(
                    "processing_error", "Failed to process connection discovery"
                ),
                "performance_report": "",
                "success": False
            }

        summary = ConnectionResultsFormatter.format_suggestions_summary(
            suggestions, target_filename
        )

        performance_report = ""
        if show_performance:
            performance_summary = processor.get_performance_summary()
            performance_report = ConnectionResultsFormatter.format_performance_report(
                performance_summary
            )

        return {
            "suggestions": suggestions,
            "summary": summary,
            "performance_report": performance_report,
            "success": True
        }
