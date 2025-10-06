"""
Type Aliases for InnerOS AI Workflow Management

Provides semantic type aliases to replace generic Dict[str, Any] throughout the codebase,
improving readability and developer experience.

Design Principles:
- Semantic naming over generic types
- IDE autocomplete support
- Self-documenting code
- Consistent naming conventions
"""

from typing import Dict, Any, List

# ============================================================================
# Result Types - Return values from manager operations
# ============================================================================

# Analytics results from quality assessment, metrics calculation
AnalyticsResult = Dict[str, Any]

# AI enhancement results (tags, summary, quality assessment)
AIEnhancementResult = Dict[str, Any]

# Connection discovery results (link suggestions with scores)
ConnectionResult = List[Dict[str, Any]]

# Complete workflow processing results (combines all managers)
WorkflowResult = Dict[str, Any]

# ============================================================================
# Configuration Types - Input configuration objects
# ============================================================================

# Generic configuration dictionary
ConfigDict = Dict[str, Any]

# Quality scoring weights and thresholds
QualityMetrics = Dict[str, float]

# ============================================================================
# Link Types - Wiki-link and connection structures
# ============================================================================

# Single link suggestion with target, score, and explanation
LinkSuggestion = Dict[str, Any]

# User feedback on link acceptance/rejection
LinkFeedback = Dict[str, Any]

# ============================================================================
# Note Types - Note metadata and content structures
# ============================================================================

# Note metadata extracted from YAML frontmatter
NoteMetadata = Dict[str, Any]

# Complete note information (path, content, metadata)
NoteInfo = Dict[str, Any]

# ============================================================================
# Metrics Types - Aggregated analytics and reporting
# ============================================================================

# Workflow report with aggregated metrics
WorkflowReport = Dict[str, Any]

# Enhanced metrics with orphaned/stale detection
EnhancedMetrics = Dict[str, Any]

# ============================================================================
# Candidate Types - Review and promotion workflows
# ============================================================================

# Promotion candidate with quality score and rationale
PromotionCandidate = Dict[str, Any]

# Review candidates for weekly review automation
ReviewCandidate = List[Dict[str, Any]]
