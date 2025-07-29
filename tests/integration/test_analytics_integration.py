"""
Integration tests for the analytics module with real data.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

from src.ai.analytics import NoteAnalytics


@pytest.mark.integration
class TestAnalyticsIntegration:
    """Integration tests for NoteAnalytics with realistic data."""
    
    def setup_method(self):
        """Set up test environment with realistic note structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.notes_dir = Path(self.temp_dir)
        
        # Create realistic directory structure
        (self.notes_dir / "Inbox").mkdir()
        (self.notes_dir / "Fleeting Notes").mkdir()
        (self.notes_dir / "Permanent Notes").mkdir()
        (self.notes_dir / "Literature Notes").mkdir()
        
        self.analytics = NoteAnalytics(str(self.notes_dir))
        
        # Create realistic test notes
        self._create_realistic_notes()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def _create_realistic_notes(self):
        """Create a realistic collection of notes for testing."""
        
        # High-quality permanent notes
        permanent_notes = [
            {
                "filename": "machine-learning-fundamentals.md",
                "content": """---
type: permanent
created: 2024-01-15 09:30
tags: ["machine-learning", "artificial-intelligence", "algorithms", "data-science"]
status: published
ai_summary: Comprehensive overview of machine learning fundamentals including supervised, unsupervised, and reinforcement learning approaches.
visibility: shared
---

# Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. This note covers the core concepts and methodologies.

## Types of Machine Learning

### Supervised Learning
Supervised learning uses labeled training data to learn a mapping function from input variables to output variables. Common algorithms include:
- Linear regression for continuous outcomes
- Logistic regression for binary classification
- Decision trees for both regression and classification
- Support vector machines for complex decision boundaries

### Unsupervised Learning
Unsupervised learning finds hidden patterns in data without labeled examples:
- Clustering algorithms like K-means and hierarchical clustering
- Dimensionality reduction techniques such as PCA and t-SNE
- Association rule learning for market basket analysis

### Reinforcement Learning
Reinforcement learning involves an agent learning to make decisions through trial and error:
- Q-learning for discrete action spaces
- Policy gradient methods for continuous control
- Actor-critic architectures combining value and policy methods

## Key Concepts

The success of machine learning depends on several critical factors:
- **Data Quality**: Clean, representative, and sufficient training data
- **Feature Engineering**: Selecting and transforming relevant input variables
- **Model Selection**: Choosing appropriate algorithms for the problem domain
- **Evaluation Metrics**: Using proper measures to assess model performance
- **Overfitting Prevention**: Techniques like cross-validation and regularization

## Applications

Machine learning has revolutionized numerous fields:
- Healthcare: Medical diagnosis and drug discovery
- Finance: Fraud detection and algorithmic trading
- Technology: Recommendation systems and natural language processing
- Transportation: Autonomous vehicles and route optimization

## Related Notes

This topic connects to several other areas in my knowledge base:
- [[deep-learning-architectures]] - Advanced neural network designs
- [[data-preprocessing-techniques]] - Preparing data for ML models
- [[model-evaluation-metrics]] - Assessing algorithm performance
- [[ethical-ai-considerations]] - Responsible AI development

## References

Key resources for deeper understanding:
- "Pattern Recognition and Machine Learning" by Christopher Bishop
- "The Elements of Statistical Learning" by Hastie, Tibshirani, and Friedman
- Online courses from Stanford CS229 and MIT 6.034
"""
            },
            {
                "filename": "quantum-computing-principles.md",
                "content": """---
type: permanent
created: 2024-02-03 14:20
tags: ["quantum-computing", "physics", "algorithms", "cryptography"]
status: published
ai_summary: Exploration of quantum computing principles, including qubits, superposition, entanglement, and quantum algorithms.
visibility: private
---

# Quantum Computing Principles

Quantum computing represents a paradigm shift from classical computation, leveraging quantum mechanical phenomena to process information in fundamentally new ways.

## Quantum Bits (Qubits)

Unlike classical bits that exist in definite states of 0 or 1, qubits can exist in superposition:
- Superposition allows qubits to be in multiple states simultaneously
- Measurement collapses the superposition to a definite state
- This enables exponential scaling of computational possibilities

## Quantum Phenomena

### Superposition
The ability of quantum systems to exist in multiple states simultaneously until measured.

### Entanglement
Quantum particles can be correlated in ways that classical physics cannot explain:
- Changes to one entangled particle instantly affect its partner
- Enables quantum teleportation and distributed quantum computing
- Critical for quantum error correction and communication protocols

### Interference
Quantum amplitudes can interfere constructively or destructively:
- Allows quantum algorithms to amplify correct answers
- Enables cancellation of incorrect computational paths
- Forms the basis of quantum speedup in many algorithms

## Quantum Algorithms

Several quantum algorithms demonstrate exponential speedup over classical approaches:

### Shor's Algorithm
- Efficiently factors large integers
- Threatens current RSA cryptographic systems
- Requires fault-tolerant quantum computers with thousands of qubits

### Grover's Algorithm
- Provides quadratic speedup for unstructured search
- Searches unsorted databases in O(√N) time
- Has applications in optimization and machine learning

### Quantum Simulation
- Simulates quantum systems that are intractable classically
- Applications in chemistry, materials science, and drug discovery
- May provide the first practical quantum advantage

## Current Challenges

Quantum computing faces significant technical hurdles:
- **Decoherence**: Quantum states are fragile and easily disrupted
- **Error Rates**: Current quantum gates have high error rates
- **Scalability**: Building systems with many high-quality qubits
- **Programming Models**: Developing intuitive quantum programming languages

## Applications and Impact

Potential applications span multiple domains:
- Cryptography: Breaking current encryption and enabling quantum-safe protocols
- Optimization: Solving complex scheduling and routing problems
- Machine Learning: Quantum neural networks and feature mapping
- Scientific Simulation: Modeling molecular and material properties

## Related Concepts

This field intersects with numerous other areas:
- [[cryptographic-protocols]] - Security implications of quantum computing
- [[linear-algebra-foundations]] - Mathematical basis of quantum mechanics
- [[complexity-theory]] - Computational complexity classes and quantum advantage
- [[quantum-error-correction]] - Protecting quantum information from noise
"""
            }
        ]
        
        # Medium-quality fleeting notes
        fleeting_notes = [
            {
                "filename": "idea-blockchain-voting.md",
                "content": """---
type: fleeting
created: 2024-02-10 16:45
tags: ["blockchain", "voting", "democracy"]
status: draft
---

# Blockchain-Based Voting System Idea

Had an interesting thought about using blockchain technology for secure, transparent voting systems.

## Key Benefits
- Immutable record of all votes
- Transparent verification process
- Reduced risk of tampering
- Potential for remote voting

## Challenges to Consider
- Voter privacy vs transparency
- Technical literacy requirements
- Infrastructure and accessibility
- Regulatory and legal frameworks

## Next Steps
- Research existing blockchain voting projects
- Analyze security vulnerabilities
- Consider user experience design
- Explore pilot program possibilities

This could connect to my notes on [[cryptographic-protocols]] and [[digital-identity-systems]].
"""
            },
            {
                "filename": "meeting-notes-ai-ethics.md",
                "content": """---
type: fleeting
created: 2024-02-08 10:15
tags: ["ai-ethics", "meeting-notes", "policy"]
status: inbox
---

# AI Ethics Discussion - Feb 8, 2024

Notes from team meeting on AI ethics guidelines.

## Key Points Discussed
- Bias in training data and algorithms
- Transparency and explainability requirements
- Privacy concerns with personal data
- Accountability for AI decisions

## Action Items
- [ ] Research existing AI ethics frameworks
- [ ] Draft initial guidelines for our projects
- [ ] Schedule follow-up meeting with legal team
- [ ] Review competitor approaches

## Resources Mentioned
- IEEE Standards for Ethical AI Design
- EU AI Act requirements
- Partnership on AI best practices

Need to develop this into a more comprehensive framework.
"""
            }
        ]
        
        # Literature notes
        literature_notes = [
            {
                "filename": "attention-is-all-you-need-paper.md",
                "content": """---
type: literature
created: 2024-01-28 11:00
tags: ["transformers", "attention-mechanism", "nlp", "deep-learning"]
status: published
source: "Vaswani et al., 2017"
ai_summary: Analysis of the seminal Transformer architecture paper that introduced self-attention mechanisms.
---

# "Attention Is All You Need" - Paper Analysis

**Authors**: Ashish Vaswani, Noam Shazeer, Niki Parmar, et al.
**Published**: NIPS 2017
**Citation Count**: 50,000+ (as of 2024)

## Abstract Summary

The paper introduces the Transformer architecture, a novel neural network design that relies entirely on attention mechanisms, dispensing with recurrence and convolutions entirely.

## Key Contributions

### Self-Attention Mechanism
- Allows each position to attend to all positions in the input sequence
- Enables parallel computation unlike RNNs
- Captures long-range dependencies more effectively

### Multi-Head Attention
- Uses multiple attention heads to capture different types of relationships
- Each head learns different aspects of the input representation
- Concatenated and projected to final dimension

### Positional Encoding
- Since there's no inherent sequence order, positional information is added
- Uses sinusoidal functions to encode position
- Allows model to understand sequence structure

## Architecture Details

The Transformer consists of:
- Encoder stack with 6 identical layers
- Decoder stack with 6 identical layers
- Each layer has multi-head attention and feed-forward networks
- Residual connections and layer normalization throughout

## Experimental Results

- Achieved state-of-the-art results on WMT translation tasks
- Significantly faster training than RNN-based models
- Better performance on long sequences
- More parallelizable architecture

## Impact and Significance

This paper fundamentally changed the field of NLP:
- Basis for BERT, GPT, and other large language models
- Enabled the current era of large-scale language models
- Influenced computer vision with Vision Transformers
- Sparked research into attention mechanisms across domains

## Personal Notes

The elegance of the attention mechanism is remarkable - it's conceptually simple yet incredibly powerful. The ability to attend to any part of the sequence directly addresses the limitations of RNNs with long sequences.

## Related Work

This connects to several other important papers:
- [[bert-paper-analysis]] - Bidirectional encoder representations
- [[gpt-architecture-evolution]] - Generative pre-training approach
- [[vision-transformer-paper]] - Applying transformers to images
"""
            }
        ]
        
        # Low-quality inbox notes
        inbox_notes = [
            {
                "filename": "random-thought.md",
                "content": """---
type: unknown
created: 2024-02-12 22:30
status: inbox
---

Quick thought about something I read today. Need to develop this more.
"""
            },
            {
                "filename": "todo-research.md",
                "content": """---
status: inbox
---

Research topics:
- Neural networks
- Quantum stuff
- Blockchain maybe?

Need to organize this better.
"""
            }
        ]
        
        # Create all notes
        all_notes = [
            ("Permanent Notes", permanent_notes),
            ("Fleeting Notes", fleeting_notes),
            ("Literature Notes", literature_notes),
            ("Inbox", inbox_notes)
        ]
        
        for directory, notes in all_notes:
            for note_data in notes:
                note_path = self.notes_dir / directory / note_data["filename"]
                note_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(note_data["content"])
    
    def test_comprehensive_note_scanning(self):
        """Test scanning of realistic note collection."""
        notes = self.analytics.scan_notes()
        
        # Should find all created notes
        assert len(notes) == 7  # 2 permanent + 2 fleeting + 1 literature + 2 inbox
        
        # Check variety of note types
        note_types = [note.note_type for note in notes]
        assert "permanent" in note_types
        assert "fleeting" in note_types
        assert "literature" in note_types
        assert "unknown" in note_types
        
        # Check quality distribution
        quality_scores = [note.quality_score for note in notes]
        assert max(quality_scores) > 0.8  # High-quality notes exist
        assert min(quality_scores) < 0.3  # Low-quality notes exist
        
        # Check AI feature detection
        notes_with_summaries = [note for note in notes if note.has_summary]
        assert len(notes_with_summaries) >= 2  # Permanent and literature notes have summaries
    
    def test_realistic_report_generation(self):
        """Test comprehensive report generation with realistic data."""
        report = self.analytics.generate_report()
        
        assert "error" not in report
        
        # Check overview metrics
        overview = report["overview"]
        assert overview["total_notes"] == 7
        assert overview["total_words"] > 1000  # Substantial content
        assert overview["average_words_per_note"] > 100
        assert 0.3 < overview["average_quality_score"] < 0.8  # Mixed quality
        assert overview["notes_with_ai_summaries"] >= 2
        assert overview["total_internal_links"] > 0
        
        # Check distributions
        distributions = report["distributions"]
        note_types = distributions["note_types"]
        assert note_types["permanent"] == 2
        assert note_types["fleeting"] == 2
        assert note_types["literature"] == 1
        assert note_types["unknown"] == 2
        
        # Check quality metrics
        quality = report["quality_metrics"]
        assert quality["high_quality_notes"] >= 1
        assert quality["low_quality_notes"] >= 1
        assert quality["quality_distribution"]["min"] < quality["quality_distribution"]["max"]
        
        # Check temporal analysis
        temporal = report["temporal_analysis"]
        assert temporal["notes_with_dates"] >= 5  # Most notes have creation dates
        assert temporal["date_range"]["earliest"] is not None
        assert temporal["date_range"]["latest"] is not None
        
        # Check recommendations
        recommendations = report["recommendations"]
        assert len(recommendations) > 0
        
        # Should recommend improvements for low-quality notes
        improvement_rec = any("low-quality" in rec for rec in recommendations)
        assert improvement_rec
        
        # Should recommend processing inbox notes
        inbox_rec = any("inbox" in rec for rec in recommendations)
        assert inbox_rec
    
    def test_export_and_import_report(self):
        """Test report export and JSON integrity."""
        output_file = self.notes_dir / "analytics_report.json"
        
        # Export report
        result = self.analytics.export_report(str(output_file))
        assert "Report exported" in result
        assert output_file.exists()
        
        # Verify JSON structure
        with open(output_file, 'r') as f:
            exported_data = json.load(f)
        
        # Check all expected sections
        expected_sections = ["overview", "distributions", "quality_metrics", 
                           "temporal_analysis", "recommendations"]
        for section in expected_sections:
            assert section in exported_data
        
        # Verify data integrity
        assert exported_data["overview"]["total_notes"] == 7
        assert len(exported_data["recommendations"]) > 0
        
        # Check that dates are properly serialized
        temporal = exported_data["temporal_analysis"]
        if temporal["date_range"]["earliest"]:
            # Should be valid ISO format
            datetime.fromisoformat(temporal["date_range"]["earliest"])
    
    def test_quality_score_accuracy(self):
        """Test that quality scores accurately reflect note characteristics."""
        notes = self.analytics.scan_notes()
        
        # Find specific notes by filename
        ml_note = next((n for n in notes if "machine-learning" in n.filename), None)
        random_note = next((n for n in notes if "random-thought" in n.filename), None)
        literature_note = next((n for n in notes if "attention-is-all" in n.filename), None)
        
        assert ml_note is not None
        assert random_note is not None
        assert literature_note is not None
        
        # Machine learning note should have high quality
        assert ml_note.quality_score > 0.8
        assert ml_note.word_count > 500
        assert ml_note.tag_count >= 4
        assert ml_note.link_count > 0
        
        # Random thought should have low quality
        assert random_note.quality_score < 0.3
        assert random_note.word_count < 50
        assert random_note.tag_count == 0
        
        # Literature note should have high quality
        assert literature_note.quality_score > 0.7
        assert literature_note.has_summary is True
        assert literature_note.tag_count >= 3
    
    def test_tag_analysis_accuracy(self):
        """Test accuracy of tag-related analytics."""
        notes = self.analytics.scan_notes()
        
        # Count total tags across all notes
        total_tags = sum(note.tag_count for note in notes)
        assert total_tags > 10  # Should have substantial tagging
        
        # Check tag distribution
        tagged_notes = [note for note in notes if note.tag_count > 0]
        untagged_notes = [note for note in notes if note.tag_count == 0]
        
        assert len(tagged_notes) >= 5  # Most notes should be tagged
        assert len(untagged_notes) >= 1  # Some inbox notes untagged
        
        # High-quality notes should generally be well-tagged
        high_quality_notes = [note for note in notes if note.quality_score > 0.7]
        for note in high_quality_notes:
            assert note.tag_count >= 3  # High-quality notes should have multiple tags
    
    def test_link_analysis_accuracy(self):
        """Test accuracy of internal link analysis."""
        notes = self.analytics.scan_notes()
        
        # Count total internal links
        total_links = sum(note.link_count for note in notes)
        assert total_links > 5  # Should have several internal links
        
        # Permanent notes should generally have more links
        permanent_notes = [note for note in notes if note.note_type == "permanent"]
        for note in permanent_notes:
            assert note.link_count > 0  # Permanent notes should be well-connected
    
    def test_temporal_analysis_accuracy(self):
        """Test accuracy of temporal analysis."""
        notes = self.analytics.scan_notes()
        
        # Most notes should have creation dates
        notes_with_dates = [note for note in notes if note.creation_date is not None]
        assert len(notes_with_dates) >= 5
        
        # Check date parsing accuracy
        for note in notes_with_dates:
            assert isinstance(note.creation_date, datetime)
            # Dates should be reasonable (not in future, not too old)
            assert note.creation_date.year >= 2020
            assert note.creation_date <= datetime.now()
    
    def test_recommendation_relevance(self):
        """Test that recommendations are relevant to the note collection."""
        report = self.analytics.generate_report()
        recommendations = report["recommendations"]
        
        # Should have multiple relevant recommendations
        assert len(recommendations) >= 3
        
        # Check for expected recommendation types
        rec_text = " ".join(recommendations).lower()
        
        # Should recommend processing inbox (we have 2 inbox notes)
        assert "inbox" in rec_text
        
        # Should recommend improvements (we have low-quality notes)
        assert any(word in rec_text for word in ["improve", "quality", "low-quality"])
        
        # Should recommend tagging (we have untagged notes)
        assert "tag" in rec_text
    
    def test_performance_with_realistic_data(self):
        """Test performance with realistic data volumes."""
        import time
        
        # Measure scanning performance
        start_time = time.time()
        notes = self.analytics.scan_notes()
        scan_time = time.time() - start_time
        
        # Should complete scanning quickly
        assert scan_time < 2.0  # Less than 2 seconds for 7 notes
        assert len(notes) == 7
        
        # Measure report generation performance
        start_time = time.time()
        report = self.analytics.generate_report()
        report_time = time.time() - start_time
        
        # Should generate report quickly
        assert report_time < 3.0  # Less than 3 seconds
        assert "error" not in report
