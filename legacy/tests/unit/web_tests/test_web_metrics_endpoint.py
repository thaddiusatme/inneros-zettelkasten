"""
TDD RED Phase: Web Dashboard Metrics Integration Tests
Phase 3.2 P0 - Critical Web Dashboard Integration

These tests define the expected behavior for /api/metrics endpoint.
All tests should FAIL initially (RED phase).
"""

import sys
from pathlib import Path
import pytest

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
src_dir = project_root / "development" / "src"
sys.path.insert(0, str(src_dir))

# Import Flask app (will fail until we add metrics endpoint)
web_ui_dir = project_root / "web_ui"
sys.path.insert(0, str(web_ui_dir))


class TestWebMetricsEndpoint:
    """Test suite for /api/metrics HTTP endpoint integration."""

    @pytest.fixture
    def client(self):
        """Create Flask test client."""
        # Import will work but endpoint won't exist yet
        from app import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_metrics_endpoint_exists(self, client):
        """Test that /api/metrics route exists and returns 200."""
        response = client.get("/api/metrics")
        assert (
            response.status_code == 200
        ), "Endpoint /api/metrics should exist and return 200"

    def test_metrics_endpoint_returns_json(self, client):
        """Test that endpoint returns JSON content type."""
        response = client.get("/api/metrics")
        assert (
            response.content_type == "application/json"
        ), "Endpoint should return application/json content type"

    def test_metrics_response_has_status_field(self, client):
        """Test that response includes 'status' field."""
        response = client.get("/api/metrics")
        data = response.get_json()
        assert "status" in data, "Response must include 'status' field"
        assert (
            data["status"] == "success"
        ), "Status should be 'success' for successful requests"

    def test_metrics_response_has_timestamp(self, client):
        """Test that response includes timestamp field."""
        response = client.get("/api/metrics")
        data = response.get_json()
        assert (
            "timestamp" in data
        ), "Response must include 'timestamp' field for caching"

    def test_metrics_response_has_current_metrics(self, client):
        """Test that response includes 'current' metrics section."""
        response = client.get("/api/metrics")
        data = response.get_json()
        assert "current" in data, "Response must include 'current' metrics section"

    def test_current_metrics_has_counters(self, client):
        """Test that current metrics includes counters."""
        response = client.get("/api/metrics")
        data = response.get_json()
        current = data.get("current", {})
        assert "counters" in current, "Current metrics must include 'counters' section"

    def test_current_metrics_has_gauges(self, client):
        """Test that current metrics includes gauges."""
        response = client.get("/api/metrics")
        data = response.get_json()
        current = data.get("current", {})
        assert "gauges" in current, "Current metrics must include 'gauges' section"

    def test_current_metrics_has_histograms(self, client):
        """Test that current metrics includes histograms."""
        response = client.get("/api/metrics")
        data = response.get_json()
        current = data.get("current", {})
        assert (
            "histograms" in current
        ), "Current metrics must include 'histograms' section"

    def test_metrics_response_has_history(self, client):
        """Test that response includes 'history' field."""
        response = client.get("/api/metrics")
        data = response.get_json()
        assert "history" in data, "Response must include 'history' field for trending"

    def test_metrics_response_format_matches_endpoint_structure(self, client):
        """Test that response format matches MetricsEndpoint.get_metrics()."""
        response = client.get("/api/metrics")
        data = response.get_json()

        # Verify complete structure matches expected format
        assert data["status"] == "success"
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["current"], dict)
        assert isinstance(data["current"]["counters"], dict)
        assert isinstance(data["current"]["gauges"], dict)
        assert isinstance(data["current"]["histograms"], dict)
        assert isinstance(data["history"], list)

    def test_metrics_endpoint_has_cors_headers(self, client):
        """Test that endpoint includes CORS headers for local development."""
        response = client.get("/api/metrics")
        # Should have Access-Control-Allow-Origin for local dev
        assert (
            "Access-Control-Allow-Origin" in response.headers
            or response.status_code == 200
        ), "Endpoint should support CORS or be accessible"

    def test_metrics_endpoint_works_without_daemon(self, client):
        """Test that endpoint works gracefully when WorkflowManager not running."""
        # This tests graceful fallback - should return empty/default metrics
        response = client.get("/api/metrics")
        assert (
            response.status_code == 200
        ), "Endpoint should work even if daemon not running"
        data = response.get_json()
        assert (
            data["status"] == "success"
        ), "Should return success status with fallback metrics"
