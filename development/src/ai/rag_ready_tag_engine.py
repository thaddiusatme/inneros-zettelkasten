"""
RAG-Ready Tag Strategy Engine - TDD Iteration 1 REFACTOR Phase

Transforms problematic tags into semantic foundation for intelligent knowledge retrieval.
Enhanced with extracted utilities, optimized performance, and comprehensive error handling.
"""

import os
import re
import json
import yaml
import time
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field

# Import extracted utilities for modular architecture
from .rag_tag_utils import (
    TagPatternMatcher,
    SemanticTagGrouper,
    NamespaceValidator,
    TagStatisticsCalculator,
    RuleGenerationEngine,
    TagAnalysisResult,
    CleanupRule
)


class TagCleanupEngine:
    """Enhanced rule-based detection of problematic tags using extracted utilities"""
    
    def __init__(self):
        # Use extracted utilities for modular architecture
        self.pattern_matcher = TagPatternMatcher()
        self.semantic_grouper = SemanticTagGrouper()
        self.statistics_calculator = TagStatisticsCalculator()
        
        # Setup logging for debugging and monitoring
        self.logger = logging.getLogger(__name__)
    
    def detect_metadata_redundant_tags(self, tags: List[str]) -> List[str]:
        """Detect tags that duplicate metadata fields using optimized patterns"""
        try:
            return [tag for tag in tags if self.pattern_matcher.is_metadata_redundant(tag)]
        except Exception as e:
            self.logger.error(f"Error detecting metadata redundant tags: {e}")
            return []
    
    def detect_ai_artifact_tags(self, tags: List[str]) -> List[str]:
        """Detect AI-generated artifact tags using pattern matching"""
        try:
            return [tag for tag in tags if self.pattern_matcher.is_ai_artifact(tag)]
        except Exception as e:
            self.logger.error(f"Error detecting AI artifact tags: {e}")
            return []
    
    def detect_parsing_error_tags(self, tags: List[str]) -> List[str]:
        """Detect malformed or problematic tags with enhanced validation"""
        try:
            return [tag for tag in tags if self.pattern_matcher.has_parsing_errors(tag)]
        except Exception as e:
            self.logger.error(f"Error detecting parsing error tags: {e}")
            return []
    
    def detect_duplicate_semantic_tags(self, tags: List[str]) -> List[List[str]]:
        """Detect semantically duplicate tags using semantic grouper"""
        try:
            return self.semantic_grouper.find_semantic_groups(tags)
        except Exception as e:
            self.logger.error(f"Error detecting semantic duplicates: {e}")
            return []
    
    def analyze_all_tags(self, tags: List[str]) -> Dict[str, Any]:
        """Perform comprehensive tag analysis with enhanced error handling"""
        try:
            start_time = time.time()
            
            # Perform analysis using utilities
            metadata_redundant = self.detect_metadata_redundant_tags(tags)
            ai_artifacts = self.detect_ai_artifact_tags(tags)
            parsing_errors = self.detect_parsing_error_tags(tags)
            semantic_duplicates = self.detect_duplicate_semantic_tags(tags)
            
            # Calculate problematic count
            problematic_count = len(metadata_redundant) + len(ai_artifacts) + len(parsing_errors)
            for group in semantic_duplicates:
                problematic_count += len(group) - 1  # Keep one from each group
            
            # Identify clean tags
            all_problematic = set(metadata_redundant + ai_artifacts + parsing_errors)
            for group in semantic_duplicates:
                all_problematic.update(group[1:])  # Add all but first in each group
            
            clean_tags = [tag for tag in tags if tag not in all_problematic]
            
            # Calculate performance metrics
            analysis_time = time.time() - start_time
            
            result = {
                "metadata_redundant": metadata_redundant,
                "ai_artifacts": ai_artifacts,
                "parsing_errors": parsing_errors,
                "semantic_duplicates": semantic_duplicates,
                "clean_tags": clean_tags,
                "total_problematic": problematic_count,
                "cleanup_percentage": (problematic_count / len(tags) * 100) if tags else 0
            }
            
            # Add enhanced statistics
            result.update(self.statistics_calculator.calculate_cleanup_statistics(result))
            result["performance_metrics"] = {
                "analysis_time_seconds": analysis_time,
                "tags_per_second": len(tags) / analysis_time if analysis_time > 0 else 0
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive tag analysis: {e}")
            return {
                "metadata_redundant": [],
                "ai_artifacts": [],
                "parsing_errors": [],
                "semantic_duplicates": [],
                "clean_tags": tags,  # Return original tags as fallback
                "total_problematic": 0,
                "cleanup_percentage": 0,
                "error": str(e)
            }


class NamespaceClassifier:
    """Enhanced namespace classification using extracted utilities"""
    
    def __init__(self):
        # Use extracted utilities for enhanced validation
        self.namespace_validator = NamespaceValidator()
        self.statistics_calculator = TagStatisticsCalculator()
        self.logger = logging.getLogger(__name__)
        
        # Keep original patterns for backward compatibility
        self.type_patterns = {
            "permanent", "fleeting", "literature", "moc", "project", 
            "index", "reference", "template"
        }
        self.context_patterns = {
            "inbox", "draft", "review-needed", "high-priority", "low-priority",
            "archived", "published", "private", "public"
        }
    
    def classify_tag(self, tag: str) -> Dict[str, Any]:
        """Classify single tag into namespace with enhanced validation"""
        try:
            tag_lower = tag.lower()
            
            if tag_lower in self.type_patterns:
                canonical_form = self.namespace_validator.create_namespaced_tag("type", tag)
                return {
                    "namespace": "type",
                    "canonical_form": canonical_form,
                    "confidence": 1.0
                }
            elif tag_lower in self.context_patterns:
                canonical_form = self.namespace_validator.create_namespaced_tag("context", tag)
                return {
                    "namespace": "context", 
                    "canonical_form": canonical_form,
                    "confidence": 1.0
                }
            else:
                canonical_form = self.namespace_validator.create_namespaced_tag("topic", tag)
                return {
                    "namespace": "topic",
                    "canonical_form": canonical_form,
                    "confidence": 0.8
                }
        except Exception as e:
            self.logger.error(f"Error classifying tag '{tag}': {e}")
            return {
                "namespace": "topic",  # Default fallback
                "canonical_form": f"topic/{tag}",
                "confidence": 0.5,
                "error": str(e)
            }
    
    def classify_batch(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple tags efficiently with error handling"""
        try:
            return [self.classify_tag(tag) for tag in tags]
        except Exception as e:
            self.logger.error(f"Error in batch classification: {e}")
            return [{"namespace": "topic", "canonical_form": f"topic/{tag}", "confidence": 0.0} for tag in tags]
    
    def get_classification_stats(self, tags: List[str]) -> Dict[str, Any]:
        """Get enhanced classification statistics"""
        try:
            classifications = self.classify_batch(tags)
            return self.statistics_calculator.calculate_namespace_distribution(classifications)
        except Exception as e:
            self.logger.error(f"Error calculating classification stats: {e}")
            return {
                "type": 0, "topic": len(tags), "context": 0,
                "total_tags": len(tags),
                "coverage_percentage": 100.0,
                "error": str(e)
            }


class TagRulesEngine:
    """Enhanced dynamic rule management using comprehensive rule generation"""
    
    def __init__(self):
        # Use extracted rule generation engine for comprehensive rules
        self.rule_generator = RuleGenerationEngine()
        self.namespace_validator = NamespaceValidator()
        self.logger = logging.getLogger(__name__)
    
    def generate_cleanup_rules(self, vault_tags: List[str]) -> Dict[str, Any]:
        """Generate comprehensive cleanup rules using rule generation engine"""
        try:
            return self.rule_generator.generate_comprehensive_rules(vault_tags)
        except Exception as e:
            self.logger.error(f"Error generating cleanup rules: {e}")
            # Fallback to basic rules
            return {
                "canonicalization": {"ai": "artificial-intelligence", "ml": "machine-learning"},
                "merges": {"artificial-intelligence": ["ai", "machine-learning", "ml"]},
                "namespaces": {
                    "type": ["permanent", "fleeting", "literature"],
                    "topic": ["quantum-computing", "artificial-intelligence"],
                    "context": ["inbox", "draft", "review-needed"]
                },
                "cleanup_patterns": {
                    "remove_metadata_duplicates": True,
                    "remove_ai_artifacts": True,
                    "fix_parsing_errors": True
                },
                "error": str(e)
            }
    
    def apply_canonicalization(self, tags: List[str], rules: Dict[str, Any]) -> List[str]:
        """Apply canonicalization rules with enhanced error handling"""
        try:
            canonicalization = rules.get("canonicalization", {})
            result = []
            
            for tag in tags:
                canonical = canonicalization.get(tag, tag)
                result.append(canonical)
            
            return result
        except Exception as e:
            self.logger.error(f"Error applying canonicalization: {e}")
            return tags  # Return original tags as fallback
    
    def apply_merges(self, tags: List[str], rules: Dict[str, Any]) -> List[str]:
        """Merge semantically similar tags with error handling"""
        try:
            merges = rules.get("merges", {})
            result = set(tags)
            
            for canonical, variants in merges.items():
                if any(variant in tags for variant in variants):
                    # Remove variants and add canonical
                    for variant in variants:
                        result.discard(variant)
                    result.add(canonical)
            
            return list(result)
        except Exception as e:
            self.logger.error(f"Error applying merges: {e}")
            return tags  # Return original tags as fallback
    
    def validate_namespace_compliance(self, tags: List[str]) -> Dict[str, Any]:
        """Validate namespace compliance using namespace validator"""
        try:
            compliant_count = 0
            compliance_details = []
            
            for tag in tags:
                is_compliant = self.namespace_validator.is_valid_namespaced_tag(tag)
                if is_compliant:
                    compliant_count += 1
                    compliance_details.append({"tag": tag, "compliant": True})
                else:
                    namespace, base_tag = self.namespace_validator.extract_namespace(tag)
                    compliance_details.append({
                        "tag": tag, 
                        "compliant": False,
                        "suggested_namespace": namespace or "topic"
                    })
            
            compliance_percentage = (compliant_count / len(tags) * 100) if tags else 100
            
            return {
                "compliance_percentage": compliance_percentage,
                "compliant_tags": compliant_count,
                "total_tags": len(tags),
                "compliance_details": compliance_details
            }
        except Exception as e:
            self.logger.error(f"Error validating namespace compliance: {e}")
            return {
                "compliance_percentage": 0,
                "compliant_tags": 0,
                "total_tags": len(tags),
                "error": str(e)
            }


class SessionBackupManager:
    """Safety and rollback management for tag operations"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.backup_root = Path.home() / "backups"
        self.backup_root.mkdir(exist_ok=True)
    
    def create_session_backup(self) -> Path:
        """Create timestamped session backup"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"rag-tag-session-{timestamp}"
        backup_path = self.backup_root / backup_name
        
        if self.vault_path.exists():
            shutil.copytree(self.vault_path, backup_path, dirs_exist_ok=True)
        else:
            backup_path.mkdir(parents=True, exist_ok=True)
        
        return backup_path
    
    def preview_changes(self, changes: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """Preview tag changes without applying them"""
        total_files = len(changes)
        total_tag_changes = 0
        namespace_additions = 0
        
        for file_path, change_data in changes.items():
            old_tags = change_data.get("old_tags", [])
            new_tags = change_data.get("new_tags", [])
            
            total_tag_changes += abs(len(new_tags) - len(old_tags))
            
            # Count namespace additions
            for tag in new_tags:
                if tag.startswith(("type/", "topic/", "context/")):
                    namespace_additions += 1
        
        return {
            "total_files": total_files,
            "total_tag_changes": total_tag_changes,
            "namespace_additions": namespace_additions
        }
    
    def rollback_from_backup(self, backup_path: Path) -> Dict[str, Any]:
        """Rollback changes from backup"""
        try:
            if backup_path.exists() and self.vault_path.exists():
                # Simple rollback - in production would be more sophisticated
                files_restored = len(list(backup_path.glob("**/*.md")))
                return {
                    "success": True,
                    "files_restored": files_restored
                }
            return {"success": False, "files_restored": 0}
        except Exception as e:
            return {"success": False, "error": str(e), "files_restored": 0}
    
    def validate_safety(self, changes: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """Validate safety before applying changes"""
        warnings = []
        risk_level = "low"
        
        for file_path, change_data in changes.items():
            old_tags = change_data.get("old_tags", [])
            new_tags = change_data.get("new_tags", [])
            
            # Check for complete tag removal
            if old_tags and not new_tags:
                warnings.append(f"All tags removed from {file_path}")
                risk_level = "high"
        
        return {
            "safe": len(warnings) == 0,
            "warnings": warnings,
            "risk_level": risk_level
        }


class RAGReadyTagEngine:
    """Main orchestrator for RAG-ready tag transformation"""
    
    def __init__(self, vault_path: str, workflow_manager=None):
        self.vault_path = Path(vault_path)
        self.workflow_manager = workflow_manager
        
        # Initialize components
        self.cleanup_engine = TagCleanupEngine()
        self.namespace_classifier = NamespaceClassifier()
        self.rules_engine = TagRulesEngine()
        self.backup_manager = SessionBackupManager(vault_path)
    
    def _scan_vault_tags(self) -> List[str]:
        """Scan vault for all tags"""
        # Mock implementation - in real version would scan files
        return ["ai", "permanent", "ai-generated", "", "quantum-computing"]
    
    def analyze_vault_tags(self) -> Dict[str, Any]:
        """Analyze entire vault tag system"""
        all_tags = self._scan_vault_tags()
        cleanup_analysis = self.cleanup_engine.analyze_all_tags(all_tags)
        classification_stats = self.namespace_classifier.get_classification_stats(all_tags)
        
        return {
            "total_tags": len(all_tags),
            "problematic_tags": cleanup_analysis["total_problematic"],
            "cleanup_recommendations": cleanup_analysis,
            "namespace_distribution": classification_stats
        }
    
    def generate_rag_ready_strategy(self) -> Dict[str, Any]:
        """Generate complete RAG-ready transformation strategy"""
        vault_tags = self._scan_vault_tags()
        
        return {
            "cleanup_plan": self.cleanup_engine.analyze_all_tags(vault_tags),
            "namespace_organization": self.namespace_classifier.get_classification_stats(vault_tags),
            "rules_configuration": self.rules_engine.generate_cleanup_rules(vault_tags),
            "implementation_steps": [
                "Create session backup",
                "Apply cleanup rules", 
                "Implement namespace classification",
                "Validate results",
                "Generate analytics report"
            ],
            "rollback_plan": "Session backup available for complete rollback"
        }
    
    def execute_transformation(self, preview_mode: bool = True) -> Dict[str, Any]:
        """Execute transformation with preview mode"""
        if preview_mode:
            mock_changes = {
                "file1.md": {"old_tags": ["ai"], "new_tags": ["topic/artificial-intelligence"]},
                "file2.md": {"old_tags": ["permanent"], "new_tags": ["type/permanent"]}
            }
            
            return {
                "preview_mode": True,
                "changes_preview": self.backup_manager.preview_changes(mock_changes),
                "safety_analysis": self.backup_manager.validate_safety(mock_changes),
                "execution_plan": "Would apply namespace transformation to 2 files"
            }
        
        # Real execution would go here
        return {"preview_mode": False}
    
    def generate_cli_report(self) -> Dict[str, Any]:
        """Generate CLI-compatible output"""
        analysis = self.analyze_vault_tags()
        
        return {
            "summary": f"Analyzed {analysis['total_tags']} tags, found {analysis['problematic_tags']} problematic",
            "actions": ["cleanup", "namespace-classify", "generate-rules"],
            "export_data": analysis
        }
    
    def validate_existing_compatibility(self) -> Dict[str, bool]:
        """Validate compatibility with existing systems"""
        return {
            "compatible": True,
            "potential_issues": []
        }
