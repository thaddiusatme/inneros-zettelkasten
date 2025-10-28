"""
Result Validation Utilities for Workflow Manager Results.

Provides validation and default value application for result dictionaries
returned by workflow managers, ensuring consistent structure and preventing
errors from missing keys or unexpected None values.

Features:
- Workflow result validation with sensible defaults
- Individual manager result validation
- Analytics, AI enhancement, and connection result defaults
- Type-safe result structure enforcement

Usage:
    >>> from src.utils.result_validator import ResultValidator
    >>> result = {'analytics': {}, 'ai_enhancement': {}, 'connections': None}
    >>> validated = ResultValidator.validate_workflow_result(result)
    >>> assert validated['connections'] == []
"""

from typing import Dict, Any


class ResultValidator:
    """
    Validates and applies defaults to workflow result dictionaries.

    Ensures all workflow and manager results have expected keys with
    reasonable default values, preventing KeyError and None-related bugs.

    Examples:
        >>> # Validate complete workflow result
        >>> result = {
        ...     'analytics': {'quality_score': 0.8},
        ...     'ai_enhancement': {},
        ...     'connections': None
        ... }
        >>> validated = ResultValidator.validate_workflow_result(result)
        >>> assert validated['connections'] == []
        >>> assert validated['ai_enhancement']['success'] == False

        >>> # Validate analytics result with missing fields
        >>> analytics = {'quality_score': 0.7}
        >>> validated = ResultValidator.validate_analytics_result(analytics)
        >>> assert validated['word_count'] == 0
        >>> assert validated['tag_count'] == 0
    """

    @staticmethod
    def validate_workflow_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete workflow result with all manager outputs.

        Ensures analytics, AI enhancement, and connections results have
        all required fields with sensible defaults. Prevents errors from
        missing or None values.

        Args:
            result: Workflow result dict with keys:
                - analytics: Analytics assessment result
                - ai_enhancement: AI enhancement result
                - connections: Connection discovery result (list)
                - errors: List of error dicts (optional)
                - warnings: List of warning strings (optional)

        Returns:
            Validated result dict with defaults applied

        Examples:
            >>> result = {
            ...     'analytics': {'quality_score': 0.5},
            ...     'ai_enhancement': {'tags': ['test']},
            ...     'connections': None,
            ...     'errors': []
            ... }
            >>> validated = ResultValidator.validate_workflow_result(result)
            >>> assert validated['analytics']['word_count'] == 0
            >>> assert validated['ai_enhancement']['success'] == False
            >>> assert validated['connections'] == []
        """
        # Validate analytics result
        if "analytics" in result and result["analytics"]:
            result["analytics"] = ResultValidator.validate_analytics_result(
                result["analytics"]
            )

        # Validate AI enhancement result
        if "ai_enhancement" in result and result["ai_enhancement"]:
            result["ai_enhancement"] = ResultValidator.validate_ai_result(
                result["ai_enhancement"]
            )

        # Validate connections result
        result["connections"] = ResultValidator.validate_connections_result(
            result.get("connections")
        )

        # Ensure errors and warnings lists exist
        result.setdefault("errors", [])
        result.setdefault("warnings", [])

        return result

    @staticmethod
    def validate_analytics_result(analytics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate analytics result with required metric fields.

        Ensures all quality metrics have default values. Used by both
        workflow validation and standalone analytics result processing.

        Args:
            analytics: Analytics result dict with metrics:
                - quality_score: 0.0-1.0 score (default: 0.5)
                - word_count: Note word count (default: 0)
                - tag_count: Number of tags (default: 0)
                - link_count: Number of links (default: 0)

        Returns:
            Validated analytics dict with all metric fields

        Examples:
            >>> analytics = {'quality_score': 0.8}
            >>> validated = ResultValidator.validate_analytics_result(analytics)
            >>> assert validated['word_count'] == 0
            >>> assert validated['tag_count'] == 0
            >>> assert validated['link_count'] == 0
        """
        analytics.setdefault("quality_score", 0.5)
        analytics.setdefault("word_count", 0)
        analytics.setdefault("tag_count", 0)
        analytics.setdefault("link_count", 0)
        analytics.setdefault("success", True)
        return analytics

    @staticmethod
    def validate_ai_result(ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate AI enhancement result with required fields.

        Ensures AI results have success flag and default values for
        tags and summary when missing.

        Args:
            ai_result: AI enhancement result dict with:
                - success: Whether enhancement succeeded (default: False)
                - tags: List of AI-generated tags (default: [])
                - summary: AI-generated summary (default: '')

        Returns:
            Validated AI result dict with defaults

        Examples:
            >>> ai_result = {'tags': ['test', 'refactoring']}
            >>> validated = ResultValidator.validate_ai_result(ai_result)
            >>> assert validated['success'] == False
            >>> assert validated['summary'] == ''
        """
        ai_result.setdefault("success", False)
        ai_result.setdefault("tags", [])
        ai_result.setdefault("summary", "")
        return ai_result

    @staticmethod
    def validate_connections_result(connections: Any) -> list:
        """
        Validate connections result ensuring list type.

        Converts None or non-list connections results to empty list,
        preventing iteration errors.

        Args:
            connections: Connection discovery result (list, None, or other)

        Returns:
            List of connection dicts (empty list if None)

        Examples:
            >>> validated = ResultValidator.validate_connections_result(None)
            >>> assert validated == []

            >>> validated = ResultValidator.validate_connections_result([{'target': 'note.md'}])
            >>> assert len(validated) == 1
        """
        if connections is None or not isinstance(connections, list):
            return []
        return connections
