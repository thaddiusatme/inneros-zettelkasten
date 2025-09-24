"""
RAG-Ready Tag Strategy Utilities - TDD Iteration 1 REFACTOR Phase

Extracted utility classes for modular architecture and reusability.
"""

import re
from typing import Dict, List, Set, Any, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TagAnalysisResult:
    """Structured result for tag analysis operations"""
    total_tags: int
    problematic_count: int
    cleanup_suggestions: Dict[str, List[str]]
    namespace_distribution: Dict[str, int]
    performance_metrics: Dict[str, float]
    

@dataclass 
class CleanupRule:
    """Represents a single tag cleanup rule"""
    rule_type: str  # canonicalization, merge, remove
    pattern: str
    replacement: str
    confidence: float
    rationale: str


class TagPatternMatcher:
    """Utility for matching tag patterns with optimized regex"""
    
    def __init__(self):
        # Precompiled regex patterns for performance
        self.metadata_pattern = re.compile(
            r'^(permanent|fleeting|literature|moc|project|inbox|draft|published|archived)$',
            re.IGNORECASE
        )
        self.ai_artifact_pattern = re.compile(
            r'(ai-generated|llm-output|auto-tagged|claude-response|gpt-generated|ollama-response|machine-generated)',
            re.IGNORECASE
        )
        self.invalid_chars_pattern = re.compile(r'[^a-zA-Z0-9\-_]')
        self.numeric_only_pattern = re.compile(r'^\d+$')
        
    def is_metadata_redundant(self, tag: str) -> bool:
        """Check if tag duplicates metadata field"""
        return bool(self.metadata_pattern.match(tag.strip()))
    
    def is_ai_artifact(self, tag: str) -> bool:
        """Check if tag is AI-generated artifact"""
        return bool(self.ai_artifact_pattern.search(tag.strip()))
    
    def has_parsing_errors(self, tag: str) -> bool:
        """Check if tag has parsing/formatting errors"""
        if not tag or not tag.strip():
            return True
        if self.numeric_only_pattern.match(tag.strip()):
            return True
        if self.invalid_chars_pattern.search(tag):
            return True
        return False


class SemanticTagGrouper:
    """Groups semantically similar tags using predefined patterns"""
    
    def __init__(self):
        self.semantic_groups = {
            "artificial-intelligence": ["ai", "artificial-intelligence", "machine-intelligence"],
            "machine-learning": ["ml", "machine-learning", "supervised-learning", "unsupervised-learning"],
            "deep-learning": ["deep-learning", "neural-networks", "artificial-neural-networks"],
            "productivity": ["productivity", "productivity-tools", "efficiency", "time-management"],
            "note-taking": ["note-taking", "notes", "knowledge-management", "pkm"],
            "programming": ["programming", "coding", "software-development", "development"],
            "research": ["research", "academic", "scholarly", "literature-review"],
            "business": ["business", "entrepreneurship", "startup", "enterprise"]
        }
        
        # Create reverse lookup for performance
        self.tag_to_canonical = {}
        for canonical, variants in self.semantic_groups.items():
            for variant in variants:
                self.tag_to_canonical[variant] = canonical
    
    def find_semantic_groups(self, tags: List[str]) -> List[List[str]]:
        """Find groups of semantically similar tags"""
        found_groups = []
        processed_tags = set()
        
        for canonical, variants in self.semantic_groups.items():
            found_variants = []
            for tag in tags:
                if tag.lower() in variants and tag not in processed_tags:
                    found_variants.append(tag)
                    processed_tags.add(tag)
            
            if len(found_variants) > 1:
                found_groups.append(found_variants)
        
        return found_groups
    
    def get_canonical_form(self, tag: str) -> str:
        """Get canonical form of tag if it has one"""
        return self.tag_to_canonical.get(tag.lower(), tag)


class NamespaceValidator:
    """Validates and enforces namespace conventions"""
    
    def __init__(self):
        self.valid_namespaces = {"type", "topic", "context"}
        self.namespace_pattern = re.compile(r'^(type|topic|context)/[a-z0-9\-]+$')
    
    def is_valid_namespaced_tag(self, tag: str) -> bool:
        """Check if tag follows namespace convention"""
        return bool(self.namespace_pattern.match(tag))
    
    def extract_namespace(self, tag: str) -> Tuple[str, str]:
        """Extract namespace and tag name from namespaced tag"""
        if '/' in tag:
            parts = tag.split('/', 1)
            if len(parts) == 2 and parts[0] in self.valid_namespaces:
                return parts[0], parts[1]
        return "", tag
    
    def create_namespaced_tag(self, namespace: str, tag: str) -> str:
        """Create properly formatted namespaced tag"""
        if namespace in self.valid_namespaces:
            clean_tag = re.sub(r'[^a-z0-9\-]', '-', tag.lower()).strip('-')
            return f"{namespace}/{clean_tag}"
        return tag


class TagStatisticsCalculator:
    """Calculates comprehensive tag statistics and metrics"""
    
    def calculate_cleanup_statistics(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate cleanup impact statistics"""
        total_tags = analysis_result.get("total_tags", 0)
        problematic = analysis_result.get("total_problematic", 0)
        
        if total_tags == 0:
            return {"cleanup_percentage": 0, "impact_score": 0}
        
        cleanup_percentage = (problematic / total_tags) * 100
        impact_score = min(cleanup_percentage / 50, 1.0)  # Normalized 0-1 score
        
        return {
            "cleanup_percentage": cleanup_percentage,
            "impact_score": impact_score,
            "tags_to_remove": problematic,
            "tags_to_keep": total_tags - problematic,
            "efficiency_gain": cleanup_percentage * 0.8  # Estimated efficiency improvement
        }
    
    def calculate_namespace_distribution(self, classifications: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calculate namespace distribution statistics"""
        distribution = {"type": 0, "topic": 0, "context": 0}
        
        for classification in classifications:
            namespace = classification.get("namespace", "topic")
            distribution[namespace] += 1
        
        total = sum(distribution.values())
        percentages = {k: (v / total * 100) if total > 0 else 0 for k, v in distribution.items()}
        
        return {
            "counts": distribution,
            "percentages": percentages,
            "total": total,
            "balance_score": self._calculate_balance_score(percentages)
        }
    
    def _calculate_balance_score(self, percentages: Dict[str, float]) -> float:
        """Calculate how balanced the namespace distribution is (0-1 score)"""
        # Ideal distribution might be 30% type, 50% topic, 20% context
        ideal = {"type": 30, "topic": 50, "context": 20}
        
        deviation = sum(abs(percentages[k] - ideal[k]) for k in percentages)
        return max(0, 1 - (deviation / 200))  # Normalize to 0-1


class RuleGenerationEngine:
    """Generates intelligent cleanup rules based on vault analysis"""
    
    def __init__(self):
        self.pattern_matcher = TagPatternMatcher()
        self.semantic_grouper = SemanticTagGrouper()
        self.statistics_calculator = TagStatisticsCalculator()
    
    def generate_comprehensive_rules(self, vault_tags: List[str]) -> Dict[str, Any]:
        """Generate comprehensive cleanup rules from vault analysis"""
        
        # Analyze current tags
        metadata_redundant = [tag for tag in vault_tags if self.pattern_matcher.is_metadata_redundant(tag)]
        ai_artifacts = [tag for tag in vault_tags if self.pattern_matcher.is_ai_artifact(tag)]
        parsing_errors = [tag for tag in vault_tags if self.pattern_matcher.has_parsing_errors(tag)]
        semantic_groups = self.semantic_grouper.find_semantic_groups(vault_tags)
        
        # Generate canonicalization rules
        canonicalization = {}
        for tag in vault_tags:
            canonical = self.semantic_grouper.get_canonical_form(tag)
            if canonical != tag:
                canonicalization[tag] = canonical
        
        # Generate merge rules
        merges = {}
        for group in semantic_groups:
            if len(group) > 1:
                canonical = self.semantic_grouper.get_canonical_form(group[0])
                merges[canonical] = group
        
        # Generate cleanup patterns
        cleanup_patterns = {
            "remove_metadata_duplicates": len(metadata_redundant) > 0,
            "remove_ai_artifacts": len(ai_artifacts) > 0,
            "fix_parsing_errors": len(parsing_errors) > 0,
            "merge_semantic_duplicates": len(semantic_groups) > 0
        }
        
        return {
            "canonicalization": canonicalization,
            "merges": merges,
            "namespace_mappings": self._generate_namespace_mappings(vault_tags),
            "cleanup_patterns": cleanup_patterns,
            "removal_candidates": metadata_redundant + ai_artifacts + parsing_errors,
            "statistics": {
                "total_rules": len(canonicalization) + len(merges),
                "cleanup_impact": len(metadata_redundant + ai_artifacts + parsing_errors),
                "merge_impact": sum(len(group) - 1 for group in semantic_groups)
            }
        }
    
    def _generate_namespace_mappings(self, vault_tags: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Generate namespace mapping suggestions"""
        type_tags = [tag for tag in vault_tags if self.pattern_matcher.is_metadata_redundant(tag)]
        
        # Simple heuristics for demonstration
        topic_indicators = ["quantum", "ai", "machine", "deep", "neural", "computing", "technology"]
        context_indicators = ["inbox", "draft", "review", "priority", "urgent", "scheduled"]
        
        topic_tags = [tag for tag in vault_tags if any(indicator in tag.lower() for indicator in topic_indicators)]
        context_tags = [tag for tag in vault_tags if any(indicator in tag.lower() for indicator in context_indicators)]
        
        return {
            "type": {"suggested": type_tags, "confidence": 0.9},
            "topic": {"suggested": topic_tags, "confidence": 0.7}, 
            "context": {"suggested": context_tags, "confidence": 0.8}
        }
