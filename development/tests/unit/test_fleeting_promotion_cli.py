"""
Test suite for --promote-note CLI command (Phase 3: Simple Promotion Workflow)

TDD RED Phase: All tests designed to fail until --promote-note is implemented.
Following the successful Phase 2 testing methodology.
"""

import tempfile
import shutil
import subprocess
import sys
import json
from pathlib import Path

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestFleetingPromotionCLI:
    """Test cases for --promote-note CLI command (US-3)."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        self.cli_script = Path(__file__).parent.parent.parent / "src" / "cli" / "workflow_demo.py"

        # Create vault structure
        (self.vault_path / "knowledge" / "Fleeting Notes").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Permanent Notes").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Literature Notes").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Inbox").mkdir(parents=True)

        # Create sample fleeting notes for testing
        self._create_sample_fleeting_notes()

    def _create_sample_fleeting_notes(self):
        """Create sample fleeting notes for promotion testing."""
        fleeting_dir = self.vault_path / "knowledge" / "Fleeting Notes"

        # High-quality note ready for promotion
        high_quality_note = fleeting_dir / "high-quality-fleeting-note.md"
        high_quality_note.write_text("""---
type: fleeting
created: 2025-09-10 14:30
status: inbox
tags: [productivity, ai, workflow, systems]
---

# Comprehensive Guide to AI-Enhanced Productivity Workflows

This is an exceptionally well-structured note that demonstrates high-quality content with clear insights, comprehensive coverage, and actionable recommendations. It should definitely be promoted to permanent status given its depth and value.

## Executive Summary
This note provides a comprehensive framework for implementing AI-enhanced productivity workflows in modern knowledge work environments. The systematic approach outlined here has been validated across multiple organizations and demonstrates significant improvements in efficiency and output quality.

## Key Insights and Principles

### 1. Foundation of AI-Enhanced Workflows
- **Automation First**: Identify repetitive cognitive tasks that can be automated
- **Human-AI Collaboration**: Design workflows that leverage both human creativity and AI processing power
- **Continuous Optimization**: Implement feedback loops for continuous improvement

### 2. Implementation Strategy
- **Phase 1**: Assessment of current workflows and identification of AI enhancement opportunities
- **Phase 2**: Pilot implementation with key stakeholders and metrics collection
- **Phase 3**: Full rollout with comprehensive training and support systems

### 3. Measurable Outcomes
- 40-60% reduction in routine cognitive tasks
- 25-35% improvement in decision-making speed
- 15-25% increase in creative output quality

## Practical Applications

### Content Creation Workflows
The integration of AI tools in content creation has shown remarkable results when properly structured:
- Research acceleration through intelligent information synthesis
- Draft generation with human oversight and refinement
- Quality assurance through automated checking systems

### Data Analysis Enhancement
AI-enhanced data analysis workflows provide:
- Pattern recognition in complex datasets
- Automated report generation with human interpretation
- Predictive modeling for strategic planning

## Technical Implementation Details

### Tool Stack Requirements
- **Core AI Platform**: GPT-4 or equivalent for text processing
- **Automation Layer**: Zapier/Make for workflow orchestration
- **Data Integration**: APIs for seamless information flow
- **Quality Monitoring**: Metrics dashboard for performance tracking

### Best Practices
1. **Start Small**: Begin with single workflow optimization
2. **Measure Everything**: Implement comprehensive analytics
3. **User Training**: Provide extensive training and support
4. **Iterative Improvement**: Regular optimization cycles

## Strategic Considerations

### Organizational Change Management
Successful AI workflow implementation requires:
- Executive sponsorship and clear vision communication
- Change management strategy addressing user concerns
- Training programs that build confidence and competency
- Success metrics that demonstrate clear ROI

### Risk Management
Key risks and mitigation strategies:
- **Data Security**: Implement robust encryption and access controls
- **Quality Control**: Human oversight for critical decisions
- **Dependency Risk**: Maintain fallback procedures for system failures
- **Skills Gap**: Comprehensive training and upskilling programs

## Future Evolution and Trends

### Emerging Technologies
The workflow landscape continues to evolve with:
- Multimodal AI capabilities for richer interaction
- Edge computing for faster processing and privacy
- Federated learning for improved personalization
- Quantum computing potential for complex optimization

### Scaling Considerations
As organizations mature in AI adoption:
- Workflow standardization across teams and departments
- Integration with enterprise systems and databases
- Cross-functional collaboration enhancement
- Advanced analytics for strategic insights

## Conclusion and Next Steps

The implementation of AI-enhanced productivity workflows represents a fundamental shift in how knowledge work is performed. Success requires thoughtful planning, systematic implementation, and continuous optimization. Organizations that embrace this transformation will gain significant competitive advantages in efficiency, quality, and innovation capacity.

### Immediate Action Items
1. Conduct workflow audit and AI enhancement assessment
2. Develop pilot program with clear success metrics
3. Create training and support infrastructure
4. Establish governance framework for AI tool usage
5. Plan phased rollout with feedback collection mechanisms

## Related Concepts and Connections
This framework connects to multiple important concepts:
- [[knowledge-management-systems]] - For information organization and retrieval
- [[digital-transformation-strategies]] - For broader organizational change
- [[ai-ethics-frameworks]] - For responsible AI implementation
- [[productivity-measurement-methods]] - For tracking and optimization
- [[change-management-best-practices]] - For successful organizational adoption

The comprehensive nature of this analysis, combined with practical implementation guidance and strategic considerations, makes this note an excellent candidate for promotion to permanent status in the knowledge management system.
""")

        # Medium-quality note needing work
        medium_quality_note = fleeting_dir / "medium-quality-fleeting-note.md"
        medium_quality_note.write_text("""---
type: fleeting
created: 2025-09-15 10:20
status: inbox
tags: [notes]
---

# Medium Quality Note

Some thoughts here but needs more development.
""")

        # Literature note for different promotion path
        literature_note = fleeting_dir / "literature-fleeting-note.md"
        literature_note.write_text("""---
type: fleeting
created: 2025-09-16 16:45
status: inbox
tags: [research, literature]
source: https://example.com/article
---

# Literature-Based Fleeting Note

Key insights from research article:
- Important finding 1
- Critical observation 2

This should be promoted to literature notes.
""")

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_promote_note_argument_parsing(self):
        """Test that --promote-note argument is recognized and parsed correctly."""
        # RED PHASE: This test will fail until --promote-note is implemented
        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--help"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "--promote-note" in result.stdout
        assert "Promote fleeting note" in result.stdout or "promote note" in result.stdout

    def test_promote_note_single_note_basic(self):
        """Test basic single note promotion functionality."""
        # RED PHASE: This test will fail until single note promotion is implemented
        note_path = "knowledge/Fleeting Notes/high-quality-fleeting-note.md"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "promotion" in result.stdout.lower()
        assert "success" in result.stdout.lower() or "promoted" in result.stdout.lower()

    def test_promote_note_with_target_directory(self):
        """Test promotion with specific target directory."""
        # RED PHASE: This test will fail until target directory selection is implemented
        note_path = "knowledge/Fleeting Notes/literature-fleeting-note.md"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path, "--to", "literature"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "literature" in result.stdout.lower()

    def test_promote_note_batch_processing(self):
        """Test batch promotion with quality threshold."""
        # RED PHASE: This test will fail until batch promotion is implemented
        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", "--batch", "--min-quality", "0.7"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "batch" in result.stdout.lower()
        assert "quality" in result.stdout.lower()

    def test_promote_note_json_format(self):
        """Test JSON output format for automation."""
        # RED PHASE: This test will fail until JSON format is implemented
        note_path = "knowledge/Fleeting Notes/high-quality-fleeting-note.md"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path, "--format", "json"
        ], capture_output=True, text=True)

        assert result.returncode == 0

        # Validate JSON structure
        output_data = json.loads(result.stdout)
        assert "promoted_notes" in output_data
        assert "target_directory" in output_data
        assert "promotion_time" in output_data

    def test_promote_note_preview_mode(self):
        """Test preview/dry-run mode before actual promotion."""
        # RED PHASE: This test will fail until preview mode is implemented
        note_path = "knowledge/Fleeting Notes/high-quality-fleeting-note.md"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path, "--preview"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "preview" in result.stdout.lower() or "would" in result.stdout.lower()
        assert "promote" in result.stdout.lower()

        # Verify no actual file move occurred
        original_path = self.vault_path / "knowledge" / "Fleeting Notes" / "high-quality-fleeting-note.md"
        assert original_path.exists()

    def test_promote_note_error_handling(self):
        """Test error handling for invalid inputs."""
        # RED PHASE: This test will fail until error handling is implemented

        # Test with non-existent note
        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", "non-existent-note.md"
        ], capture_output=True, text=True)

        assert result.returncode != 0
        error_output = (result.stderr + result.stdout).lower()
        assert "not found" in error_output or "does not exist" in error_output

        # Test with non-fleeting note (invalid type)
        non_fleeting = self.vault_path / "knowledge" / "Fleeting Notes" / "permanent-note.md"
        non_fleeting.write_text("""---
type: permanent
created: 2025-09-17 20:00
---

# Already Permanent Note
""")

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", "knowledge/Fleeting Notes/permanent-note.md"
        ], capture_output=True, text=True)

        assert result.returncode != 0 or "already" in result.stdout.lower()

    def test_promote_note_file_operations_safety(self):
        """Test that file operations are safe and preserve content."""
        # RED PHASE: This test will fail until safe file operations are implemented
        note_path = "knowledge/Fleeting Notes/high-quality-fleeting-note.md"
        original_content = (self.vault_path / note_path).read_text()

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path
        ], capture_output=True, text=True)

        assert result.returncode == 0

        # Verify content preservation (note may have moved)
        permanent_dir = self.vault_path / "knowledge" / "Permanent Notes"
        promoted_files = list(permanent_dir.glob("*.md"))
        assert len(promoted_files) >= 1

        # Find the promoted file and verify content preservation
        promoted_content = promoted_files[0].read_text()
        assert "Comprehensive Guide to AI-Enhanced Productivity Workflows" in promoted_content
        assert "Executive Summary" in promoted_content

    def test_promote_note_metadata_updates(self):
        """Test that promotion updates metadata correctly."""
        # RED PHASE: This test will fail until metadata updating is implemented
        note_path = "knowledge/Fleeting Notes/high-quality-fleeting-note.md"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path
        ], capture_output=True, text=True)

        assert result.returncode == 0

        # Find promoted note and check metadata
        permanent_dir = self.vault_path / "knowledge" / "Permanent Notes"
        promoted_files = list(permanent_dir.glob("*.md"))
        assert len(promoted_files) >= 1

        promoted_content = promoted_files[0].read_text()
        assert "type: permanent" in promoted_content
        assert "promoted_at:" in promoted_content or "promotion_date:" in promoted_content

    def test_promote_note_integration_with_triage(self):
        """Test integration with Phase 2 triage system."""
        # RED PHASE: This test will fail until triage integration is implemented

        # First run triage to identify high-quality notes
        triage_result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-triage", "--format", "json"
        ], capture_output=True, text=True)

        assert triage_result.returncode == 0
        triage_data = json.loads(triage_result.stdout)

        # Find a high-quality note from triage
        high_quality_notes = [note for note in triage_data["recommendations"]
                            if note["action"] == "Promote to Permanent"]
        assert len(high_quality_notes) > 0

        # Promote the first high-quality note
        note_to_promote = high_quality_notes[0]["note_path"]

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_to_promote
        ], capture_output=True, text=True)

        assert result.returncode == 0


class TestFleetingPromotionIntegration:
    """Integration tests for promotion workflow with existing systems."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        self.cli_script = Path(__file__).parent.parent.parent / "src" / "cli" / "workflow_demo.py"

        # Create basic vault structure
        (self.vault_path / "knowledge" / "Fleeting Notes").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Permanent Notes").mkdir(parents=True)

        # Create sample note
        self._create_test_note()

    def _create_test_note(self):
        """Create a test note for promotion."""
        fleeting_dir = self.vault_path / "knowledge" / "Fleeting Notes"
        test_note = fleeting_dir / "integration-test-note.md"
        test_note.write_text("""---
type: fleeting
created: 2025-09-17 20:00
status: inbox
tags: [test, integration]
---

# Integration Test Note

This note tests the integration between promotion and existing systems.
""")

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_promotion_does_not_break_existing_commands(self):
        """Test that adding --promote-note doesn't break existing CLI commands."""
        # RED PHASE: This test ensures we don't break existing functionality

        # Test that --fleeting-triage still works
        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-triage"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "TRIAGE REPORT" in result.stdout

    def test_promotion_follows_cli_output_formatting_patterns(self):
        """Test that promotion output follows established formatting patterns."""
        # RED PHASE: This test will fail until formatting is implemented
        note_path = "knowledge/Fleeting Notes/integration-test-note.md"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = result.stdout

        # Check for emoji usage (following Phase 2 patterns)
        assert any(emoji in output for emoji in ["✅", "📄", "🚀", "🔄"])

        # Check for section headers (following Phase 2 patterns)
        assert any(header in output for header in ["PROMOTION", "RESULTS", "SUCCESS"])

    def test_promotion_performance_target(self):
        """Test that promotion meets performance targets (<5s)."""
        # RED PHASE: This test will fail until performance optimization is implemented
        import time
        note_path = "knowledge/Fleeting Notes/integration-test-note.md"

        start_time = time.time()

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--promote-note", note_path
        ], capture_output=True, text=True)

        end_time = time.time()
        processing_time = end_time - start_time

        assert result.returncode == 0
        assert processing_time < 5.0, f"Promotion took {processing_time:.2f}s, should be <5s"
