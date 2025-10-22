# YouTube API Trigger System - Requirements & Implementation Review

**Date**: 2025-10-18  
**Status**: 📋 Planning Review  
**Purpose**: Refine requirements and validate technical approach before implementation  
**Related**: `youtube-api-trigger-system-manifest.md`

---

## 🎯 Executive Summary

**Problem**: YouTube note processing requires manual triggering via file saves. No programmatic API access.

**Solution**: REST API layer that enables:
- Templater to trigger processing on note creation
- Future integrations (mobile, browser extension, webhooks)
- Real-time queue monitoring

**Approach**: Build minimal API layer on top of existing proven processing (Phase 1-3)

**Timeline**: 4.5 hours across 3 focused sessions

---

## 📖 User Stories

### **Epic: YouTube Processing Automation**

#### **US-1: API-Triggered Processing** (P0 - Critical)

**As a** Zettelkasten user  
**I want** YouTube notes to process automatically when I create them from a template  
**So that** I don't have to manually trigger processing or wait for file watcher

**Acceptance Criteria:**
- ✅ POST `/api/youtube/process` endpoint accepts note path
- ✅ API validates note exists and has required frontmatter
- ✅ Returns 202 Accepted with job_id immediately (non-blocking)
- ✅ Processing happens in background using existing YouTubeFeatureHandler
- ✅ Returns 400 Bad Request for invalid/missing notes
- ✅ Returns 409 Conflict if note already processed (ai_processed: true)
- ✅ Respects cooldown period (60s) to prevent loops

**Success Metrics:**
- API response time: <100ms
- Processing completes: <30 seconds
- Success rate: >95% for valid notes

---

#### **US-2: Templater Auto-Trigger** (P0 - Critical)

**As a** Zettelkasten user  
**I want** my YouTube template to automatically call the processing API  
**So that** processing starts immediately without any manual steps

**Acceptance Criteria:**
- ✅ Template creates note with all required frontmatter
- ✅ Templater hook fires automatically after template completes
- ✅ User sees notification: "🎥 Processing {video_title}..."
- ✅ API call happens in background (doesn't block note creation)
- ✅ Graceful error if daemon offline: "⚠️ Daemon offline, process manually"
- ✅ No duplicate processing if template run multiple times

**Success Metrics:**
- Zero manual steps after Cmd+P → Template
- Notification appears within 1 second
- Template completes even if API fails

---

#### **US-3: Queue Visibility** (P1 - Important)

**As a** Zettelkasten user  
**I want** to see what's currently processing  
**So that** I know the system is working and what's queued

**Acceptance Criteria:**
- ✅ GET `/api/youtube/queue` returns current queue status
- ✅ Shows: currently processing note, queued count, recent completions
- ✅ Terminal dashboard displays queue table
- ✅ Dashboard updates in real-time (1s refresh)
- ✅ Shows processing time and estimated completion

**Success Metrics:**
- Queue status updates within 1 second
- Dashboard shows accurate current state
- No performance impact on processing

---

#### **US-4: Error Handling & Recovery** (P1 - Important)

**As a** Zettelkasten user  
**I want** clear error messages when processing fails  
**So that** I can fix issues and retry

**Acceptance Criteria:**
- ✅ API returns descriptive error messages (not stack traces)
- ✅ Templater shows user-friendly notifications on failure
- ✅ Failed jobs logged with full context for debugging
- ✅ Retry mechanism for transient failures (network, rate limits)
- ✅ Cooldown bypassed for manual retry requests

**Success Metrics:**
- All errors have actionable messages
- Retry succeeds for transient failures
- Users can self-service common issues

---

## 🏗️ Technical Architecture (Detailed)

### **Component Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                        Obsidian                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  YouTube         │         │  Templater       │          │
│  │  Template        │────────>│  Hook Script     │          │
│  └──────────────────┘         └──────────────────┘          │
│                                        │                     │
│                                        │ HTTP POST           │
└────────────────────────────────────────┼─────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Automation Daemon (Python)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTTP Server (Flask)                                  │   │
│  │  ┌─────────────────┐     ┌──────────────────┐        │   │
│  │  │  /api/youtube/  │────>│  Processing      │        │   │
│  │  │  process        │     │  Queue           │        │   │
│  │  └─────────────────┘     └──────────────────┘        │   │
│  │           │                       │                   │   │
│  └───────────┼───────────────────────┼───────────────────┘   │
│              │                       │                       │
│              ▼                       ▼                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  YouTubeFeatureHandler                              │    │
│  │  (Existing - Phase 1-3 Proven Working)              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │    │
│  │  │ Transcript   │→│ AI Quote     │→│ Note     │  │    │
│  │  │ Fetcher      │  │ Extractor    │  │ Enhancer │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

### **Phase 1: API Endpoint Layer**

#### **1.1 New File: `src/automation/youtube_api.py`**

**Purpose**: REST API routes for YouTube processing

**Design Decisions:**
- **Framework**: Flask (already used in http_server.py)
- **Response Format**: JSON with consistent structure
- **Status Codes**: RESTful conventions (202, 400, 404, 409, 500)
- **Queue**: In-memory queue (future: Redis for persistence)

**API Contract:**

```python
"""
POST /api/youtube/process
─────────────────────────

Request:
{
    "note_path": "knowledge/Inbox/YouTube/test.md",  # Relative or absolute
    "force": false                                    # Optional: bypass cooldown
}

Response (202 Accepted):
{
    "success": true,
    "message": "Processing started",
    "job_id": "uuid-v4",
    "estimated_seconds": 25
}

Response (400 Bad Request):
{
    "success": false,
    "error": "Note file not found",
    "note_path": "knowledge/Inbox/YouTube/test.md"
}

Response (409 Conflict):
{
    "success": false,
    "error": "Note already processed",
    "details": "ai_processed: true in frontmatter"
}

Response (429 Too Many Requests):
{
    "success": false,
    "error": "Cooldown active",
    "retry_after_seconds": 45,
    "last_processed": "2025-10-18T21:30:00Z"
}

GET /api/youtube/queue
──────────────────────

Response (200 OK):
{
    "success": true,
    "queue": {
        "processing": {
            "note": "lit-20251018-0924-andrej-karpathy.md",
            "started_at": "2025-10-18T21:35:12Z",
            "elapsed_seconds": 12
        },
        "queued": [
            {"note": "lit-20251018-1000-ai-tutorial.md", "position": 1},
            {"note": "lit-20251018-1015-podcast.md", "position": 2}
        ],
        "metrics": {
            "today_processed": 12,
            "today_success": 11,
            "today_failed": 1,
            "average_time_seconds": 24.5
        }
    }
}
```

**Implementation Details:**

```python
# src/automation/youtube_api.py

from flask import Blueprint, request, jsonify
from pathlib import Path
import uuid
from datetime import datetime
import threading
import queue

youtube_api = Blueprint('youtube_api', __name__)

# Processing queue (in-memory for MVP)
processing_queue = queue.Queue()
current_processing = None
metrics = {
    "today_processed": 0,
    "today_success": 0,
    "today_failed": 0,
    "total_time": 0
}

@youtube_api.route('/api/youtube/process', methods=['POST'])
def process_note():
    """
    Trigger YouTube note processing
    
    Validates note, checks cooldown, queues for processing
    Returns immediately (202 Accepted) - async processing
    """
    data = request.get_json()
    
    # Validation
    note_path = data.get('note_path')
    if not note_path:
        return jsonify({
            "success": False,
            "error": "note_path is required"
        }), 400
    
    # Convert to absolute path
    vault_path = get_vault_path()  # From daemon config
    full_path = (vault_path / note_path).resolve()
    
    # Check file exists
    if not full_path.exists():
        return jsonify({
            "success": False,
            "error": "Note file not found",
            "note_path": str(note_path)
        }), 404
    
    # Check already processed (unless force=true)
    if not data.get('force', False):
        if is_already_processed(full_path):
            return jsonify({
                "success": False,
                "error": "Note already processed",
                "details": "ai_processed: true in frontmatter"
            }), 409
        
        # Check cooldown
        cooldown = check_cooldown(full_path)
        if cooldown:
            return jsonify({
                "success": False,
                "error": "Cooldown active",
                "retry_after_seconds": cooldown['seconds'],
                "last_processed": cooldown['timestamp']
            }), 429
    
    # Create job
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "note_path": str(full_path),
        "created_at": datetime.now().isoformat(),
        "force": data.get('force', False)
    }
    
    # Queue for processing
    processing_queue.put(job)
    
    return jsonify({
        "success": True,
        "message": "Processing started",
        "job_id": job_id,
        "estimated_seconds": 25
    }), 202

@youtube_api.route('/api/youtube/queue', methods=['GET'])
def get_queue():
    """Get current processing queue status"""
    
    queued_items = []
    # Peek at queue without removing items
    # (Implementation detail: may need thread-safe queue wrapper)
    
    return jsonify({
        "success": True,
        "queue": {
            "processing": current_processing,
            "queued": queued_items,
            "metrics": metrics
        }
    }), 200

# Helper functions
def get_vault_path():
    """Get vault path from daemon config"""
    # Implementation: Read from daemon instance
    pass

def is_already_processed(note_path):
    """Check if note has ai_processed: true"""
    from src.utils.frontmatter import parse_frontmatter
    content = note_path.read_text()
    frontmatter, _ = parse_frontmatter(content)
    return frontmatter.get('ai_processed') is True

def check_cooldown(note_path):
    """Check if note is in cooldown period"""
    # Implementation: Check YouTubeFeatureHandler._last_processed
    pass
```

**Questions for Review:**
1. ✅ Is 202 Accepted the right status for async processing?
2. ✅ Should we persist queue to disk or keep in-memory for MVP?
3. ✅ Should `force=true` bypass both cooldown AND ai_processed checks?
4. ⚠️ How do we handle concurrent requests to process same note?
5. ⚠️ Should we add rate limiting per note or globally?

---

#### **1.2 Integration with HTTP Server**

**Modify**: `src/automation/http_server.py`

**Current State**: Has `/health` and `/metrics` endpoints

**Changes Needed:**

```python
# src/automation/http_server.py

def create_app(daemon):
    """Create Flask app with all routes"""
    app = Flask(__name__)
    CORS(app)  # Allow Obsidian (localhost) access
    
    # Existing routes
    @app.route('/health')
    def health():
        # ... existing code ...
    
    @app.route('/metrics')
    def metrics():
        # ... existing code ...
    
    # NEW: Register YouTube API blueprint
    from .youtube_api import youtube_api, init_youtube_api
    init_youtube_api(daemon)  # Pass daemon reference for handler access
    app.register_blueprint(youtube_api)
    
    return app
```

**Questions for Review:**
1. ✅ Should API routes be in blueprint or directly in http_server.py?
2. ⚠️ How do we pass daemon/handler reference to API cleanly?
3. ⚠️ Do we need authentication for localhost API?

---

#### **1.3 Processing Queue Worker**

**Purpose**: Background thread that processes queued jobs

**Design:**

```python
# In src/automation/youtube_api.py or separate worker.py

class ProcessingWorker:
    """Background worker that processes YouTube notes from queue"""
    
    def __init__(self, youtube_handler):
        self.handler = youtube_handler
        self.queue = processing_queue  # Reference to global queue
        self.running = False
        self.thread = None
    
    def start(self):
        """Start background worker thread"""
        self.running = True
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop worker gracefully"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _worker_loop(self):
        """Main worker loop - processes jobs from queue"""
        global current_processing
        
        while self.running:
            try:
                # Get next job (blocks with timeout)
                job = self.queue.get(timeout=1)
                
                current_processing = {
                    "note": Path(job['note_path']).name,
                    "started_at": datetime.now().isoformat(),
                    "elapsed_seconds": 0
                }
                
                # Process using existing handler
                class MockEvent:
                    def __init__(self, path):
                        self.src_path = str(path)
                
                event = MockEvent(job['note_path'])
                result = self.handler.handle(event)
                
                # Update metrics
                if result.get('success'):
                    metrics['today_success'] += 1
                else:
                    metrics['today_failed'] += 1
                
                metrics['today_processed'] += 1
                
                current_processing = None
                self.queue.task_done()
                
            except queue.Empty:
                continue  # No jobs, keep waiting
            except Exception as e:
                # Log error, mark job failed
                metrics['today_failed'] += 1
                current_processing = None
```

**Questions for Review:**
1. ⚠️ Should worker be in same file as API or separate `worker.py`?
2. ✅ Should queue size be limited (backpressure)?
3. ⚠️ How do we handle daemon restart (queue persistence)?
4. ⚠️ Should we support multiple worker threads for concurrency?

---

### **Phase 2: Templater Integration**

#### **2.1 Templater Hook Script**

**New File**: `.obsidian/scripts/trigger_youtube_processing.js`

**Purpose**: Called by Templater after note creation to trigger API

**Implementation:**

```javascript
/**
 * Trigger YouTube Processing - Templater Hook
 * 
 * Automatically called after YouTube template completes
 * Sends API request to local daemon to start processing
 * 
 * Usage in template:
 *   <%* await tp.user.trigger_youtube_processing(tp); %>
 */

async function trigger_youtube_processing(tp) {
    const API_URL = 'http://localhost:8080/api/youtube/process';
    const notePath = tp.file.path(true); // Get absolute path
    const noteTitle = tp.file.title;
    
    try {
        // Show processing notification
        new Notice(`🎥 Processing: ${noteTitle}`, 3000);
        
        // Call API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                note_path: notePath,
                force: false
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            new Notice(`✅ Processing started (${result.estimated_seconds}s)`, 2000);
        } else {
            // Show user-friendly error
            if (response.status === 409) {
                new Notice(`ℹ️ Already processed`, 2000);
            } else if (response.status === 429) {
                new Notice(`⏳ Cooldown active (${result.retry_after_seconds}s)`, 3000);
            } else {
                new Notice(`⚠️ ${result.error}`, 5000);
            }
        }
        
    } catch (error) {
        // Daemon offline or network error
        console.error('YouTube processing API error:', error);
        new Notice(
            `⚠️ Daemon offline. Process manually:\n` +
            `cd development && python3 src/cli/youtube_cli.py process-note "${notePath}"`,
            10000
        );
    }
    
    // Return empty string (Templater requirement)
    return '';
}

module.exports = trigger_youtube_processing;
```

**Questions for Review:**
1. ✅ Should we show different notifications for different error types?
2. ⚠️ Should we retry on network error or fail immediately?
3. ✅ Should manual CLI command be shown in notification or separate doc?
4. ⚠️ How do we handle Obsidian mobile (no localhost)?

---

#### **2.2 Updated YouTube Template**

**Modify**: `knowledge/Templates/youtube-video.md` (or `.obsidian/templates/`)

**Key Changes:**

```markdown
<%*
// ... existing template logic (fetch metadata, build frontmatter) ...

// ──────────────────────────────────────────────────────
// NEW: Automatic API Trigger
// ──────────────────────────────────────────────────────
// Call processing API after template completes
// This triggers transcript fetch + AI quote extraction
await tp.user.trigger_youtube_processing(tp);
%>
```

**Questions for Review:**
1. ✅ Should API call be optional (user config)?
2. ⚠️ Should we add delay before API call (let user review note first)?
3. ✅ Should template still work if Templater script missing?

---

### **Phase 3: Dashboard Enhancement**

#### **3.1 Queue Display in Terminal Dashboard**

**Modify**: `src/cli/terminal_dashboard.py`

**Add YouTube Queue Table:**

```python
def create_youtube_queue_panel(health_data):
    """Create YouTube processing queue display panel"""
    from rich.table import Table
    from rich.panel import Panel
    
    youtube = health_data.get('handlers', {}).get('youtube', {})
    queue = youtube.get('queue', {})
    
    # Create table
    table = Table(title="YouTube Processing Queue", show_header=True)
    table.add_column("Status", style="cyan")
    table.add_column("Note", style="white")
    table.add_column("Time", style="yellow")
    
    # Currently processing
    if queue.get('processing'):
        proc = queue['processing']
        elapsed = calculate_elapsed(proc['started_at'])
        table.add_row(
            "🔄 Processing",
            proc['note'],
            f"{elapsed}s"
        )
    
    # Queued items
    for item in queue.get('queued', []):
        table.add_row(
            f"⏳ Queued #{item['position']}",
            item['note'],
            "waiting"
        )
    
    # Metrics
    metrics = queue.get('metrics', {})
    table.add_row(
        "✅ Today",
        f"{metrics.get('today_success', 0)} success / {metrics.get('today_failed', 0)} failed",
        f"avg {metrics.get('average_time_seconds', 0):.1f}s"
    )
    
    return Panel(table, title="YouTube Processing", border_style="blue")
```

**Questions for Review:**
1. ✅ Should queue panel be always visible or toggle-able?
2. ⚠️ Should we show last N completed items (history)?
3. ⚠️ Should we add progress bar for current processing?

---

## 🚨 Risks & Constraints

### **Technical Risks**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Queue lost on daemon restart | High | Medium | Accept for MVP, document persistence as Phase 5 |
| Concurrent processing same note | Medium | Low | Add file lock or job deduplication |
| API port already in use | Low | High | Make port configurable, check on startup |
| Templater script doesn't load | Low | Medium | Document setup, provide diagnostics |
| Network timeout in Templater | Medium | Low | Show clear error, provide manual command |

### **User Experience Risks**

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| User doesn't know daemon must run | High | High | Clear documentation, health check endpoint |
| Notification overload (many templates) | Medium | Medium | Batch notifications, cooldown warnings |
| User expects immediate results | Medium | Low | Clear "Processing..." → "Complete" notifications |
| Template works but no processing | Medium | High | Graceful degradation, show manual command |

### **Operational Constraints**

- **Daemon Must Be Running**: API unavailable if daemon offline
- **Local-Only Access**: No remote/mobile access (localhost:8080 only)
- **Single Vault**: One daemon instance per vault
- **Templater Desktop Only**: No mobile template auto-trigger
- **In-Memory Queue**: Lost on restart (acceptable for MVP)

---

## ✅ Testable Success Criteria

### **Phase 1: API Foundation**

```bash
# Test 1: API endpoint exists
curl http://localhost:8080/api/youtube/process
# Expected: 400 Bad Request (missing note_path)

# Test 2: Valid request queues processing
curl -X POST http://localhost:8080/api/youtube/process \
  -H "Content-Type: application/json" \
  -d '{"note_path": "knowledge/Inbox/YouTube/test.md"}'
# Expected: 202 Accepted with job_id

# Test 3: Already processed detection
curl -X POST http://localhost:8080/api/youtube/process \
  -H "Content-Type: application/json" \
  -d '{"note_path": "knowledge/Inbox/YouTube/processed-note.md"}'
# Expected: 409 Conflict

# Test 4: Queue status
curl http://localhost:8080/api/youtube/queue
# Expected: 200 OK with queue status

# Test 5: File not found
curl -X POST http://localhost:8080/api/youtube/process \
  -H "Content-Type: application/json" \
  -d '{"note_path": "nonexistent.md"}'
# Expected: 404 Not Found
```

### **Phase 2: Templater Integration**

1. ✅ Create note from YouTube template
2. ✅ See "🎥 Processing..." notification within 1 second
3. ✅ API receives POST request (check daemon logs)
4. ✅ Processing completes within 30 seconds
5. ✅ Note has quotes and transcript link
6. ✅ `ai_processed: true` in frontmatter
7. ✅ Graceful error if daemon offline

### **Phase 3: Dashboard**

1. ✅ Dashboard shows "Processing: test.md"
2. ✅ Dashboard shows queued count
3. ✅ Dashboard updates within 1 second
4. ✅ Metrics show today's successes/failures
5. ✅ Dashboard doesn't freeze during processing

---

## 🎯 Implementation Checklist

### **Before Starting**
- [ ] Review this requirements doc with team
- [ ] Validate user stories cover all use cases
- [ ] Confirm technical approach is sound
- [ ] Identify any missing requirements
- [ ] Get sign-off to proceed

### **Phase 1 Prep**
- [ ] Create feature branch: `feat/youtube-api-trigger-system`
- [ ] Set up test fixtures (sample YouTube notes)
- [ ] Verify existing http_server.py works
- [ ] Document API contract (OpenAPI spec?)

### **Phase 2 Prep**
- [ ] Test Templater custom scripts work
- [ ] Verify fetch() available in Templater context
- [ ] Document Templater setup steps

### **Phase 3 Prep**
- [ ] Review terminal_dashboard.py current structure
- [ ] Design queue panel layout (mockup?)

---

## 📝 Open Questions for Review

### **Architecture**
1. Should processing queue be persistent (Redis) or in-memory acceptable for MVP?
2. Should we support multiple worker threads or single-threaded queue?
3. Should API be separate Blueprint or integrated into http_server.py?

### **User Experience**
4. Should Templater hook be automatic or require user opt-in?
5. Should we add delay between template completion and API call?
6. How should we handle notification spam if user creates many notes quickly?

### **Error Handling**
7. Should force=true bypass both cooldown AND ai_processed checks?
8. Should we retry transient failures automatically or require manual retry?
9. How do we communicate queue position to user?

### **Testing**
10. Should we mock YouTubeFeatureHandler for API tests or use real handler?
11. Should we test Templater integration programmatically or manually?
12. What's acceptable test coverage target? (80%?)

### **Documentation**
13. Should we create OpenAPI spec for API or keep it in markdown?
14. Should API docs be separate file or integrated into manifest?
15. What troubleshooting scenarios should we document?

---

## 🚀 Next Steps

1. **Review Meeting**: Walk through this doc, answer open questions
2. **Refine**: Update based on feedback
3. **Sign-Off**: Confirm approach before coding
4. **TDD Session 1**: Build API endpoint (Phase 1)
5. **Iterate**: Phase 2 → 3 → 4

---

**Status**: 📋 Ready for Review  
**Reviewer**: @thaddius  
**Next**: Technical review meeting
