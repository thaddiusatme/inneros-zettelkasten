#!/usr/bin/env python3
"""
Mock Daemon - Simple HTTP Server for Demo
Runs on port 8080 and responds to /health endpoint
No dependencies required - pure Python!
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

START_TIME = time.time()

class MockDaemonHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            # Calculate uptime
            uptime_seconds = int(time.time() - START_TIME)
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Mock health response
            health_data = {
                "daemon": {
                    "is_healthy": True,
                    "uptime": uptime,
                    "handlers_count": 3
                },
                "handlers": {
                    "screenshot": {
                        "is_healthy": True,
                        "processed_count": 42,
                        "last_activity": "2 minutes ago"
                    },
                    "smart_link": {
                        "is_healthy": True,
                        "processed_count": 15,
                        "last_activity": "5 minutes ago"
                    },
                    "youtube": {
                        "is_healthy": True,
                        "processed_count": 8,
                        "last_activity": "10 minutes ago"
                    }
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    PORT = 8080
    server = HTTPServer(('0.0.0.0', PORT), MockDaemonHandler)
    
    print("🎭 Mock Daemon Starting (Demo Mode)...")
    print(f"🔌 Listening on: http://localhost:{PORT}")
    print(f"💚 Health endpoint: http://localhost:{PORT}/health")
    print("⌨️  Press Ctrl+C to stop")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Mock daemon stopped")
        server.shutdown()
