import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.utils.frontmatter import parse_frontmatter, build_frontmatter


class TestParseFrontmatter:
    """Test cases for parse_frontmatter function."""

    def test_parse_valid_frontmatter(self):
        """Test parsing valid YAML frontmatter."""
        content = """---
type: permanent
created: 2025-08-18 20:30
status: published
tags: [test, frontmatter, yaml]
visibility: private
---

This is the body content.
More content here."""

        metadata, body = parse_frontmatter(content)

        assert metadata['type'] == 'permanent'
        assert metadata['created'] == '2025-08-18 20:30'
        assert metadata['status'] == 'published'
        assert metadata['tags'] == ['test', 'frontmatter', 'yaml']
        assert metadata['visibility'] == 'private'
        assert body.strip() == "This is the body content.\nMore content here."

    def test_parse_no_frontmatter(self):
        """Test parsing content with no frontmatter."""
        content = "Just body content with no frontmatter."

        metadata, body = parse_frontmatter(content)

        assert metadata == {}
        assert body == content

    def test_parse_empty_frontmatter(self):
        """Test parsing content with empty frontmatter."""
        content = """---
---

Body content after empty frontmatter."""

        metadata, body = parse_frontmatter(content)

        assert metadata == {}
        assert body.strip() == "Body content after empty frontmatter."

    def test_parse_malformed_yaml(self):
        """Test parsing content with malformed YAML - should return safe defaults."""
        content = """---
type: permanent
invalid_yaml: [unclosed list
status: published
---

Body content."""

        metadata, body = parse_frontmatter(content)

        # Should return empty dict for malformed YAML and preserve original content
        assert metadata == {}
        assert "Body content." in body

    def test_parse_no_closing_delimiter(self):
        """Test parsing frontmatter without closing delimiter."""
        content = """---
type: fleeting
created: 2025-08-18 20:30

Body content without closing delimiter."""

        metadata, body = parse_frontmatter(content)

        # Should treat as no frontmatter when delimiter is missing
        assert metadata == {}
        assert content in body

    def test_parse_nested_yaml_structures(self):
        """Test parsing complex nested YAML structures."""
        content = """---
type: literature
created: 2025-08-18 20:30
source:
  url: https://example.com
  title: "Test Article"
  author: "John Doe"
claims:
  - "First claim here"
  - "Second claim here"
tags: [research, literature, claims]
---

Literature note body."""

        metadata, body = parse_frontmatter(content)

        assert metadata['type'] == 'literature'
        assert metadata['source']['url'] == 'https://example.com'
        assert metadata['source']['title'] == 'Test Article'
        assert len(metadata['claims']) == 2
        assert metadata['claims'][0] == 'First claim here'
        assert body.strip() == "Literature note body."


class TestBuildFrontmatter:
    """Test cases for build_frontmatter function."""

    def test_build_basic_frontmatter(self):
        """Test building basic frontmatter with proper field ordering."""
        metadata = {
            'tags': ['test', 'frontmatter'],
            'type': 'permanent',
            'status': 'published',
            'created': '2025-08-18 20:30',
            'visibility': 'private'
        }
        body = "This is the body content."

        result = build_frontmatter(metadata, body)

        # Check that it contains YAML delimiters
        assert result.startswith('---\n')
        assert '\n---\n' in result
        assert result.endswith(body)

        # Check field ordering - created should come first
        lines = result.split('\n')
        yaml_lines = []
        in_frontmatter = False
        for line in lines:
            if line == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    break
            elif in_frontmatter:
                yaml_lines.append(line)

        # created should be first field
        assert yaml_lines[0].startswith('created:')
        # type should be second
        assert yaml_lines[1].startswith('type:')
        # status should be third
        assert yaml_lines[2].startswith('status:')

    def test_build_empty_frontmatter(self):
        """Test building with empty metadata."""
        metadata = {}
        body = "Just body content."

        result = build_frontmatter(metadata, body)

        # Should return just the body when no metadata
        assert result == body

    def test_build_with_nested_structures(self):
        """Test building frontmatter with nested YAML structures."""
        metadata = {
            'created': '2025-08-18 20:30',
            'type': 'literature',
            'source': {
                'url': 'https://example.com',
                'title': 'Test Article'
            },
            'claims': ['First claim', 'Second claim']
        }
        body = "Literature note body."

        result = build_frontmatter(metadata, body)

        assert 'source:' in result
        assert 'url: https://example.com' in result
        assert 'title: Test Article' in result
        assert 'claims:' in result
        assert '- First claim' in result

    def test_build_preserves_yaml_formatting(self):
        """Test that building preserves consistent YAML formatting."""
        metadata = {
            'created': '2025-08-18 20:30',
            'type': 'permanent',
            'tags': ['tag1', 'tag2', 'tag3'],
            'boolean_field': True,
            'numeric_field': 42
        }
        body = "Test body."

        result = build_frontmatter(metadata, body)

        # Check proper YAML formatting
        # Tags must be inline array style
        assert 'tags: [tag1, tag2, tag3]' in result
        assert 'boolean_field: true' in result
        assert 'numeric_field: 42' in result

    def test_build_enforces_inline_tags(self):
        """Tags must be rendered as inline arrays, never hyphen lists."""
        metadata = {
            'created': '2025-08-18 20:30',
            'type': 'permanent',
            'tags': ['alpha', 'beta'],
        }
        body = "Body"
        out = build_frontmatter(metadata, body)
        # Enforce inline formatting
        assert 'tags: [alpha, beta]' in out
        # Ensure hyphen list form is not used for tags
        assert 'tags:\n- alpha' not in out


class TestFrontmatterRoundtrip:
    """Test cases for roundtrip consistency between parse and build."""

    def test_roundtrip_consistency(self):
        """Test that parse -> build -> parse produces consistent results."""
        original_content = """---
created: 2025-08-18 20:30
type: permanent
status: published
tags: [test, roundtrip]
visibility: private
---

This is test content for roundtrip testing."""

        # First parse
        metadata1, body1 = parse_frontmatter(original_content)

        # Build back
        rebuilt_content = build_frontmatter(metadata1, body1)

        # Parse again
        metadata2, body2 = parse_frontmatter(rebuilt_content)

        # Should be identical
        assert metadata1 == metadata2
        assert body1 == body2

    def test_field_ordering_consistency(self):
        """Test that field ordering is preserved across roundtrips."""
        metadata = {
            'visibility': 'private',
            'tags': ['test'],
            'type': 'permanent',
            'status': 'published',
            'created': '2025-08-18 20:30'
        }
        body = "Test body."

        # Build once
        content1 = build_frontmatter(metadata, body)

        # Parse and build again
        parsed_metadata, parsed_body = parse_frontmatter(content1)
        content2 = build_frontmatter(parsed_metadata, parsed_body)

        # Field ordering should be consistent
        # Extract field order from both
        def extract_field_order(content):
            lines = content.split('\n')
            fields = []
            in_frontmatter = False
            for line in lines:
                if line == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                    else:
                        break
                elif in_frontmatter and ':' in line:
                    field_name = line.split(':')[0].strip()
                    fields.append(field_name)
            return fields

        fields1 = extract_field_order(content1)
        fields2 = extract_field_order(content2)
        assert fields1 == fields2
