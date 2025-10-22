"""
YouTube API Blueprint - TDD REFACTOR PHASE

REST API endpoints for triggering YouTube note processing.
Production-ready implementation with proper error handling and logging.

Architecture:
- Flask Blueprint with /process and /queue endpoints
- In-memory queue for MVP (no persistence)
- Background thread worker for async processing
- Thread-safe queue management
- Helper functions for validation and error handling

Endpoints:
- POST /api/youtube/process - Trigger note processing
- GET /api/youtube/queue - Get queue status
"""

from flask import Blueprint, request, jsonify
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Dict, Any, Tuple
import time
import uuid
import threading
import queue
import logging

if TYPE_CHECKING:
    from .feature_handlers import YouTubeFeatureHandler


# Configure logging
logger = logging.getLogger(__name__)

# Global queue and processing state (in-memory for MVP)
processing_queue = queue.Queue()
current_job: Optional[Dict[str, Any]] = None
job_results: Dict[str, Dict[str, Any]] = {}  # job_id -> result
processing_lock = threading.Lock()


# ============================================================================
# Validation Helper Functions
# ============================================================================

def validate_note_file(note_path: Path) -> Optional[Tuple[Dict, str]]:
    """
    Validate that note file exists and return error response if invalid.
    
    Args:
        note_path: Path to note file
        
    Returns:
        Tuple of (error_dict, status_code) if invalid, None if valid
    """
    if not note_path.exists():
        return ({
            'error': 'not_found',
            'message': f'Note file does not exist: {note_path}'
        }, 404)
    return None


def validate_video_id(frontmatter: Dict[str, Any]) -> Optional[Tuple[Dict, str]]:
    """
    Validate that video_id exists in frontmatter.
    
    Args:
        frontmatter: Parsed note frontmatter
        
    Returns:
        Tuple of (error_dict, status_code) if invalid, None if valid
    """
    video_id = frontmatter.get('video_id')
    if not video_id or video_id.strip() == '':
        return ({
            'error': 'invalid_request',
            'message': 'Note missing required field: video_id'
        }, 400)
    return None


def check_already_processed(frontmatter: Dict[str, Any], force: bool) -> Optional[Tuple[Dict, str]]:
    """
    Check if note has already been processed.
    
    Args:
        frontmatter: Parsed note frontmatter
        force: If True, skip this check
        
    Returns:
        Tuple of (error_dict, status_code) if already processed, None otherwise
    """
    if not force and frontmatter.get('ai_processed'):
        ai_processed_at = frontmatter.get('ai_processed_at', 'unknown')
        return ({
            'error': 'already_processed',
            'message': f'Note already processed at {ai_processed_at}',
            'ai_processed_at': ai_processed_at
        }, 409)
    return None


def check_cooldown(note_path: Path, handler: 'YouTubeFeatureHandler', force: bool) -> Optional[Tuple[Dict, str]]:
    """
    Check if note is within cooldown period.
    
    Args:
        note_path: Path to note file
        handler: YouTubeFeatureHandler with cooldown settings
        force: If True, skip this check
        
    Returns:
        Tuple of (error_dict, status_code) if cooldown active, None otherwise
    """
    if not force:
        note_str = str(note_path)
        last_time = handler._last_processed.get(note_str, 0)
        cooldown = handler.cooldown_seconds
        elapsed = time.time() - last_time
        
        if elapsed < cooldown:
            retry_after = int(cooldown - elapsed)
            return ({
                'error': 'cooldown_active',
                'message': f'Note processed recently. Wait {retry_after} seconds.',
                'retry_after': retry_after
            }, 429)
    return None


def create_youtube_blueprint(handler: 'YouTubeFeatureHandler') -> Blueprint:
    """
    Create Flask Blueprint for YouTube API endpoints.
    
    Args:
        handler: YouTubeFeatureHandler instance for processing
        
    Returns:
        Configured Flask Blueprint
    """
    bp = Blueprint('youtube_api', __name__)
    
    # Start background worker thread
    worker_thread = threading.Thread(
        target=_process_queue_worker,
        args=(handler,),
        daemon=True
    )
    worker_thread.start()
    
    @bp.route('/process', methods=['POST'])
    def process_note():
        """
        POST /api/youtube/process
        
        Request body:
        {
            "note_path": "/path/to/note.md",
            "force": false  # optional
        }
        
        Returns:
            202: Accepted for processing
            400: Invalid request
            404: Note not found
            409: Already processed (without force=true)
            429: Cooldown active (without force=true)
        """
        # Parse JSON request
        if not request.is_json:
            logger.warning("Received non-JSON request")
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        
        # Validate note_path field
        if 'note_path' not in data:
            logger.warning("Request missing note_path field")
            return jsonify({
                'error': 'invalid_request',
                'message': 'Missing required field: note_path'
            }), 400
        
        note_path = Path(data['note_path'])
        force = data.get('force', False)
        
        logger.info(f"Processing request for note: {note_path} (force={force})")
        
        # Run validation checks
        if error := validate_note_file(note_path):
            logger.warning(f"Note file not found: {note_path}")
            return jsonify(error[0]), error[1]
        
        # Read frontmatter and run additional validations
        try:
            content = note_path.read_text(encoding='utf-8')
            from src.utils.frontmatter import parse_frontmatter
            frontmatter, _ = parse_frontmatter(content)
            
            # Run all validation checks
            for validator in [
                lambda: validate_video_id(frontmatter),
                lambda: check_already_processed(frontmatter, force),
                lambda: check_cooldown(note_path, handler, force)
            ]:
                if error := validator():
                    logger.info(f"Validation failed: {error[0].get('error')}")
                    return jsonify(error[0]), error[1]
        
        except Exception as e:
            logger.error(f"Error reading note {note_path}: {e}")
            return jsonify({
                'error': 'invalid_request',
                'message': f'Error reading note: {str(e)}'
            }), 400
        
        # Create job and add to queue
        job_id = str(uuid.uuid4())
        job = {
            'job_id': job_id,
            'note_path': str(note_path),
            'force': force,
            'queued_at': time.time()
        }
        
        processing_queue.put(job)
        logger.info(f"Job {job_id} queued for processing: {note_path}")
        
        return jsonify({
            'status': 'accepted',
            'job_id': job_id,
            'message': 'Processing started',
            'note_path': str(note_path)
        }), 202
    
    @bp.route('/queue', methods=['GET'])
    def get_queue_status():
        """
        GET /api/youtube/queue
        
        Returns:
            200: Queue status
        """
        with processing_lock:
            # Get currently processing job
            processing_info = None
            if current_job:
                elapsed = time.time() - current_job.get('started_at', time.time())
                processing_info = {
                    'note_path': current_job.get('note_path'),
                    'started_at': time.strftime('%Y-%m-%dT%H:%M:%S', 
                                                time.localtime(current_job.get('started_at', time.time()))),
                    'elapsed_seconds': round(elapsed, 1)
                }
            
            # Get queued jobs
            queued_items = []
            # Note: queue.Queue doesn't allow direct iteration, 
            # so this is a simplified representation
            queue_size = processing_queue.qsize()
            
            return jsonify({
                'queue_size': queue_size,
                'processing': processing_info,
                'queued': queued_items  # Simplified for MVP
            }), 200
    
    return bp


def _process_queue_worker(handler: 'YouTubeFeatureHandler'):
    """
    Background worker thread that processes jobs from the queue.
    
    Args:
        handler: YouTubeFeatureHandler for processing notes
        
    Notes:
        Runs in background daemon thread, processing jobs until process exits.
        Logs all processing attempts, successes, and failures.
    """
    global current_job
    
    logger.info("Queue worker thread started")
    
    while True:
        try:
            # Get next job from queue (blocking with timeout)
            job = processing_queue.get(timeout=1.0)
            job_id = job['job_id']
            note_path = Path(job['note_path'])
            
            logger.info(f"Starting job {job_id}: {note_path}")
            
            with processing_lock:
                current_job = job
                current_job['started_at'] = time.time()
            
            # Create a mock event object for handler
            from unittest.mock import Mock
            event = Mock()
            event.src_path = str(note_path)
            
            # Process the note
            result = handler.handle(event)
            
            processing_time = time.time() - current_job['started_at']
            
            # Store result
            job_results[job_id] = {
                'completed_at': time.time(),
                'result': result
            }
            
            if result.get('success'):
                logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s: "
                           f"{result.get('quotes_added', 0)} quotes added")
            else:
                logger.error(f"Job {job_id} failed after {processing_time:.2f}s: "
                            f"{result.get('error', 'Unknown error')}")
            
            # Clear current job
            with processing_lock:
                current_job = None
            
            processing_queue.task_done()
            
        except queue.Empty:
            # No jobs in queue, continue waiting
            continue
        except Exception as e:
            # Log error and continue processing other jobs
            logger.exception(f"Unexpected error in queue worker: {e}")
            with processing_lock:
                current_job = None
