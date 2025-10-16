"""
Web Metrics Utilities for Flask Dashboard Integration
Phase 3.2 REFACTOR - Extracted utility classes for production-ready architecture
"""

from datetime import datetime
from typing import Dict, Any, Optional
from flask import jsonify


class WebMetricsFormatter:
    """Formats metrics data for web dashboard display.
    
    Handles JSON response formatting, CORS headers, and graceful fallback.
    """
    
    def __init__(self, enable_cors: bool = True):
        """Initialize formatter.
        
        Args:
            enable_cors: Whether to add CORS headers for local development
        """
        self.enable_cors = enable_cors
    
    def format_metrics_response(self, metrics_data: Dict[str, Any]):
        """Format metrics data as Flask JSON response with CORS headers.
        
        Args:
            metrics_data: Metrics data from MetricsEndpoint.get_metrics()
            
        Returns:
            Flask response object with JSON data and headers
        """
        response = jsonify(metrics_data)
        
        if self.enable_cors:
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
    
    def format_fallback_response(self, error: Optional[Exception] = None) -> Dict[str, Any]:
        """Create fallback response when metrics unavailable.
        
        Args:
            error: Optional exception that triggered fallback
            
        Returns:
            Dictionary with empty metrics structure
        """
        fallback = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'current': {
                'counters': {},
                'gauges': {},
                'histograms': {}
            },
            'history': []
        }
        
        # Optionally include error info in development mode
        if error:
            fallback['_debug_error'] = str(error)
        
        return fallback


class MetricsCoordinatorIntegration:
    """Integrates WorkflowMetricsCoordinator with web metrics endpoint.
    
    Provides bridge between daemon metrics and web dashboard.
    """
    
    def __init__(self, metrics_endpoint):
        """Initialize coordinator integration.
        
        Args:
            metrics_endpoint: MetricsEndpoint instance
        """
        self.metrics_endpoint = metrics_endpoint
        self.workflow_coordinator = None
    
    def set_workflow_coordinator(self, coordinator):
        """Set WorkflowMetricsCoordinator for daemon integration.
        
        Args:
            coordinator: WorkflowMetricsCoordinator instance
        """
        self.workflow_coordinator = coordinator
    
    def get_combined_metrics(self) -> Dict[str, Any]:
        """Get metrics from both endpoint and coordinator if available.
        
        Returns:
            Dictionary with combined metrics from all sources
        """
        # Get base metrics from endpoint
        metrics = self.metrics_endpoint.get_metrics()
        
        # Add coordinator metrics if available
        if self.workflow_coordinator:
            try:
                coordinator_metrics = self.workflow_coordinator.get_metrics()
                # Merge coordinator metrics into current section
                for metric_type in ['counters', 'gauges', 'histograms']:
                    if metric_type in coordinator_metrics:
                        metrics['current'][metric_type].update(
                            coordinator_metrics[metric_type]
                        )
            except Exception:
                # Graceful degradation if coordinator fails
                pass
        
        return metrics


class WebMetricsErrorHandler:
    """Handles errors in metrics endpoint gracefully.
    
    Provides logging and fallback for production reliability.
    """
    
    def __init__(self, logger=None):
        """Initialize error handler.
        
        Args:
            logger: Optional logger instance for error reporting
        """
        self.logger = logger
        self.error_count = 0
        self.last_error = None
    
    def handle_metrics_error(self, error: Exception, context: str = "metrics_endpoint"):
        """Handle metrics retrieval error.
        
        Args:
            error: Exception that occurred
            context: Context string for logging
            
        Returns:
            None (logs error and updates stats)
        """
        self.error_count += 1
        self.last_error = {
            'error': str(error),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.logger:
            self.logger.warning(f"Metrics error in {context}: {error}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring.
        
        Returns:
            Dictionary with error count and last error info
        """
        return {
            'error_count': self.error_count,
            'last_error': self.last_error
        }
