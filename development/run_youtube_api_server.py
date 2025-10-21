#!/usr/bin/env python3
"""
Standalone YouTube API Server - For Testing Templater Integration

Runs just the YouTube API endpoints without the full daemon.
Perfect for testing the Templater hook script.

Usage:
    python3 development/run_youtube_api_server.py
    
Then test in Obsidian with the YouTube template.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from flask import Flask
from automation.youtube_api import create_youtube_blueprint
from automation.feature_handlers import YouTubeFeatureHandler

def main():
    """Run standalone YouTube API server."""
    
    # Get vault path (repo root)
    vault_path = Path(__file__).parent.parent
    
    print("🚀 Starting Standalone YouTube API Server...")
    print(f"📁 Vault: {vault_path}")
    
    # Create YouTubeFeatureHandler
    try:
        config = {
            'vault_path': str(vault_path),
            'max_quotes': 5,
            'min_quality': 0.5,
            'processing_timeout': 120,
            'cooldown_seconds': 300
        }
        handler = YouTubeFeatureHandler(config=config)
        print("✅ YouTube handler initialized")
    except Exception as e:
        print(f"❌ Failed to initialize handler: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Create Flask app
    app = Flask(__name__)
    
    # Enable CORS for Obsidian
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Register YouTube API blueprint
    youtube_bp = create_youtube_blueprint(handler)
    app.register_blueprint(youtube_bp, url_prefix='/api/youtube')
    
    # Add health endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'youtube_api'}, 200
    
    # Add root endpoint
    @app.route('/')
    def root():
        return {
            'name': 'YouTube API Server',
            'version': '1.0.0',
            'endpoints': {
                '/health': 'Server health check',
                '/api/youtube/process': 'POST - Trigger YouTube note processing',
                '/api/youtube/queue': 'GET - Check processing queue status'
            }
        }, 200
    
    print("✅ YouTube API registered at /api/youtube")
    print("🌐 Server starting on http://localhost:8080")
    print("💡 Press Ctrl+C to stop\n")
    print("📋 Available endpoints:")
    print("   GET  http://localhost:8080/health")
    print("   POST http://localhost:8080/api/youtube/process")
    print("   GET  http://localhost:8080/api/youtube/queue")
    print()
    
    # Run server
    try:
        app.run(host='localhost', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
