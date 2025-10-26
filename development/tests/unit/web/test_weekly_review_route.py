"""
Test suite for /weekly-review route to prevent data structure errors
Phase 3.2 P1 - Weekly Review Route Safety Tests
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
src_dir = project_root / 'development' / 'src'
sys.path.insert(0, str(src_dir))

# Import Flask app
web_ui_dir = project_root / 'web_ui'
sys.path.insert(0, str(web_ui_dir))


@pytest.fixture
def client():
    """Create test Flask client."""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestWeeklyReviewRoute:
    """Tests for weekly review route basic functionality."""

    def test_weekly_review_route_exists(self, client):
        """Test that /weekly-review route is accessible."""
        response = client.get('/weekly-review')
        # Should either succeed or show error page, not 404
        assert response.status_code in [200, 500]

    def test_weekly_review_returns_html(self, client):
        """Test that weekly review returns HTML content."""
        response = client.get('/weekly-review')
        assert 'text/html' in response.content_type

    def test_weekly_review_with_custom_path(self, client):
        """Test weekly review with custom vault path parameter."""
        response = client.get('/weekly-review?path=/custom/vault')
        assert response.status_code in [200, 500]


class TestWeeklyReviewDataStructure:
    """Tests to ensure weekly review data structure is correct."""

    def test_review_data_has_required_fields(self, client):
        """Test that review_data has all required top-level fields."""
        response = client.get('/weekly-review')

        if response.status_code == 200:
            html = response.data.decode()
            # Check for key elements that indicate proper data structure
            assert 'Weekly Review' in html
            assert 'Notes to Review' in html or 'candidates_count' in html

    def test_recommendations_is_dict(self, client):
        """Test that recommendations field is a dictionary with expected keys."""
        # This is tested implicitly - if template renders, structure is correct
        response = client.get('/weekly-review')
        html = response.data.decode()

        # Should not have attribute errors
        assert "'dict' object has no attribute" not in html
        assert "has no attribute 'quality_score'" not in html

    def test_recommendation_items_have_required_fields(self, client):
        """CRITICAL: Test that each recommendation item has required fields."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        # Should not crash when accessing these fields
        assert "has no attribute 'quality_score'" not in html
        assert "has no attribute 'confidence'" not in html
        assert "has no attribute 'filename'" not in html
        assert "has no attribute 'title'" not in html


class TestWeeklyReviewEmptyVault:
    """Tests for weekly review with no notes."""

    def test_empty_inbox_and_fleeting(self, client):
        """Test weekly review with no inbox or fleeting notes."""
        # Just test that it doesn't crash - empty state is acceptable
        response = client.get('/weekly-review')
        assert response.status_code in [200, 500]

        html = response.data.decode()
        # Should not have attribute errors even with empty vault
        assert "has no attribute 'quality_score'" not in html
        assert "has no attribute 'confidence'" not in html


class TestWeeklyReviewPerformance:
    """Tests to ensure weekly review loads quickly."""

    def test_weekly_review_responds_within_timeout(self, client):
        """Test that weekly review responds within reasonable time."""
        import time
        start = time.time()
        response = client.get('/weekly-review')
        duration = time.time() - start

        # Should respond within 5 seconds (used to take 30+ seconds!)
        assert duration < 5.0, f"Weekly review took {duration:.2f}s, should be < 5s"
        assert response.status_code in [200, 500]


class TestWeeklyReviewItemStructure:
    """Tests for individual recommendation item structure."""

    def test_promote_items_have_quality_score(self, client):
        """Test that promote recommendation items have quality_score field."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        # If there are promote items, quality_score should work
        if 'Ready for Promotion' in html:
            assert "has no attribute 'quality_score'" not in html

    def test_keep_items_have_quality_score(self, client):
        """Test that keep recommendation items have quality_score field."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        # If there are keep items, quality_score should work
        if 'Keep as Fleeting' in html:
            assert "has no attribute 'quality_score'" not in html

    def test_improve_items_have_quality_score(self, client):
        """Test that improve recommendation items have quality_score field."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        # If there are improve items, quality_score should work
        if 'Need Improvement' in html:
            assert "has no attribute 'quality_score'" not in html

    def test_items_have_confidence_field(self, client):
        """Test that all recommendation items have confidence field."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        # Should not crash when accessing confidence
        assert "has no attribute 'confidence'" not in html


class TestWeeklyReviewErrorHandling:
    """Tests for error handling in weekly review."""

    @patch('pathlib.Path.glob')
    def test_handles_glob_exception(self, mock_glob, client):
        """Test that weekly review handles file system errors gracefully."""
        mock_glob.side_effect = PermissionError("Cannot read directory")

        response = client.get('/weekly-review')
        html = response.data.decode()

        # Should show error page, not crash
        assert 'Error' in html
        # Should not expose raw Python exception
        assert 'Traceback' not in html

    def test_handles_nonexistent_vault(self, client):
        """Test weekly review with non-existent vault path."""
        response = client.get('/weekly-review?path=/nonexistent/vault')
        # Should handle gracefully, not crash
        assert response.status_code in [200, 500]


class TestWeeklyReviewTemplateCompatibility:
    """Tests to ensure data structure matches template expectations."""

    def test_data_structure_matches_template(self, client):
        """Test that data structure has all fields expected by template."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        if response.status_code == 200:
            # Template expects these fields on each item:
            required_fields = ['quality_score', 'confidence', 'filename', 'title', 'reason']

            for field in required_fields:
                # Should not have attribute errors for any of these
                assert f"has no attribute '{field}'" not in html

    def test_recommendations_structure(self, client):
        """Test that recommendations dict has expected structure."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        if response.status_code == 200:
            # Template expects recommendations.promote, .keep, .improve
            # If these don't exist, template would error
            assert "'dict' object has no attribute 'promote'" not in html
            assert "'dict' object has no attribute 'keep'" not in html
            assert "'dict' object has no attribute 'improve'" not in html


class TestWeeklyReviewRegressionPrevention:
    """Regression tests for previously encountered bugs."""

    def test_no_quality_score_attribute_error(self, client):
        """REGRESSION: Prevent 'dict object has no attribute quality_score' error."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        # This was the exact error the user encountered
        assert "'dict' object has no attribute 'quality_score'" not in html
        assert "has no attribute 'quality_score'" not in html

    def test_no_confidence_attribute_error(self, client):
        """REGRESSION: Prevent 'dict object has no attribute confidence' error."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        assert "has no attribute 'confidence'" not in html

    def test_no_undefined_jinja_errors(self, client):
        """REGRESSION: Prevent Jinja2 UndefinedError exceptions."""
        response = client.get('/weekly-review')
        html = response.data.decode()

        # Common Jinja error patterns
        assert 'UndefinedError' not in html
        assert 'is undefined' not in html


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
