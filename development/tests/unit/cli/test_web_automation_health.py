"""
Tests for Issue #20: Web UI /automation/health endpoint.

RED Phase: Verify the web UI serves automation health data.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure web_ui is importable
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "web_ui"))
sys.path.insert(0, str(PROJECT_ROOT / "development"))


@pytest.fixture
def web_client():
    """Create a test client for the web UI Flask app."""
    from web_ui.app import app

    app.config["TESTING"] = True
    # Enable the automation_health feature flag
    app.config.setdefault("FEATURE_FLAGS", {})["automation_health"] = True
    with app.test_client() as client:
        yield client


class TestAutomationHealthEndpoint:
    """Web UI /automation/health should return daemon status."""

    def test_endpoint_exists(self, web_client):
        """/automation/health should return 200."""
        with patch("web_ui.app.check_all") as mock_check:
            mock_check.return_value = {
                "overall_status": "OK",
                "overall_healthy": True,
                "automations": [],
                "checks": {},
                "errors": [],
            }
            response = web_client.get("/automation/health")
            assert response.status_code == 200

    def test_endpoint_renders_dashboard_skeleton(self, web_client):
        """/automation/health should return the live dashboard HTML skeleton."""
        with patch("web_ui.app.check_all") as mock_check:
            mock_check.return_value = {
                "overall_status": "OK",
                "overall_healthy": True,
                "automations": [],
                "checks": {},
                "errors": [],
            }
            response = web_client.get("/automation/health")
            html = response.data.decode()
            assert "Automation Health" in html
            assert "health-dashboard" in html
            assert "/api/automation/health" in html
            assert "POLL_INTERVAL" in html

    def test_endpoint_shows_errors(self, web_client):
        """/automation/health should display errors when daemons unhealthy."""
        with patch("web_ui.app.check_all") as mock_check:
            mock_check.return_value = {
                "overall_status": "ERROR",
                "overall_healthy": False,
                "automations": [
                    {
                        "name": "inneros_daemon",
                        "running": False,
                        "last_run_status": "failed",
                        "last_run_timestamp": "2026-02-16 13:00",
                        "error_message": "Process crashed",
                    },
                ],
                "checks": {"inneros_daemon": False},
                "errors": ["inneros_daemon: Process crashed"],
            }
            response = web_client.get("/automation/health")
            html = response.data.decode()
            assert (
                "ERROR" in html or "error" in html.lower() or "Process crashed" in html
            )


class TestAutomationHealthAPI:
    """/api/automation/health should return JSON for programmatic access."""

    def test_api_returns_json(self, web_client):
        """/api/automation/health should return JSON."""
        with patch("web_ui.app.check_all") as mock_check:
            mock_check.return_value = {
                "overall_status": "OK",
                "overall_healthy": True,
                "automations": [
                    {
                        "name": "inneros_daemon",
                        "running": True,
                        "last_run_status": "success",
                        "last_run_timestamp": "2026-02-16 14:00",
                        "error_message": None,
                    }
                ],
                "checks": {"inneros_daemon": True},
                "errors": [],
            }
            response = web_client.get("/api/automation/health")
            assert response.status_code == 200
            data = response.get_json()
            assert data["overall_status"] == "OK"
            assert len(data["automations"]) == 1

    def test_api_returns_503_when_unhealthy(self, web_client):
        """/api/automation/health should return 503 when daemons are down."""
        with patch("web_ui.app.check_all") as mock_check:
            mock_check.return_value = {
                "overall_status": "ERROR",
                "overall_healthy": False,
                "automations": [],
                "checks": {},
                "errors": ["daemon not running"],
            }
            response = web_client.get("/api/automation/health")
            assert response.status_code == 503
            data = response.get_json()
            assert data["overall_status"] == "ERROR"
