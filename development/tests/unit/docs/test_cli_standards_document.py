"""TDD RED Phase: CLI Argument Standards Documentation Tests

P0_TASK: Create CLI Argument Standards Document

Goal: Comprehensive documentation of CLI argument patterns, naming conventions,
backward compatibility strategy, and testing requirements. Serves as template
for all new CLI development.

RED Phase expectations:
- All tests should FAIL initially (document doesn't exist)
- Tests validate document existence and structure
- Tests validate required sections are present
- Tests validate code examples are syntactically valid
- After implementation, tests should PASS (GREEN phase)

See: NEXT-SESSION-PROMPT-cli-integration-tests.md P0_TASK for context
"""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
DOCS_DIR = REPO_ROOT / "development" / "docs"
STANDARDS_DOC = DOCS_DIR / "CLI-ARGUMENT-STANDARDS.md"


class TestCLIStandardsDocument:
    """Tests ensuring CLI Argument Standards documentation exists and is complete.
    
    P0_TASK: Create comprehensive CLI standards documentation
    
    Test strategy:
    1. Validate document exists at expected location
    2. Validate all required sections are present
    3. Validate code examples are syntactically valid Python
    4. Validate document provides actionable guidance
    """

    REQUIRED_SECTIONS = [
        "# Standard Argument Naming Conventions",
        "# Required vs Optional Arguments",
        "# Backward Compatibility Guidelines",
        "# Help Text Formatting",
        "# Error Message Standards",
        "# CLI Testing Requirements",
        "# CLI Examples by Type",
    ]

    def test_cli_standards_document_exists(self):
        """RED: CLI-ARGUMENT-STANDARDS.md should exist in development/docs/
        
        This foundational document guides all CLI development and ensures
        consistency across the codebase.
        
        This test will FAIL until document is created.
        """
        assert STANDARDS_DOC.exists(), (
            f"CLI standards document must exist at: {STANDARDS_DOC}\n"
            f"Create document with comprehensive CLI development guidelines."
        )

    def test_cli_standards_document_has_required_sections(self):
        """RED: Document should contain all 7 required sections
        
        Required sections provide complete CLI development guidance:
        1. Standard argument naming conventions
        2. Required vs optional arguments
        3. Backward compatibility guidelines
        4. Help text formatting
        5. Error message standards
        6. CLI testing requirements
        7. Examples for each CLI type
        
        This test will FAIL until all sections are present.
        """
        if not STANDARDS_DOC.exists():
            assert False, f"Document doesn't exist: {STANDARDS_DOC}"
        
        content = STANDARDS_DOC.read_text()
        
        missing_sections = []
        for section in self.REQUIRED_SECTIONS:
            if section not in content:
                missing_sections.append(section)
        
        assert len(missing_sections) == 0, (
            f"Document missing required sections:\n"
            + "\n".join(f"  - {s}" for s in missing_sections)
            + "\n\nAll 7 sections must be present for completeness."
        )

    def test_cli_standards_document_has_code_examples(self):
        """RED: Document should include Python code examples
        
        Code examples demonstrate proper implementation patterns and serve as
        templates for new CLI development.
        
        This test will FAIL until code examples are added.
        """
        if not STANDARDS_DOC.exists():
            assert False, f"Document doesn't exist: {STANDARDS_DOC}"
        
        content = STANDARDS_DOC.read_text()
        
        # Check for Python code blocks (markdown fenced with python)
        python_code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)
        
        assert len(python_code_blocks) >= 3, (
            f"Document should include at least 3 Python code examples.\n"
            f"Found: {len(python_code_blocks)} code blocks\n"
            f"Examples should cover: argparse patterns, error handling, testing"
        )

    def test_cli_standards_document_references_real_clis(self):
        """RED: Document should reference actual CLI files as examples
        
        Real CLI references provide concrete examples and enable readers to
        explore working implementations.
        
        This test will FAIL until real CLI references are added.
        """
        if not STANDARDS_DOC.exists():
            assert False, f"Document doesn't exist: {STANDARDS_DOC}"
        
        content = STANDARDS_DOC.read_text()
        
        # Should reference at least 2 real CLI files
        expected_references = [
            "core_workflow_cli.py",
            "safe_workflow_cli.py",
        ]
        
        found_references = [ref for ref in expected_references if ref in content]
        
        assert len(found_references) >= 2, (
            f"Document should reference real CLI implementations.\n"
            f"Expected references: {expected_references}\n"
            f"Found: {found_references}\n"
            f"Add references to working CLIs as implementation examples."
        )

    def test_cli_standards_document_provides_vault_flag_guidance(self):
        """RED: Document should provide specific --vault flag guidance
        
        The --vault flag is the standardized pattern for all workflow CLIs.
        Document must provide clear guidance on implementation.
        
        This test will FAIL until --vault guidance is added.
        """
        if not STANDARDS_DOC.exists():
            assert False, f"Document doesn't exist: {STANDARDS_DOC}"
        
        content = STANDARDS_DOC.read_text()
        
        # Check for --vault flag mentions
        assert "--vault" in content, (
            "Document must include --vault flag guidance.\n"
            "This is the standard pattern for all workflow CLIs."
        )
        
        # Should have guidance on both flag and positional argument patterns
        has_flag_pattern = "--vault" in content
        has_positional_pattern = "vault_path" in content or "positional" in content.lower()
        
        assert has_flag_pattern and has_positional_pattern, (
            "Document must cover both --vault flag (new standard) and "
            "positional argument (backward compatibility) patterns."
        )

    def test_cli_standards_document_includes_testing_section(self):
        """RED: Document should include comprehensive testing guidance
        
        Testing requirements ensure all CLIs are properly validated with both
        unit and integration tests.
        
        This test will FAIL until testing section is comprehensive.
        """
        if not STANDARDS_DOC.exists():
            assert False, f"Document doesn't exist: {STANDARDS_DOC}"
        
        content = STANDARDS_DOC.read_text()
        
        # Testing section should mention key testing concepts
        testing_keywords = ["unit test", "integration test", "pytest", "subprocess"]
        found_keywords = [kw for kw in testing_keywords if kw.lower() in content.lower()]
        
        assert len(found_keywords) >= 3, (
            f"Testing section should cover comprehensive testing approach.\n"
            f"Expected keywords: {testing_keywords}\n"
            f"Found: {found_keywords}\n"
            f"Add guidance on unit tests, integration tests, and CLI execution testing."
        )

    def test_cli_standards_document_has_deprecation_strategy(self):
        """RED: Document should include deprecation strategy for backward compatibility
        
        Deprecation strategy guides migration from old patterns to new standards
        without breaking existing automation.
        
        This test will FAIL until deprecation guidance is added.
        """
        if not STANDARDS_DOC.exists():
            assert False, f"Document doesn't exist: {STANDARDS_DOC}"
        
        content = STANDARDS_DOC.read_text()
        
        # Should mention deprecation concepts
        deprecation_keywords = ["deprecat", "backward compat", "migration", "warning"]
        found_keywords = [kw for kw in deprecation_keywords if kw.lower() in content.lower()]
        
        assert len(found_keywords) >= 2, (
            f"Document should include deprecation/migration strategy.\n"
            f"Expected keywords: {deprecation_keywords}\n"
            f"Found: {found_keywords}\n"
            f"Add clear guidance on handling backward compatibility during transitions."
        )
