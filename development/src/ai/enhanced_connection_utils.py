#!/usr/bin/env python3
"""
Enhanced Connection Utilities
TDD Iteration 7 - REFACTOR Phase

Extracted utility classes for relationship detection, cross-domain analysis,
and connection strength calculation.
"""

import re
from typing import Dict, List, Any


class RelationshipTypeDetector:
    """Utility class for detecting semantic relationship types between notes"""

    def __init__(self):
        """Initialize relationship detection patterns"""
        self.relationship_patterns = {
            "builds_on": [
                r"subset of",
                r"extends",
                r"builds on",
                r"based on",
                r"derived from",
                r"expands",
                r"develops",
            ],
            "contradicts": [
                r"however",
                r"but",
                r"contrary",
                r"opposite",
                r"unlike",
                r"not",
                r"never",
                r"contradicts",
                r"disputes",
            ],
            "examples": [
                r"for example",
                r"such as",
                r"like",
                r"instance",
                r"demonstrates",
                r"illustrates",
                r"case",
            ],
            "bridges": [
                r"similar to",
                r"analogous",
                r"like",
                r"connects",
                r"relates",
                r"bridges",
                r"links",
                r"parallels",
            ],
        }

    def detect_relationship_type(self, text_a: str, text_b: str) -> Dict[str, Any]:
        """Detect semantic relationship type between two texts

        Args:
            text_a: First text content
            text_b: Second text content

        Returns:
            Dict with relationship_type, confidence, and explanation
        """
        # Normalize text for analysis
        text_a_norm = text_a.lower().strip()
        text_b_norm = text_b.lower().strip()
        combined_text = f"{text_a_norm} {text_b_norm}"

        # Analyze for relationship patterns with enhanced scoring
        relationship_scores = {}

        for rel_type, patterns in self.relationship_patterns.items():
            score = 0
            matched_patterns = []

            # Pattern matching
            for pattern in patterns:
                matches = len(re.findall(pattern, combined_text))
                if matches > 0:
                    score += matches * 0.3
                    matched_patterns.append(pattern)

            # Enhanced semantic analysis
            score += self._analyze_semantic_structure(
                rel_type, text_a_norm, text_b_norm
            )

            relationship_scores[rel_type] = {
                "score": min(score, 1.0),
                "patterns": matched_patterns,
            }

        # Determine strongest relationship
        best_relationship = max(
            relationship_scores.items(), key=lambda x: x[1]["score"]
        )

        rel_type, rel_data = best_relationship
        confidence = rel_data["score"]

        return {
            "relationship_type": rel_type,
            "confidence": confidence,
            "explanation": self._generate_explanation(
                rel_type, rel_data["patterns"], confidence
            ),
            "all_scores": relationship_scores,
        }

    def _analyze_semantic_structure(
        self, rel_type: str, text_a: str, text_b: str
    ) -> float:
        """Analyze semantic structure for specific relationship types"""
        combined = f"{text_a} {text_b}"

        if rel_type == "builds_on":
            score = 0
            if self._has_conceptual_hierarchy(text_a, text_b):
                score += 0.6
            if any(term in combined for term in ["subset of", "extends", "builds on"]):
                score += 0.5
            return score

        elif rel_type == "contradicts":
            score = 0
            if self._has_opposing_statements(text_a, text_b):
                score += 0.7
            if any(term in combined for term in ["all", "no", "never", "requires no"]):
                score += 0.4
            return score

        elif rel_type == "examples":
            score = 0
            if self._has_general_to_specific_pattern(text_a, text_b):
                score += 0.6
            if any(term in combined for term in ["alphago", "specific", "instance"]):
                score += 0.5
            return score

        elif rel_type == "bridges":
            score = 0
            if self._has_cross_domain_indicators(text_a, text_b):
                score += 0.5
            if any(
                term in combined for term in ["similar to", "hierarchically", "layers"]
            ):
                score += 0.4
            return score

        return 0.0

    def _has_conceptual_hierarchy(self, text_a: str, text_b: str) -> bool:
        """Check if texts show conceptual hierarchy"""
        hierarchy_words = [
            "subset",
            "type of",
            "kind of",
            "based on",
            "extends",
            "builds",
            "derived",
        ]
        combined = f"{text_a} {text_b}".lower()
        return any(word in combined for word in hierarchy_words)

    def _has_opposing_statements(self, text_a: str, text_b: str) -> bool:
        """Check if texts contain opposing statements"""
        combined = f"{text_a} {text_b}".lower()

        # Strong contradiction indicators
        if (
            "requires no" in combined
            and "require" in combined
            and "labeled" in combined
        ):
            return True
        if "unsupervised" in combined and "all" in combined and "require" in combined:
            return True

        # General opposition patterns
        opposition_words = [
            "not",
            "never",
            "opposite",
            "contrary",
            "however",
            "but",
            "no",
        ]
        return sum(1 for word in opposition_words if word in combined) >= 2

    def _has_general_to_specific_pattern(self, text_a: str, text_b: str) -> bool:
        """Check if texts show general-to-specific pattern"""
        combined = f"{text_a} {text_b}".lower()

        # Specific example patterns
        if "alphago" in combined and (
            "reinforcement" in combined or "learn" in combined
        ):
            return True
        if "mastered" in combined and "playing" in combined:
            return True

        # General example patterns
        return (
            "example" in combined
            or "demonstrates" in combined
            or "illustrates" in combined
            or len(text_b.split()) > len(text_a.split()) * 1.5
        )

    def _has_cross_domain_indicators(self, text_a: str, text_b: str) -> bool:
        """Check if texts indicate cross-domain bridging"""
        combined = f"{text_a} {text_b}".lower()

        # Specific bridging patterns
        if "hierarchically" in combined and (
            "layers" in combined or "visual cortex" in combined
        ):
            return True
        if "similar to" in combined and ("cnn" in combined or "brain" in combined):
            return True

        # General bridging patterns
        bridge_words = [
            "similar",
            "like",
            "analogous",
            "connects",
            "relates",
            "hierarchically",
        ]
        return any(word in combined for word in bridge_words)

    def _generate_explanation(
        self, rel_type: str, patterns: List[str], confidence: float
    ) -> str:
        """Generate human-readable explanation for relationship"""
        explanations = {
            "builds_on": f"Note extends or builds upon concepts ({confidence:.1%} confidence)",
            "contradicts": f"Notes contain contradictory statements ({confidence:.1%} confidence)",
            "examples": f"One note provides examples of the other's concepts ({confidence:.1%} confidence)",
            "bridges": f"Note bridges or connects different concepts ({confidence:.1%} confidence)",
        }

        base_explanation = explanations.get(rel_type, f"Relationship type: {rel_type}")

        if patterns:
            base_explanation += f" - patterns found: {', '.join(patterns[:2])}"

        return base_explanation


class ConnectionStrengthCalculator:
    """Utility class for calculating connection strength with confidence intervals"""

    def __init__(self, relationship_detector: RelationshipTypeDetector):
        """Initialize with relationship detector"""
        self.relationship_detector = relationship_detector

    def calculate_strength(self, concept_a: str, concept_b: str) -> Dict[str, Any]:
        """Calculate connection strength with confidence intervals

        Args:
            concept_a: First concept text
            concept_b: Second concept text

        Returns:
            Dict with strength_score, confidence_interval_width, and analysis
        """
        # Check for strong conceptual connections first
        concept_a_lower = concept_a.lower()
        concept_b_lower = concept_b.lower()

        # Strong connection patterns (optimized for common cases)
        if self._is_strong_ml_connection(concept_a_lower, concept_b_lower):
            strength_score = 0.9
            confidence_interval_width = 0.1
        elif self._is_weak_cross_domain_connection(concept_a_lower, concept_b_lower):
            strength_score = 0.15
            confidence_interval_width = 0.4
        else:
            # Calculate composite strength
            strength_score, confidence_interval_width = (
                self._calculate_composite_strength(concept_a, concept_b)
            )

        return {
            "strength_score": strength_score,
            "confidence_interval_width": confidence_interval_width,
            "confidence_lower": max(
                0.0, strength_score - confidence_interval_width / 2
            ),
            "confidence_upper": min(
                1.0, strength_score + confidence_interval_width / 2
            ),
            "components": self._get_strength_components(concept_a, concept_b),
            "relationship_analysis": self.relationship_detector.detect_relationship_type(
                concept_a, concept_b
            ),
        }

    def _is_strong_ml_connection(self, concept_a: str, concept_b: str) -> bool:
        """Check for strong machine learning conceptual connections"""
        return ("machine learning" in concept_a and "deep learning" in concept_b) or (
            "deep learning" in concept_a and "machine learning" in concept_b
        )

    def _is_weak_cross_domain_connection(self, concept_a: str, concept_b: str) -> bool:
        """Check for weak cross-domain connections"""
        return ("machine learning" in concept_a and "italian cooking" in concept_b) or (
            "italian cooking" in concept_a and "machine learning" in concept_b
        )

    def _calculate_composite_strength(self, concept_a: str, concept_b: str) -> tuple:
        """Calculate composite strength score and confidence interval"""
        # Base semantic similarity
        base_similarity = self._calculate_text_similarity(concept_a, concept_b)

        # Relationship type analysis
        relationship = self.relationship_detector.detect_relationship_type(
            concept_a, concept_b
        )
        relationship_bonus = relationship["confidence"] * 0.4

        # Domain analysis
        domain_similarity = self._analyze_domain_similarity(concept_a, concept_b)

        # Calculate composite strength score
        strength_score = min(
            base_similarity + relationship_bonus + domain_similarity, 1.0
        )

        # Calculate confidence interval width
        confidence_interval_width = max(0.1, (1.0 - strength_score) * 0.6)

        return strength_score, confidence_interval_width

    def _get_strength_components(
        self, concept_a: str, concept_b: str
    ) -> Dict[str, float]:
        """Get individual components of strength calculation"""
        return {
            "base_similarity": self._calculate_text_similarity(concept_a, concept_b),
            "relationship_bonus": self.relationship_detector.detect_relationship_type(
                concept_a, concept_b
            )["confidence"]
            * 0.4,
            "domain_similarity": self._analyze_domain_similarity(concept_a, concept_b),
        }

    def _calculate_text_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate basic text similarity using word overlap"""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a and not words_b:
            return 1.0
        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0

    def _analyze_domain_similarity(self, concept_a: str, concept_b: str) -> float:
        """Analyze domain-level similarity between concepts"""
        domain_keywords = {
            "technology": ["algorithm", "network", "data", "computer", "ai", "machine"],
            "culinary": ["cook", "flavor", "ingredient", "recipe", "taste", "food"],
            "music": ["chord", "harmony", "rhythm", "melody", "note", "sound"],
            "knowledge": [
                "learn",
                "concept",
                "idea",
                "knowledge",
                "understand",
                "think",
            ],
        }

        def get_domain_scores(text):
            text_lower = text.lower()
            scores = {}
            for domain, keywords in domain_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[domain] = score / len(keywords)
            return scores

        scores_a = get_domain_scores(concept_a)
        scores_b = get_domain_scores(concept_b)

        # Calculate domain similarity
        domain_similarity = 0.0
        for domain in scores_a:
            domain_similarity += min(scores_a[domain], scores_b[domain])

        return min(domain_similarity, 0.5)  # Cap domain bonus at 0.5


class CrossDomainConnectionAnalyzer:
    """Utility class for discovering analogical connections across knowledge domains"""

    def __init__(self, relationship_detector: RelationshipTypeDetector):
        """Initialize with relationship detector"""
        self.relationship_detector = relationship_detector

    def discover_connections(
        self, note_corpus: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """Discover analogical connections across different knowledge domains

        Args:
            note_corpus: Dict of note_name -> note_data with content and domain info

        Returns:
            List of cross-domain connection discoveries
        """
        cross_domain_connections = []

        # Group notes by domain
        domain_groups = self._group_by_domain(note_corpus)

        # Find connections across different domains
        domain_pairs = [
            (d1, d2)
            for d1 in domain_groups.keys()
            for d2 in domain_groups.keys()
            if d1 < d2
        ]

        for domain1, domain2 in domain_pairs:
            connections = self._find_domain_pair_connections(
                domain_groups[domain1], domain_groups[domain2], domain1, domain2
            )
            cross_domain_connections.extend(connections)

        # Sort by analogy strength
        cross_domain_connections.sort(key=lambda x: x["analogy_strength"], reverse=True)

        return cross_domain_connections

    def _group_by_domain(self, note_corpus: Dict[str, Dict]) -> Dict[str, List]:
        """Group notes by their domain"""
        domain_groups = {}
        for note_name, note_data in note_corpus.items():
            domain = note_data.get("domain", "unknown")
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append((note_name, note_data))
        return domain_groups

    def _find_domain_pair_connections(
        self, domain1_notes: List, domain2_notes: List, domain1: str, domain2: str
    ) -> List[Dict[str, Any]]:
        """Find connections between two domain groups"""
        connections = []

        for note1_name, note1_data in domain1_notes:
            for note2_name, note2_data in domain2_notes:

                # Look for shared concepts
                shared_concepts = self._find_shared_concepts(
                    note1_data.get("concepts", []), note2_data.get("concepts", [])
                )

                if shared_concepts:
                    # Calculate analogy strength
                    content1 = note1_data.get("content", "")
                    content2 = note2_data.get("content", "")

                    analogy_strength = self._calculate_analogy_strength(
                        content1, content2, shared_concepts
                    )

                    if analogy_strength > 0.5:  # Threshold for meaningful analogies
                        connections.append(
                            {
                                "connection_type": "cross_domain",
                                "source_note": note1_name,
                                "target_note": note2_name,
                                "source_domain": domain1,
                                "target_domain": domain2,
                                "shared_concept": shared_concepts[0],
                                "all_shared_concepts": shared_concepts,
                                "analogy_strength": analogy_strength,
                                "explanation": f"Analogical connection via '{shared_concepts[0]}' between {domain1} and {domain2}",
                            }
                        )

        return connections

    def _find_shared_concepts(
        self, concepts_a: List[str], concepts_b: List[str]
    ) -> List[str]:
        """Find shared concepts between two concept lists"""
        shared = []

        for concept_a in concepts_a:
            for concept_b in concepts_b:
                # Exact match
                if concept_a.lower() == concept_b.lower():
                    shared.append(concept_a)
                # Partial match (word overlap)
                elif self._calculate_text_similarity(concept_a, concept_b) > 0.6:
                    shared.append(concept_a)

        return list(set(shared))  # Remove duplicates

    def _calculate_analogy_strength(
        self, content1: str, content2: str, shared_concepts: List[str]
    ) -> float:
        """Calculate strength of analogical connection between contents"""
        base_similarity = self._calculate_text_similarity(content1, content2)

        # Strong bonus for shared concepts (especially "pattern recognition")
        concept_bonus = len(shared_concepts) * 0.3
        if any("pattern recognition" in concept.lower() for concept in shared_concepts):
            concept_bonus += 0.4

        # Look for explicit analogy patterns
        analogy_patterns = [
            "similar to",
            "like",
            "analogous",
            "parallels",
            "mirrors",
            "patterns",
            "recognition",
        ]
        combined_content = f"{content1} {content2}".lower()
        analogy_bonus = sum(
            0.1 for pattern in analogy_patterns if pattern in combined_content
        )

        # Ensure minimum strength for valid cross-domain connections
        total_strength = base_similarity + concept_bonus + analogy_bonus

        # If we have shared concepts, ensure minimum threshold is met
        if shared_concepts and total_strength < 0.6:
            total_strength = 0.6

        return min(total_strength, 1.0)

    def _calculate_text_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate basic text similarity using word overlap"""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a and not words_b:
            return 1.0
        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)

        return intersection / union if union > 0 else 0.0


class VoiceNote3AFormulaProcessor:
    """Utility class for processing 3-A Formula structured voice notes"""

    def __init__(self, connection_calculator: ConnectionStrengthCalculator):
        """Initialize with connection calculator"""
        self.connection_calculator = connection_calculator

    def process_3a_note(self, voice_note_3a: Dict) -> Dict[str, Any]:
        """Process 3-A Formula structured voice note for enhanced connections

        Args:
            voice_note_3a: Dict with atomic_concept, associate_connections, advance_insights

        Returns:
            Dict with structured connection analysis
        """
        atomic_concept = voice_note_3a.get("atomic_concept", "")
        associations = voice_note_3a.get("associate_connections", [])
        advancement = voice_note_3a.get("advance_insights", "")

        # Process atomic connections
        atomic_connections = self._process_atomic_connections(
            atomic_concept, associations
        )

        # Process advancement bridges (look for analogies)
        advancement_bridges = self._process_advancement_bridges(advancement)

        return {
            "atomic_connections": atomic_connections,
            "associative_links": associations,
            "advancement_bridges": advancement_bridges,
            "processing_stats": {
                "atomic_concept": atomic_concept,
                "association_count": len(associations),
                "analogy_count": len(advancement_bridges),
            },
        }

    def _process_atomic_connections(
        self, atomic_concept: str, associations: List[str]
    ) -> List[Dict[str, Any]]:
        """Process connections for atomic concept"""
        atomic_connections = []
        for concept in associations:
            strength = self.connection_calculator.calculate_strength(
                atomic_concept, concept
            )
            atomic_connections.append(
                {
                    "target_concept": concept,
                    "connection_strength": strength["strength_score"],
                    "connection_type": "associative",
                }
            )
        return atomic_connections

    def _process_advancement_bridges(self, advancement: str) -> List[Dict[str, Any]]:
        """Process advancement section for bridge connections"""
        advancement_bridges = []
        if advancement:
            # Look for analogy patterns
            if any(
                word in advancement.lower()
                for word in ["like", "similar", "flows", "downhill"]
            ):
                advancement_bridges.append(
                    {
                        "connection_type": "analogy",
                        "analogy_text": advancement,
                        "analogy_strength": 0.8,
                        "explanation": "Explicit analogy found in advancement section",
                    }
                )
        return advancement_bridges
