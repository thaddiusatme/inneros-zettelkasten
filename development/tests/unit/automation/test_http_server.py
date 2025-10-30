"""
Tests for HTTP monitoring server.

TDD Iteration 6: HTTP Monitoring Endpoints
RED phase - All tests should fail until http_server.py is implemented.
"""

import pytest


class MockDaemon:
    """Mock daemon for testing HTTP endpoints.
    
    Attributes:
        screenshot_handler: Mock screenshot handler for testing
        smart_link_handler: Mock smart link handler for testing
        youtube_handler: Mock YouTube handler for testing HTTP server endpoints
        _running: Internal running state flag
    """

    def __init__(self):
        self.screenshot_handler = None
        self.smart_link_handler = None
        self.youtube_handler = None
        self._running = False

    def get_daemon_health(self) -> dict:
        """Mock health status."""
        return {
            "daemon": {
                "is_healthy": True,
                "status_code": 200,
                "checks": {"scheduler": True, "file_watcher": True},
            },
            "handlers": {
                "screenshot": {"is_healthy": "N/A", "events_processed": 0},
                "smart_link": {"is_healthy": "N/A", "events_processed": 0},
            },
        }

    def export_prometheus_metrics(self) -> str:
        """Mock Prometheus metrics."""
        return """# HELP inneros_handler_events_total Total events processed
# TYPE inneros_handler_events_total counter
inneros_handler_events_total 42

# HELP inneros_handler_processing_seconds Average processing time
# TYPE inneros_handler_processing_seconds gauge
inneros_handler_processing_seconds 0.123
"""

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def is_running(self):
        return self._running


# RED Phase Tests


def test_health_endpoint_returns_daemon_health():
    """
    Given: HTTP server with daemon
    When: GET /health request
    Then: JSON response with daemon health data
    """
    # This will fail: ModuleNotFoundError: No module named 'automation.http_server'
    from src.automation.http_server import create_app

    daemon = MockDaemon()
    app = create_app(daemon)
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = response.get_json()
    assert "daemon" in data
    assert "handlers" in data
    assert data["daemon"]["is_healthy"] is True


def test_metrics_endpoint_returns_prometheus_format():
    """
    Given: HTTP server with daemon
    When: GET /metrics request
    Then: Prometheus text exposition format returned
    """
    from src.automation.http_server import create_app

    daemon = MockDaemon()
    app = create_app(daemon)
    client = app.test_client()

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.content_type == "text/plain; charset=utf-8"

    text = response.get_data(as_text=True)
    assert "# HELP" in text
    assert "# TYPE" in text
    assert "inneros_handler_events_total" in text


def test_health_endpoint_handles_daemon_error():
    """
    Given: Daemon that raises exception
    When: GET /health request
    Then: 503 status with error message
    """
    from src.automation.http_server import create_app

    class FailingDaemon:
        def __init__(self):
            self.youtube_handler = None
        
        def get_daemon_health(self):
            raise Exception("Daemon health check failed")

    daemon = FailingDaemon()
    app = create_app(daemon)
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 503
    data = response.get_json()
    assert "error" in data


def test_metrics_endpoint_handles_daemon_error():
    """
    Given: Daemon that raises exception
    When: GET /metrics request
    Then: 503 status with error text
    """
    from src.automation.http_server import create_app

    class FailingDaemon:
        def __init__(self):
            self.youtube_handler = None
        
        def export_prometheus_metrics(self):
            raise Exception("Metrics export failed")

    daemon = FailingDaemon()
    app = create_app(daemon)
    client = app.test_client()

    response = client.get("/metrics")

    assert response.status_code == 503
    assert "error" in response.get_data(as_text=True).lower()


def test_app_creation_requires_daemon():
    """
    Given: No daemon provided
    When: create_app() called
    Then: TypeError raised
    """
    from src.automation.http_server import create_app

    with pytest.raises(TypeError):
        create_app()  # Missing required daemon argument


def test_unknown_route_returns_404():
    """
    Given: HTTP server
    When: GET /unknown request
    Then: 404 status returned
    """
    from src.automation.http_server import create_app

    daemon = MockDaemon()
    app = create_app(daemon)
    client = app.test_client()

    response = client.get("/unknown")

    assert response.status_code == 404


def test_health_endpoint_cors_headers():
    """
    Given: HTTP server
    When: GET /health request
    Then: CORS headers present for monitoring tools
    """
    from src.automation.http_server import create_app

    daemon = MockDaemon()
    app = create_app(daemon)
    client = app.test_client()

    response = client.get("/health")

    # CORS headers for monitoring dashboards
    assert "Access-Control-Allow-Origin" in response.headers


def test_root_endpoint_returns_info():
    """
    Given: HTTP server
    When: GET / request
    Then: Server info and available endpoints returned
    """
    from src.automation.http_server import create_app

    daemon = MockDaemon()
    app = create_app(daemon)
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    data = response.get_json()
    assert "name" in data
    assert "endpoints" in data
    assert "/health" in str(data["endpoints"])
    assert "/metrics" in str(data["endpoints"])
