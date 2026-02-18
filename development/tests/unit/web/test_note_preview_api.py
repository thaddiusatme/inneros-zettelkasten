"""
Test suite for /api/note-content endpoint - Note Preview API
TDD RED Phase: All tests should FAIL before implementation.
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
src_dir = project_root / "development" / "src"
sys.path.insert(0, str(src_dir))

# Import Flask app
web_ui_dir = project_root / "web_ui"
sys.path.insert(0, str(web_ui_dir))


@pytest.fixture
def client():
    """Create test Flask client."""
    from app import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def vault_with_note(tmp_path):
    """Create a temporary vault with a sample note for testing."""
    inbox = tmp_path / "Inbox"
    inbox.mkdir()

    note = inbox / "test-note.md"
    note.write_text(
        "---\n"
        "title: Test Note\n"
        "quality_score: 0.85\n"
        "tags:\n"
        "  - testing\n"
        "  - tdd\n"
        "---\n"
        "\n"
        "# Test Note\n"
        "\n"
        "This is the body of the test note.\n",
        encoding="utf-8",
    )
    return tmp_path


class TestNoteContentEndpoint:
    """Tests for the /api/note-content API endpoint."""

    def test_note_content_endpoint_exists(self, client):
        """GET /api/note-content should return a non-404 status."""
        response = client.get("/api/note-content?filename=test.md&source=Inbox")
        assert response.status_code != 404, "Endpoint /api/note-content should exist"

    def test_note_content_returns_json(self, client, vault_with_note):
        """Response content-type should be application/json."""
        response = client.get(
            f"/api/note-content?filename=test-note.md&source=Inbox"
            f"&path={vault_with_note}"
        )
        assert "application/json" in response.content_type

    def test_note_content_returns_required_fields(self, client, vault_with_note):
        """JSON response must include title, frontmatter, body, and path."""
        response = client.get(
            f"/api/note-content?filename=test-note.md&source=Inbox"
            f"&path={vault_with_note}"
        )
        data = response.get_json()
        assert data is not None, "Response should be valid JSON"
        for field in ("title", "frontmatter", "body", "path"):
            assert field in data, f"Response missing required field: {field}"

    def test_note_content_parses_frontmatter(self, client, vault_with_note):
        """YAML frontmatter should be parsed into a dict, body separated."""
        response = client.get(
            f"/api/note-content?filename=test-note.md&source=Inbox"
            f"&path={vault_with_note}"
        )
        data = response.get_json()
        assert isinstance(data["frontmatter"], dict)
        assert data["frontmatter"].get("quality_score") == 0.85
        assert "tags" in data["frontmatter"]
        assert "# Test Note" in data["body"]

    def test_note_content_rejects_path_traversal(self, client):
        """Filenames with path traversal sequences must be rejected (400)."""
        response = client.get(
            "/api/note-content?filename=../../etc/passwd&source=Inbox"
        )
        assert (
            response.status_code == 400
        ), "Path traversal in filename should return 400"

    def test_note_content_returns_404_for_missing_file(self, client, vault_with_note):
        """Non-existent note should return 404."""
        response = client.get(
            f"/api/note-content?filename=nonexistent.md&source=Inbox"
            f"&path={vault_with_note}"
        )
        assert response.status_code == 404

    def test_note_content_requires_filename_param(self, client):
        """Missing filename parameter should return 400."""
        response = client.get("/api/note-content?source=Inbox")
        assert response.status_code == 400, "Missing filename param should return 400"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
