"""
Test suite for /analytics route to prevent type errors
Phase 3.2 P1 - Analytics Route Safety Tests
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

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


class TestAnalyticsRouteTypeSafety:
    """Tests to ensure analytics route handles all data types correctly."""
    
    def test_analytics_route_exists(self, client):
        """Test that /analytics route is accessible."""
        response = client.get('/analytics')
        # Should either succeed or show error page, not 404
        assert response.status_code in [200, 500]
    
    def test_analytics_returns_html_not_json(self, client):
        """Test that analytics returns HTML content."""
        response = client.get('/analytics')
        assert 'text/html' in response.content_type
    
    @patch('app.NoteAnalytics')
    def test_analytics_handles_dict_response(self, mock_analytics, client):
        """Test analytics route properly handles dictionary response from generate_report()."""
        # Mock generate_report to return valid dict
        mock_instance = MagicMock()
        mock_instance.generate_report.return_value = {
            'overview': {
                'total_notes': 100,
                'notes_with_ai_summaries': 10
            },
            'quality_metrics': {
                'high_quality_notes': 30,
                'medium_quality_notes': 50,
                'low_quality_notes': 20
            },
            'recommendations': ['Add more tags', 'Link notes']
        }
        mock_analytics.return_value = mock_instance
        
        response = client.get('/analytics')
        assert response.status_code == 200
        html = response.data.decode()
        
        # Verify we're calling .get() on a dict, not a string
        # This would fail if stats was a string
        assert 'Error' not in html or "'str' object has no attribute 'get'" not in html
    
    @patch('app.NoteAnalytics')
    def test_analytics_handles_empty_dict_response(self, mock_analytics, client):
        """Test analytics route handles empty dictionary without crashing."""
        mock_instance = MagicMock()
        mock_instance.generate_report.return_value = {}
        mock_analytics.return_value = mock_instance
        
        response = client.get('/analytics')
        assert response.status_code == 200
        html = response.data.decode()
        
        # Should gracefully handle missing keys with .get() defaults
        assert "'str' object has no attribute 'get'" not in html
    
    @patch('app.NoteAnalytics')
    def test_analytics_handles_error_dict_response(self, mock_analytics, client):
        """Test analytics route handles error dictionary."""
        mock_instance = MagicMock()
        mock_instance.generate_report.return_value = {"error": "No notes found"}
        mock_analytics.return_value = mock_instance
        
        response = client.get('/analytics')
        assert response.status_code == 200
        html = response.data.decode()
        
        # Should handle error dict gracefully
        assert "'str' object has no attribute 'get'" not in html
    
    @patch('app.NoteAnalytics')
    def test_analytics_handles_exception_in_generate_report(self, mock_analytics, client):
        """Test analytics route handles exceptions from generate_report()."""
        mock_instance = MagicMock()
        mock_instance.generate_report.side_effect = Exception("Failed to analyze notes")
        mock_analytics.return_value = mock_instance
        
        response = client.get('/analytics')
        html = response.data.decode()
        
        # Should show error page, not crash with type error
        assert 'Error' in html
        assert "'str' object has no attribute 'get'" not in html
    
    @patch('app.NoteAnalytics')
    def test_analytics_stats_is_always_dict(self, mock_analytics, client):
        """CRITICAL: Test that stats variable is always treated as dict, never string."""
        # This is the core bug we're preventing
        mock_instance = MagicMock()
        
        # Try various problematic return types
        problematic_returns = [
            "error string",  # String instead of dict
            None,            # None instead of dict
            [],              # List instead of dict
            123,             # Number instead of dict
        ]
        
        for bad_return in problematic_returns:
            mock_instance.generate_report.return_value = bad_return
            mock_analytics.return_value = mock_instance
            
            response = client.get('/analytics')
            html = response.data.decode()
            
            # Should handle gracefully, not crash with AttributeError
            assert "'str' object has no attribute 'get'" not in html
            assert "'NoneType' object has no attribute 'get'" not in html
            assert "'list' object has no attribute 'get'" not in html
            assert "'int' object has no attribute 'get'" not in html
    
    @patch('app.NoteAnalytics')
    def test_analytics_type_guard_catches_string_return(self, mock_analytics, client):
        """Test that type guard catches and reports when generate_report() returns a string."""
        mock_instance = MagicMock()
        mock_instance.generate_report.return_value = "unexpected string error"
        mock_analytics.return_value = mock_instance
        
        response = client.get('/analytics')
        html = response.data.decode()
        
        # Should show error page with TypeError, not AttributeError
        assert 'Error' in html
        # Should mention it expected dict but got str
        assert 'Expected dict' in html or 'TypeError' in html.lower()
        # Should NOT have the original AttributeError
        assert "'str' object has no attribute 'get'" not in html
    
    def test_analytics_with_custom_vault_path(self, client):
        """Test analytics route with custom vault path parameter."""
        response = client.get('/analytics?path=/custom/vault')
        assert response.status_code in [200, 500]  # Should handle path parameter
    
    @patch('app.NoteAnalytics')
    def test_analytics_data_structure_is_correct(self, mock_analytics, client):
        """Test that dashboard_data structure is always correctly formatted."""
        mock_instance = MagicMock()
        mock_instance.generate_report.return_value = {
            'overview': {'total_notes': 50},
            'quality_metrics': {'high_quality_notes': 10},
            'recommendations': []
        }
        mock_analytics.return_value = mock_instance
        
        response = client.get('/analytics')
        assert response.status_code == 200
        
        # The page should render without type errors
        html = response.data.decode()
        assert 'AttributeError' not in html


class TestAnalyticsErrorHandling:
    """Tests for analytics error handling and resilience."""
    
    @patch('app.NoteAnalytics')
    def test_analytics_shows_user_friendly_error(self, mock_analytics, client):
        """Test that analytics shows user-friendly error messages."""
        mock_analytics.side_effect = FileNotFoundError("Vault not found")
        
        response = client.get('/analytics')
        html = response.data.decode()
        
        # Should show error template with user-friendly message
        assert 'Error' in html
        # Should not expose raw Python exception
        assert 'Traceback' not in html
    
    @patch('app.NoteAnalytics')
    def test_analytics_handles_permission_error(self, mock_analytics, client):
        """Test analytics handles permission errors gracefully."""
        mock_analytics.side_effect = PermissionError("Cannot read vault")
        
        response = client.get('/analytics')
        html = response.data.decode()
        
        assert 'Error' in html
        assert "'str' object has no attribute 'get'" not in html


class TestAnalyticsDataTypeGuards:
    """Tests to verify type guards prevent the bug."""
    
    def test_dict_get_on_string_raises_attribute_error(self):
        """Demonstrate the actual bug: calling .get() on a string."""
        bad_stats = "error message"
        
        # This is the bug - trying to call .get() on a string
        with pytest.raises(AttributeError, match="'str' object has no attribute 'get'"):
            overview = bad_stats.get('overview', {})
    
    def test_dict_get_on_dict_works(self):
        """Demonstrate correct behavior: calling .get() on a dict."""
        good_stats = {'overview': {'total_notes': 100}}
        
        # This works correctly
        overview = good_stats.get('overview', {})
        assert overview == {'total_notes': 100}
    
    def test_dict_get_on_none_raises_attribute_error(self):
        """Test that None also causes AttributeError."""
        bad_stats = None
        
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'get'"):
            overview = bad_stats.get('overview', {})


class TestAnalyticsDateHandling:
    """Tests for date/datetime handling in analytics."""
    
    def test_parse_date_handles_datetime_object(self):
        """Test that _parse_date handles datetime objects from YAML parser."""
        from datetime import datetime, date
        
        # Import NoteAnalytics for testing _parse_date
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent.parent.parent
        src_dir = project_root / 'development' / 'src'
        sys.path.insert(0, str(src_dir))
        
        from ai.analytics import NoteAnalytics
        
        # Create temp vault for testing
        analytics = NoteAnalytics("/tmp/test_vault")
        
        # Test datetime object (already parsed by YAML)
        dt = datetime(2025, 10, 16, 19, 43)
        result = analytics._parse_date(dt)
        assert result == dt
        
        # Test date object (from YAML date field)
        d = date(2025, 10, 16)
        result = analytics._parse_date(d)
        assert result is not None
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 16
        
        # Test string (traditional parsing)
        result = analytics._parse_date("2025-10-16")
        assert result is not None
        assert result.year == 2025


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
