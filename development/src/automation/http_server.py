"""
HTTP Monitoring Server - Thin Flask app for daemon health and metrics endpoints.

TDD Iteration 6: HTTP Monitoring Endpoints
Provides /health and /metrics endpoints for external monitoring.

Architecture:
- Thin HTTP layer with zero business logic
- Delegates all work to AutomationDaemon methods
- CORS-enabled for monitoring dashboards
- Error handling with proper HTTP status codes

Size: ~100 LOC (ADR-001 compliant)
"""

from flask import Flask, jsonify, Response
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .daemon import AutomationDaemon


def create_app(daemon: 'AutomationDaemon') -> Flask:
    """
    Create Flask app with health and metrics endpoints.
    
    Args:
        daemon: AutomationDaemon instance to monitor
        
    Returns:
        Configured Flask application
        
    Raises:
        TypeError: If daemon is not provided
    """
    app = Flask(__name__)
    
    # Enable CORS for monitoring dashboards
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    @app.route('/')
    def root():
        """Server info and available endpoints."""
        return jsonify({
            'name': 'InnerOS Automation Daemon Monitoring',
            'version': '1.0.0',
            'endpoints': {
                '/': 'Server information',
                '/health': 'Daemon and handler health status (JSON)',
                '/metrics': 'Prometheus metrics (text)'
            }
        })
    
    @app.route('/health')
    def health():
        """
        Health endpoint returning daemon and handler status.
        
        Returns:
            JSON with daemon health and handler metrics
            
        Status Codes:
            200: Healthy
            503: Unhealthy or error
        """
        try:
            health_data = daemon.get_daemon_health()
            
            # Determine overall health status
            is_healthy = health_data.get('daemon', {}).get('is_healthy', False)
            status_code = 200 if is_healthy else 503
            
            return jsonify(health_data), status_code
            
        except Exception as e:
            return jsonify({
                'error': 'Health check failed',
                'message': str(e)
            }), 503
    
    @app.route('/metrics')
    def metrics():
        """
        Metrics endpoint returning Prometheus exposition format.
        
        Returns:
            Text in Prometheus format with handler metrics
            
        Status Codes:
            200: Success
            503: Error
        """
        try:
            metrics_text = daemon.export_prometheus_metrics()
            response = Response(metrics_text, mimetype='text/plain')
            response.charset = 'utf-8'
            return response
            
        except Exception as e:
            error_text = f"# Error exporting metrics\n# {str(e)}\n"
            response = Response(error_text, status=503, mimetype='text/plain')
            response.charset = 'utf-8'
            return response
    
    return app


def run_server(daemon: 'AutomationDaemon', host: str = '127.0.0.1', port: int = 8080, debug: bool = False):
    """
    Run the HTTP monitoring server.
    
    Args:
        daemon: AutomationDaemon instance to monitor
        host: Host to bind to
        port: Port to listen on
        debug: Enable Flask debug mode
    """
    app = create_app(daemon)
    app.run(host=host, port=port, debug=debug)
