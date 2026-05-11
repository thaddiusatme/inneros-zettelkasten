import sys
import os
import pytest

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from validate_metadata import validate_created_date, extract_frontmatter, parse_frontmatter, validate_metadata, has_templater_placeholders


def test_validate_created_date_valid_datetime():
    """Test that a valid datetime string passes validation."""
    assert validate_created_date("2025-07-20 14:30") is True

def test_validate_created_date_valid_date():
    """Test that a valid date string passes validation."""
    assert validate_created_date("2025-07-20") is True

def test_validate_created_date_invalid_format():
    """Test that an invalid date string fails validation."""
    assert validate_created_date("20-07-2025") is False

def test_validate_created_date_invalid_string():
    """Test that a non-date string fails validation."""
    assert validate_created_date("not a date") is False


# Fixture to provide the path to the test_data directory
@pytest.fixture
def test_data_path():
    return os.path.join(os.path.dirname(__file__), 'test_data')


# Tests for extract_frontmatter
def test_extract_frontmatter_valid(test_data_path):
    """Test extracting frontmatter from a valid note."""
    file_path = os.path.join(test_data_path, 'valid_note.md')
    frontmatter = extract_frontmatter(file_path)
    assert frontmatter is not None
    assert 'type: permanent' in frontmatter

def test_extract_frontmatter_invalid(test_data_path):
    """Test extracting frontmatter from a note with invalid metadata."""
    file_path = os.path.join(test_data_path, 'invalid_note.md')
    frontmatter = extract_frontmatter(file_path)
    assert frontmatter is not None
    assert 'type: unknown_type' in frontmatter

def test_extract_frontmatter_missing(test_data_path):
    """Test a note with missing frontmatter."""
    file_path = os.path.join(test_data_path, 'missing_frontmatter_note.md')
    frontmatter = extract_frontmatter(file_path)
    assert frontmatter is None


# Tests for validate_metadata
def test_validate_metadata_valid(test_data_path):
    """Test validating a note with correct metadata."""
    file_path = os.path.join(test_data_path, 'valid_note.md')
    frontmatter = extract_frontmatter(file_path)
    metadata = parse_frontmatter(frontmatter)
    errors = validate_metadata(metadata, file_path)
    assert not errors

def test_validate_metadata_invalid(test_data_path):
    """Test validating a note with incorrect metadata."""
    file_path = os.path.join(test_data_path, 'invalid_note.md')
    frontmatter = extract_frontmatter(file_path)
    metadata = parse_frontmatter(frontmatter)
    errors = validate_metadata(metadata, file_path)
    assert len(errors) > 0
    assert any("Invalid type" in e for e in errors)
    assert any("Invalid created date format" in e for e in errors)


# Tests for templater placeholder detection
def test_has_templater_placeholders_with_date_token():
    """Test that {{date:...}} tokens are detected as templater placeholders."""
    frontmatter = """---
type: fleeting
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
---"""
    assert has_templater_placeholders(frontmatter) is True


def test_has_templater_placeholders_with_ejs_token():
    """Test that <%...%> tokens are detected as templater placeholders."""
    frontmatter = """---
type: fleeting
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
---"""
    assert has_templater_placeholders(frontmatter) is True


def test_has_templater_placeholders_with_ejs_equals():
    """Test that <%=...%> tokens are detected as templater placeholders."""
    frontmatter = """---
type: fleeting
created: <%= tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
---"""
    assert has_templater_placeholders(frontmatter) is True


def test_has_templater_placeholders_clean_yaml():
    """Test that clean YAML without placeholders returns False."""
    frontmatter = """---
type: fleeting
created: 2025-08-20 16:30
status: inbox
---"""
    assert has_templater_placeholders(frontmatter) is False


def test_has_templater_placeholders_empty_string():
    """Test that empty string returns False."""
    assert has_templater_placeholders("") is False


def test_has_templater_placeholders_none():
    """Test that None input returns False."""
    assert has_templater_placeholders(None) is False
