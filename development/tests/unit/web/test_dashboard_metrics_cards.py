"""
TDD RED Phase: Dashboard Metrics Cards Integration Tests
Phase 3.2 P1 - Dashboard Metrics Visualization

These tests define the expected behavior for dashboard metrics cards.
All tests should FAIL initially (RED phase).

Test Coverage:
- Dashboard route and template rendering
- Metrics cards HTML structure
- JavaScript fetch integration
- Card update logic and error handling
- Mobile-responsive layout
- Auto-refresh functionality
"""

import sys
from pathlib import Path
import pytest
import re

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
src_dir = project_root / "development" / "src"
sys.path.insert(0, str(src_dir))

# Import Flask app
web_ui_dir = project_root / "web_ui"
sys.path.insert(0, str(web_ui_dir))


class TestDashboardMetricsCards:
    """Test suite for dashboard metrics cards visualization."""

    @pytest.fixture
    def client(self):
        """Create Flask test client."""
        from app import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_dashboard_route_exists(self, client):
        """Test that /dashboard route exists and returns 200."""
        response = client.get("/dashboard")
        assert (
            response.status_code == 200
        ), "Route /dashboard should exist and return 200"

    def test_dashboard_renders_template(self, client):
        """Test that dashboard renders dashboard.html template."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Should contain dashboard-specific elements
        assert (
            "dashboard" in html.lower() or "metrics" in html.lower()
        ), "Dashboard page should render dashboard/metrics content"

    def test_dashboard_has_metrics_section(self, client):
        """Test that dashboard includes metrics cards section."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Look for metrics section container
        has_metrics_section = (
            'id="metrics-cards"' in html
            or 'class="metrics-cards"' in html
            or re.search(r'<section[^>]*class="[^"]*metrics[^"]*"', html, re.IGNORECASE)
        )

        assert (
            has_metrics_section
        ), "Dashboard must include a metrics cards section (#metrics-cards or .metrics-cards)"

    def test_metrics_section_has_card_grid(self, client):
        """Test that metrics section uses grid layout for cards."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Check for grid layout classes (Bootstrap row/col or CSS grid)
        has_grid = (
            'class="row"' in html
            or 'class="grid"' in html
            or 'class="metrics-grid"' in html
            or re.search(r'class="[^"]*grid[^"]*"', html, re.IGNORECASE)
        )

        assert has_grid, "Metrics section should use grid layout for responsive cards"

    def test_counter_card_elements_exist(self, client):
        """Test that counter metric cards have proper structure."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Look for counter cards (should have data-metric-type="counter")
        has_counter_card = 'data-metric-type="counter"' in html or re.search(
            r'class="[^"]*counter[^"]*card[^"]*"', html, re.IGNORECASE
        )

        assert (
            has_counter_card
        ), "Dashboard should have at least one counter metric card"

        # Check for value display element
        has_value_element = "data-metric-value" in html or re.search(
            r'class="[^"]*metric-value[^"]*"', html, re.IGNORECASE
        )

        assert (
            has_value_element
        ), "Counter cards must have element for displaying metric value"

    def test_gauge_card_elements_exist(self, client):
        """Test that gauge metric cards have proper structure."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Look for gauge cards
        has_gauge_card = 'data-metric-type="gauge"' in html or re.search(
            r'class="[^"]*gauge[^"]*card[^"]*"', html, re.IGNORECASE
        )

        assert has_gauge_card, "Dashboard should have at least one gauge metric card"

    def test_histogram_card_elements_exist(self, client):
        """Test that histogram metric cards have proper structure."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Look for histogram cards
        has_histogram_card = 'data-metric-type="histogram"' in html or re.search(
            r'class="[^"]*histogram[^"]*card[^"]*"', html, re.IGNORECASE
        )

        assert (
            has_histogram_card
        ), "Dashboard should have at least one histogram metric card"

    def test_dashboard_includes_metrics_javascript(self, client):
        """Test that dashboard includes metrics.js for fetch logic."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Should include metrics.js script
        assert (
            "metrics.js" in html
        ), "Dashboard must include metrics.js for API fetch functionality"

    def test_metrics_cards_have_error_state_elements(self, client):
        """Test that cards include error state display elements."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Look for error state elements (hidden by default)
        has_error_elements = "data-error-message" in html or re.search(
            r'class="[^"]*error[^"]*"', html, re.IGNORECASE
        )

        assert (
            has_error_elements
        ), "Dashboard should have error state elements for failed fetch handling"

    def test_metrics_cards_have_loading_state_elements(self, client):
        """Test that cards include loading state indicators."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Look for loading/spinner elements
        has_loading_elements = (
            "data-loading" in html
            or re.search(r'class="[^"]*loading[^"]*"', html, re.IGNORECASE)
            or re.search(r'class="[^"]*spinner[^"]*"', html, re.IGNORECASE)
        )

        assert (
            has_loading_elements
        ), "Dashboard should have loading indicators for initial fetch state"

    def test_dashboard_has_mobile_responsive_meta(self, client):
        """Test that dashboard includes viewport meta for mobile responsiveness."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Should have viewport meta tag (likely in base template)
        assert (
            "viewport" in html and "width=device-width" in html
        ), "Dashboard should have viewport meta tag for mobile responsiveness"

    def test_metrics_cards_have_timestamp_display(self, client):
        """Test that cards display last updated timestamp."""
        response = client.get("/dashboard")
        html = response.data.decode()

        # Look for timestamp elements
        has_timestamp = (
            "<time" in html
            or "data-timestamp" in html
            or re.search(r'class="[^"]*timestamp[^"]*"', html, re.IGNORECASE)
        )

        assert has_timestamp, "Dashboard should display timestamp for metrics freshness"


class TestMetricsJavaScriptIntegration:
    """Test suite for metrics.js fetch and update logic.

    Note: These tests verify that metrics.js file exists and has proper structure.
    Full JavaScript testing would require a headless browser (Selenium/Playwright).
    """

    def test_metrics_js_file_exists(self):
        """Test that metrics.js file exists in static directory."""
        metrics_js_path = project_root / "web_ui" / "static" / "js" / "metrics.js"

        assert (
            metrics_js_path.exists()
        ), "metrics.js file must exist at web_ui/static/js/metrics.js"

    def test_metrics_js_has_metricsupdater_class(self):
        """Test that metrics.js defines MetricsUpdater class."""
        metrics_js_path = project_root / "web_ui" / "static" / "js" / "metrics.js"

        if not metrics_js_path.exists():
            pytest.skip("metrics.js not created yet - expected in RED phase")

        content = metrics_js_path.read_text()

        # Should define MetricsUpdater class
        assert (
            "class MetricsUpdater" in content or "function MetricsUpdater" in content
        ), "metrics.js must define MetricsUpdater class/function"

    def test_metrics_js_has_fetch_logic(self):
        """Test that metrics.js includes fetch() API calls."""
        metrics_js_path = project_root / "web_ui" / "static" / "js" / "metrics.js"

        if not metrics_js_path.exists():
            pytest.skip("metrics.js not created yet - expected in RED phase")

        content = metrics_js_path.read_text()

        # Should use fetch API
        assert (
            "fetch(" in content and "/api/metrics" in content
        ), "metrics.js must use fetch() to call /api/metrics endpoint"


class TestDashboardCSS:
    """Test suite for dashboard.css styling."""

    def test_dashboard_css_file_exists(self):
        """Test that dashboard.css file exists."""
        css_path = project_root / "web_ui" / "static" / "css" / "dashboard.css"

        assert (
            css_path.exists()
        ), "dashboard.css file must exist at web_ui/static/css/dashboard.css"

    def test_dashboard_css_has_card_styles(self):
        """Test that dashboard.css includes card styling."""
        css_path = project_root / "web_ui" / "static" / "css" / "dashboard.css"

        if not css_path.exists():
            pytest.skip("dashboard.css not created yet - expected in RED phase")

        content = css_path.read_text()

        # Should have card-related styles
        assert (
            "card" in content.lower() or "metric" in content.lower()
        ), "dashboard.css must include card/metric styling"

    def test_dashboard_css_has_responsive_breakpoints(self):
        """Test that dashboard.css includes media queries for responsive layout."""
        css_path = project_root / "web_ui" / "static" / "css" / "dashboard.css"

        if not css_path.exists():
            pytest.skip("dashboard.css not created yet - expected in RED phase")

        content = css_path.read_text()

        # Should have media queries for mobile responsiveness
        assert (
            "@media" in content
        ), "dashboard.css should include @media queries for responsive design"
