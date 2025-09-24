"""
Advanced Tag Enhancement Utilities (TDD Iteration 3 REFACTOR Phase)

Extracted utility classes for modular architecture following TDD Iteration 1&2 success patterns.
Building on proven TagQualityScorer foundation with enhanced intelligent suggestion capabilities.
"""
import re
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
from .ai_tagging_prevention_utils import TagQualityScorer


@dataclass
class EnhancementRecommendation:
    """Structured recommendation for tag enhancement"""
    original_tag: str
    suggested_tag: str
    reason: str
    confidence: float
    enhancement_type: str
    
    
@dataclass 
class SuggestionContext:
    """Contextual information for generating better suggestions"""
    note_content: str
    existing_tags: List[str] 
    domain_hints: List[str]
    user_preferences: Dict[str, Any]


class SemanticDomainMapper:
    """Advanced semantic domain mapping for contextual suggestions"""
    
    def __init__(self):
        self.domain_hierarchies = {
            'artificial-intelligence': {
                'parent': None,
                'children': ['machine-learning', 'deep-learning', 'natural-language-processing', 'computer-vision'],
                'related': ['cognitive-science', 'robotics', 'automation']
            },
            'quantum-computing': {
                'parent': 'physics',
                'children': ['quantum-entanglement', 'superconducting-qubits', 'quantum-algorithms'],
                'related': ['cryptography', 'high-performance-computing']
            },
            'blockchain': {
                'parent': 'distributed-systems',
                'children': ['cryptocurrency', 'smart-contracts', 'consensus-algorithms'],
                'related': ['cryptography', 'fintech', 'web3']
            }
        }
        
        self.compound_concept_patterns = [
            (r'machine\s+learning', 'machine-learning'),
            (r'artificial\s+intelligence', 'artificial-intelligence'),
            (r'natural\s+language\s+processing', 'natural-language-processing'),
            (r'computer\s+vision', 'computer-vision'),
            (r'quantum\s+computing', 'quantum-computing'),
            (r'deep\s+learning', 'deep-learning'),
            (r'neural\s+networks?', 'neural-networks'),
        ]
        
    def map_to_semantic_domain(self, concept: str) -> List[str]:
        """Map concept to semantic domain with hierarchical suggestions"""
        suggestions = []
        concept_lower = concept.lower()
        
        # Check compound concept patterns first
        for pattern, replacement in self.compound_concept_patterns:
            if re.search(pattern, concept_lower):
                suggestions.append(replacement)
                
        # Check domain hierarchies
        for domain, hierarchy in self.domain_hierarchies.items():
            if any(child in concept_lower for child in hierarchy['children']):
                suggestions.append(domain)  # Suggest parent domain
            elif domain in concept_lower:
                suggestions.extend(hierarchy['children'])  # Suggest child concepts
                
        return list(set(suggestions))
        
    def get_contextual_alternatives(self, tag: str, context: str) -> List[str]:
        """Get contextually relevant alternatives based on content"""
        alternatives = []
        context_lower = context.lower()
        
        # Context-driven mapping
        if 'research' in context_lower and tag == 'ai':
            alternatives.extend(['artificial-intelligence', 'machine-learning-research'])
        elif 'application' in context_lower and 'quantum' in tag:
            alternatives.extend(['quantum-computing', 'quantum-applications'])
        elif 'business' in context_lower and 'blockchain' in tag:
            alternatives.extend(['cryptocurrency', 'fintech', 'blockchain-business'])
            
        return alternatives


class IntelligentTagFormatter:
    """Intelligent tag formatting with context awareness"""
    
    def __init__(self):
        self.format_rules = {
            'underscore_to_hyphen': (r'_', '-'),
            'space_to_hyphen': (r'\s+', '-'),
            'camelcase_to_kebab': (r'([a-z])([A-Z])', r'\1-\2'),
            'remove_special_chars': (r'[^\w\s-]', ''),
            'lowercase': ('UPPER', 'lower')
        }
        
        self.semantic_corrections = {
            'ai': 'artificial-intelligence',
            'ml': 'machine-learning', 
            'dl': 'deep-learning',
            'nlp': 'natural-language-processing',
            'cv': 'computer-vision',
            'nn': 'neural-networks'
        }
        
    def apply_intelligent_formatting(self, tag: str) -> List[EnhancementRecommendation]:
        """Apply intelligent formatting with explanations"""
        recommendations = []
        original_tag = tag
        
        # Apply format corrections
        formatted_tag = self._apply_format_rules(tag)
        
        if formatted_tag != original_tag:
            recommendations.append(EnhancementRecommendation(
                original_tag=original_tag,
                suggested_tag=formatted_tag,
                reason='Applied standard kebab-case formatting',
                confidence=0.9,
                enhancement_type='format_correction'
            ))
            
        # Apply semantic corrections
        if formatted_tag.lower() in self.semantic_corrections:
            semantic_tag = self.semantic_corrections[formatted_tag.lower()]
            recommendations.append(EnhancementRecommendation(
                original_tag=original_tag,
                suggested_tag=semantic_tag,
                reason='Expanded abbreviation for semantic clarity',
                confidence=0.95,
                enhancement_type='semantic_expansion'
            ))
            
        return recommendations
        
    def _apply_format_rules(self, tag: str) -> str:
        """Apply format rules in sequence"""
        result = tag
        
        # Remove special characters first
        result = re.sub(r'[^\w\s-]', '', result)
        
        # Handle camelCase
        result = re.sub(r'([a-z])([A-Z])', r'\1-\2', result)
        
        # Replace spaces and underscores with hyphens
        result = re.sub(r'[\s_]+', '-', result)
        
        # Convert to lowercase
        result = result.lower()
        
        # Clean up multiple hyphens
        result = re.sub(r'-+', '-', result)
        
        # Remove leading/trailing hyphens
        result = result.strip('-')
        
        return result


class ContextualSuggestionEngine:
    """Generate contextually relevant tag suggestions"""
    
    def __init__(self):
        self.domain_mapper = SemanticDomainMapper()
        self.content_analyzers = {
            'technical_terms': self._extract_technical_terms,
            'domain_concepts': self._extract_domain_concepts,
            'compound_phrases': self._extract_compound_phrases
        }
        
    def generate_contextual_suggestions(self, note_content: str, existing_tags: List[str]) -> List[EnhancementRecommendation]:
        """Generate suggestions based on note content and existing tags"""
        suggestions = []
        
        # Analyze content for missing concepts
        content_concepts = self._analyze_content_concepts(note_content)
        
        # Find gaps between content and existing tags
        missing_concepts = set(content_concepts) - set(existing_tags)
        
        for concept in missing_concepts:
            if self._is_high_quality_concept(concept):
                suggestions.append(EnhancementRecommendation(
                    original_tag='',  # New suggestion
                    suggested_tag=concept,
                    reason=f'Content analysis suggests missing concept: {concept}',
                    confidence=0.8,
                    enhancement_type='contextual_addition'
                ))
                
        # Suggest improvements for existing tags
        for tag in existing_tags:
            improvements = self.domain_mapper.map_to_semantic_domain(tag)
            for improvement in improvements:
                if improvement != tag and improvement not in existing_tags:
                    suggestions.append(EnhancementRecommendation(
                        original_tag=tag,
                        suggested_tag=improvement,
                        reason=f'Semantic enhancement based on domain mapping',
                        confidence=0.7,
                        enhancement_type='semantic_enhancement'
                    ))
                    
        return suggestions
        
    def _analyze_content_concepts(self, content: str) -> List[str]:
        """Analyze content to extract key concepts"""
        concepts = []
        
        for analyzer_name, analyzer_func in self.content_analyzers.items():
            extracted = analyzer_func(content)
            concepts.extend(extracted)
            
        return list(set(concepts))
        
    def _extract_technical_terms(self, content: str) -> List[str]:
        """Extract technical terms from content"""
        # Use domain mapper's compound patterns
        terms = []
        for pattern, replacement in self.domain_mapper.compound_concept_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                terms.append(replacement)
        return terms
        
    def _extract_domain_concepts(self, content: str) -> List[str]:
        """Extract domain-specific concepts"""
        concepts = []
        content_lower = content.lower()
        
        # Check for domain indicators
        for domain in self.domain_mapper.domain_hierarchies.keys():
            if domain.replace('-', ' ') in content_lower:
                concepts.append(domain)
                
        return concepts
        
    def _extract_compound_phrases(self, content: str) -> List[str]:
        """Extract compound technical phrases"""
        phrases = []
        
        # Look for multi-word technical terms
        compound_patterns = [
            r'(\w+\s+(?:learning|computing|processing|intelligence|networks?))',
            r'((?:quantum|machine|deep|artificial)\s+\w+)',
            r'(\w+\s+(?:algorithm|model|system|framework)s?)'
        ]
        
        for pattern in compound_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                formatted = match.lower().replace(' ', '-')
                phrases.append(formatted)
                
        return phrases
        
    def _is_high_quality_concept(self, concept: str) -> bool:
        """Validate concept quality for suggestions"""
        if len(concept) < 3 or len(concept) > 50:
            return False
        if not re.match(r'^[a-z]+(?:-[a-z]+)*$', concept):
            return False
        return True


class AdaptiveLearningEngine:
    """Machine learning from user feedback for continuous improvement"""
    
    def __init__(self):
        self.learning_patterns = {
            'user_preferences': {},
            'rejection_patterns': {},
            'success_patterns': {},
            'domain_preferences': {}
        }
        self.confidence_adjustments = {}
        
    def learn_from_feedback_session(self, feedback_data: Dict[str, Any]) -> None:
        """Learn from comprehensive user feedback session"""
        # Learn user preferences
        for original, preferred in feedback_data.get('accepted_suggestions', []):
            self.learning_patterns['user_preferences'][original] = preferred
            self._update_success_patterns(original, preferred)
            
        # Learn rejection patterns
        for original, rejected in feedback_data.get('rejected_suggestions', []):
            self.learning_patterns['rejection_patterns'][original] = rejected
            self._adjust_confidence_down(original, rejected)
            
        # Learn from user corrections
        for original, corrected in feedback_data.get('user_corrections', []):
            self.learning_patterns['user_preferences'][original] = corrected
            self._identify_correction_patterns(original, corrected)
            
    def apply_learned_intelligence(self, suggestions: List[EnhancementRecommendation]) -> List[EnhancementRecommendation]:
        """Apply learned intelligence to enhance suggestion quality"""
        enhanced_suggestions = []
        
        for suggestion in suggestions:
            # Apply confidence adjustments based on learning
            adjusted_confidence = self._calculate_adjusted_confidence(suggestion)
            
            # Check against rejection patterns
            if not self._matches_rejection_pattern(suggestion):
                enhanced_suggestion = EnhancementRecommendation(
                    original_tag=suggestion.original_tag,
                    suggested_tag=suggestion.suggested_tag,
                    reason=suggestion.reason + self._add_learning_context(suggestion),
                    confidence=adjusted_confidence,
                    enhancement_type=suggestion.enhancement_type
                )
                enhanced_suggestions.append(enhanced_suggestion)
                
        return enhanced_suggestions
        
    def _update_success_patterns(self, original: str, preferred: str) -> None:
        """Update success patterns from user acceptance"""
        pattern_key = f"{original}→{preferred}"
        if pattern_key not in self.learning_patterns['success_patterns']:
            self.learning_patterns['success_patterns'][pattern_key] = 0
        self.learning_patterns['success_patterns'][pattern_key] += 1
        
    def _adjust_confidence_down(self, original: str, rejected: str) -> None:
        """Adjust confidence down for rejected patterns"""
        rejection_key = f"{original}→{rejected}"
        self.confidence_adjustments[rejection_key] = -0.2
        
    def _identify_correction_patterns(self, original: str, corrected: str) -> None:
        """Identify patterns in user corrections"""
        # Analyze correction patterns for future learning
        if len(corrected) > len(original):
            self.learning_patterns['domain_preferences']['expansion'] = True
        elif '-' in corrected and '-' not in original:
            self.learning_patterns['domain_preferences']['hyphenation'] = True
            
    def _calculate_adjusted_confidence(self, suggestion: EnhancementRecommendation) -> float:
        """Calculate confidence adjusted by learning"""
        base_confidence = suggestion.confidence
        
        # Check for specific adjustment patterns
        adjustment_key = f"{suggestion.original_tag}→{suggestion.suggested_tag}"
        if adjustment_key in self.confidence_adjustments:
            base_confidence += self.confidence_adjustments[adjustment_key]
            
        # Apply domain preferences
        if self.learning_patterns['domain_preferences'].get('hyphenation') and '-' in suggestion.suggested_tag:
            base_confidence += 0.1
            
        return max(0.0, min(1.0, base_confidence))
        
    def _matches_rejection_pattern(self, suggestion: EnhancementRecommendation) -> bool:
        """Check if suggestion matches known rejection patterns"""
        return suggestion.suggested_tag in self.learning_patterns['rejection_patterns'].values()
        
    def _add_learning_context(self, suggestion: EnhancementRecommendation) -> str:
        """Add learning context to suggestion reasons"""
        success_count = sum(1 for pattern in self.learning_patterns['success_patterns'] 
                          if suggestion.suggested_tag in pattern)
        if success_count > 0:
            return f" (Previously accepted {success_count} times)"
        return ""


class PerformanceOptimizedProcessor:
    """Optimized batch processing for large tag collections"""
    
    def __init__(self):
        self.batch_size = 100
        self.quality_scorer = TagQualityScorer()
        self.processing_stats = {
            'total_processed': 0,
            'processing_times': [],
            'quality_improvements': []
        }
        
    def process_tag_batch(self, tags: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process tags in optimized batches"""
        import time
        start_time = time.time()
        
        results = {
            'processed_tags': [],
            'enhancement_candidates': [],
            'high_quality_tags': [],
            'batch_statistics': {}
        }
        
        # Process in batches to maintain performance
        for i in range(0, len(tags), self.batch_size):
            batch = tags[i:i + self.batch_size]
            batch_result = self._process_single_batch(batch, context)
            
            # Merge results
            results['processed_tags'].extend(batch_result['processed'])
            results['enhancement_candidates'].extend(batch_result['candidates'])
            results['high_quality_tags'].extend(batch_result['high_quality'])
            
        processing_time = time.time() - start_time
        
        # Update statistics
        self.processing_stats['total_processed'] += len(tags)
        self.processing_stats['processing_times'].append(processing_time)
        
        results['batch_statistics'] = {
            'processing_time': processing_time,
            'tags_per_second': len(tags) / processing_time if processing_time > 0 else 0,
            'total_tags': len(tags),
            'enhancement_rate': len(results['enhancement_candidates']) / len(tags) if tags else 0
        }
        
        return results
        
    def _process_single_batch(self, batch: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a single batch of tags efficiently"""
        processed = []
        candidates = []
        high_quality = []
        
        for tag in batch:
            if not tag or not tag.strip():
                continue
                
            # Quick quality assessment
            quality_result = self.quality_scorer.score_tag_quality(tag)
            
            processed.append({
                'tag': tag,
                'quality_score': quality_result['total_score'],
                'quality_level': quality_result['quality_level']
            })
            
            if quality_result['total_score'] < 0.7:
                candidates.append(tag)
            else:
                high_quality.append(tag)
                
        return {
            'processed': processed,
            'candidates': candidates,
            'high_quality': high_quality
        }
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        if not self.processing_stats['processing_times']:
            return {'no_data': True}
            
        avg_time = sum(self.processing_stats['processing_times']) / len(self.processing_stats['processing_times'])
        
        return {
            'total_processed': self.processing_stats['total_processed'],
            'average_processing_time': avg_time,
            'peak_performance': max(len(self.processing_stats['processing_times'])) if self.processing_stats['processing_times'] else 0,
            'performance_target_met': avg_time < 10.0,  # <10s target
            'processing_efficiency': 'excellent' if avg_time < 5.0 else 'good' if avg_time < 10.0 else 'needs_improvement'
        }
