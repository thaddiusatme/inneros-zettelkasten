"""
TDD RED PHASE: YouTube API Endpoint Tests

These tests define the expected behavior of the YouTube API trigger system.
All tests should FAIL initially - we haven't implemented the API yet.

Test Coverage:
- POST /api/youtube/process with valid note path → 202 Accepted
- POST with invalid file path → 404 Not Found
- POST with already-processed note → 409 Conflict
- POST with missing video_id → 400 Bad Request
- POST with cooldown active → 429 Too Many Requests
- GET /api/youtube/queue → 200 with queue status
- Force flag bypasses cooldown and ai_processed flag
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Import will fail initially - that's expected for RED phase
try:
    from src.automation.youtube_api import create_youtube_blueprint
except ImportError:
    create_youtube_blueprint = None


@pytest.fixture
def temp_note():
    """Create temporary note file with valid frontmatter."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""---
video_id: dQw4w9WgXcQ
video_title: Test Video
created: 2025-10-18
type: youtube
---

# Test Video

My notes here.
""")
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_processed_note():
    """Create temporary note that's already been processed."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""---
video_id: dQw4w9WgXcQ
video_title: Test Video
created: 2025-10-18
type: youtube
ai_processed: true
ai_processed_at: 2025-10-18T10:00:00
---

# Test Video

My notes here.

## AI-Generated Quotes
- Quote 1
- Quote 2
""")
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def mock_handler():
    """Mock YouTubeFeatureHandler for testing."""
    handler = Mock()
    handler.handle = Mock(return_value={
        'success': True,
        'quotes_added': 3,
        'processing_time': 2.5
    })
    handler.cooldown_seconds = 60
    handler.last_processed_time = {}
    return handler


@pytest.fixture
def app(mock_handler):
    """Create Flask app with YouTube API blueprint."""
    if create_youtube_blueprint is None:
        pytest.skip("youtube_api module not yet implemented")
    
    flask_app = Flask(__name__)
    blueprint = create_youtube_blueprint(mock_handler)
    flask_app.register_blueprint(blueprint, url_prefix='/api/youtube')
    flask_app.config['TESTING'] = True
    
    return flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestYouTubeAPIEndpoints:
    """Test YouTube API REST endpoints."""
    
    def test_post_process_valid_note_returns_202(self, client, temp_note):
        """
        RED TEST: POST valid note path should return 202 Accepted with job_id.
        
        Expected response:
        {
            "status": "accepted",
            "job_id": "uuid-string",
            "message": "Processing started",
            "note_path": "/path/to/note.md"
        }
        """
        response = client.post(
            '/api/youtube/process',
            data=json.dumps({'note_path': str(temp_note)}),
            content_type='application/json'
        )
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['status'] == 'accepted'
        assert 'job_id' in data
        assert 'message' in data
        assert data['note_path'] == str(temp_note)
    
    def test_post_process_invalid_path_returns_404(self, client):
        """
        RED TEST: POST non-existent file should return 404 Not Found.
        
        Expected response:
        {
            "error": "not_found",
            "message": "Note file does not exist: /fake/path.md"
        }
        """
        response = client.post(
            '/api/youtube/process',
            data=json.dumps({'note_path': '/fake/nonexistent.md'}),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'not_found'
        assert 'message' in data
        assert '/fake/nonexistent.md' in data['message']
    
    def test_post_process_already_processed_returns_409(self, client, temp_processed_note):
        """
        RED TEST: POST already-processed note should return 409 Conflict.
        
        Expected response:
        {
            "error": "already_processed",
            "message": "Note already processed at 2025-10-18T10:00:00",
            "ai_processed_at": "2025-10-18T10:00:00"
        }
        """
        response = client.post(
            '/api/youtube/process',
            data=json.dumps({'note_path': str(temp_processed_note)}),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error'] == 'already_processed'
        assert 'ai_processed_at' in data
    
    def test_post_process_missing_video_id_returns_400(self, client):
        """
        RED TEST: POST note without video_id should return 400 Bad Request.
        
        Expected response:
        {
            "error": "invalid_request",
            "message": "Note missing required field: video_id"
        }
        """
        # Create temp note without video_id
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
created: 2025-10-18
type: youtube
---

# No Video ID
""")
            temp_path = Path(f.name)
        
        try:
            response = client.post(
                '/api/youtube/process',
                data=json.dumps({'note_path': str(temp_path)}),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'invalid_request'
            assert 'video_id' in data['message']
        finally:
            temp_path.unlink()
    
    def test_post_process_cooldown_active_returns_429(self, client, temp_note, mock_handler):
        """
        RED TEST: POST during cooldown period should return 429 Too Many Requests.
        
        Expected response:
        {
            "error": "cooldown_active",
            "message": "Note processed recently. Wait 45 seconds.",
            "retry_after": 45
        }
        """
        # Simulate recent processing
        import time
        mock_handler.last_processed_time[str(temp_note)] = time.time() - 15  # 15 seconds ago
        
        response = client.post(
            '/api/youtube/process',
            data=json.dumps({'note_path': str(temp_note)}),
            content_type='application/json'
        )
        
        assert response.status_code == 429
        data = json.loads(response.data)
        assert data['error'] == 'cooldown_active'
        assert 'retry_after' in data
        assert data['retry_after'] > 0
    
    def test_post_process_force_flag_bypasses_checks(self, client, temp_processed_note, mock_handler):
        """
        RED TEST: POST with force=true should bypass cooldown and ai_processed checks.
        
        Expected: 202 Accepted even though note is already processed.
        """
        import time
        mock_handler.last_processed_time[str(temp_processed_note)] = time.time()
        
        response = client.post(
            '/api/youtube/process',
            data=json.dumps({
                'note_path': str(temp_processed_note),
                'force': True
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert data['status'] == 'accepted'
    
    def test_get_queue_returns_status(self, client):
        """
        RED TEST: GET /api/youtube/queue should return queue status.
        
        Expected response:
        {
            "queue_size": 2,
            "processing": {
                "note_path": "/path/to/current.md",
                "started_at": "2025-10-18T10:30:00",
                "elapsed_seconds": 5.2
            },
            "queued": [
                {"note_path": "/path/to/note1.md", "position": 1},
                {"note_path": "/path/to/note2.md", "position": 2}
            ]
        }
        """
        response = client.get('/api/youtube/queue')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'queue_size' in data
        assert 'processing' in data or data['processing'] is None
        assert 'queued' in data
    
    def test_post_process_missing_note_path_returns_400(self, client):
        """
        RED TEST: POST without note_path should return 400 Bad Request.
        
        Expected response:
        {
            "error": "invalid_request",
            "message": "Missing required field: note_path"
        }
        """
        response = client.post(
            '/api/youtube/process',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'invalid_request'
        assert 'note_path' in data['message']
    
    def test_post_process_invalid_json_returns_400(self, client):
        """
        RED TEST: POST with invalid JSON should return 400 Bad Request.
        """
        response = client.post(
            '/api/youtube/process',
            data='invalid json{',
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestYouTubeAPIQueueWorker:
    """Test background queue processing worker."""
    
    def test_queue_processes_jobs_in_order(self, mock_handler):
        """
        RED TEST: Queue worker should process jobs in FIFO order.
        """
        # This will be implemented when we create the queue worker
        pytest.skip("Queue worker not yet implemented")
    
    def test_queue_updates_metrics_on_success(self, mock_handler):
        """
        RED TEST: Successful processing should update metrics.
        """
        pytest.skip("Queue worker not yet implemented")
    
    def test_queue_handles_processing_errors(self, mock_handler):
        """
        RED TEST: Queue worker should handle processing errors gracefully.
        """
        pytest.skip("Queue worker not yet implemented")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
