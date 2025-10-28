# YouTube API Trigger System - Project Manifest

**Status**: 🟡 Planning  
**Priority**: P0 - Critical workflow automation  
**Created**: 2025-10-17  
**Epic**: YouTube Processing Automation  
**Related**: `youtube-auto-promotion-integration-manifest.md`, `system-observability-integration-manifest.md`

---

## 🎯 Vision

Transform YouTube note processing from file-watcher-based automation to a **modern API-first architecture** that enables:
- Templater-triggered automatic processing on note creation
- External tool integration (mobile apps, browser extensions, webhooks)
- Real-time dashboard monitoring of processing queue
- Foundation for future API-driven features

**Key Principle**: Build reusable API infrastructure that serves current needs (Templater) while enabling future integrations (mobile, web, automation platforms).

---

## 📊 Current State

### **What Works**
- ✅ YouTube transcript fetching via `youtube-transcript-api`
- ✅ AI quote extraction with Ollama
- ✅ File watcher monitoring `knowledge/Inbox/`
- ✅ HTTP server with `/health` and `/metrics` endpoints
- ✅ YouTubeFeatureHandler with cooldown and caching
- ✅ Dashboard monitoring infrastructure

### **Current Workflow**
```
1. User creates YouTube note with template
2. User adds personal context
3. User saves note
4. File watcher detects change (2s debounce)
5. YouTubeFeatureHandler checks criteria:
   - source: youtube ✓
   - ai_processed: false ✓
6. Cooldown check (60s)
7. Processing begins (transcript → AI quotes → insert)
```

### **Limitations**
- ❌ No explicit user trigger - relies on file saves
- ❌ No way to trigger from external tools (Templater, mobile)
- ❌ No processing queue visibility
- ❌ No API for programmatic control
- ❌ Cooldown can block legitimate user-initiated processing

---

## 🎯 Target State

### **API-First Architecture**
```
Templater Script
    ↓ [HTTP POST]
Custom API (/api/youtube/process)
    ↓ [Triggers]
YouTubeFeatureHandler (existing logic)
    ↓ [Calls]
YouTube Transcript API (Google)
    ↓ [Returns]
AI Processing → Note Enhancement
```

### **New User Workflow**
```
1. Cmd+P → "Template: YouTube"
2. Templater prompts:
   - Paste URL (from clipboard)
   - Video title
   - Why saving this? (personal context)
3. Note created → Templater hook fires automatically
4. Notification: "🎥 Processing YouTube video..."
5. User continues working (non-blocking)
6. Background: API call → Processing → Quotes inserted
7. Notification: "✅ 5 quotes extracted"
8. User reviews enhanced note
```

### **Future Integrations Enabled**
- 📱 Mobile app: Share YouTube video → Auto-creates note
- 🌐 Browser extension: One-click save from YouTube
- 🔗 Zapier/IFTTT: Watch Later → Auto-process
- 📊 Web dashboard: Batch processing interface
- ⚡ Keyboard shortcuts: Cmd+Shift+Y to process current note

---

## 🏗️ Technical Architecture

### **Phase 1: API Endpoint Layer**

**New File**: `development/src/automation/youtube_api.py`

```python
"""YouTube Processing REST API Routes"""

Routes:
  POST /api/youtube/process
    - Trigger processing for specific note
    - Request: {"note_path": "/absolute/path/to/note.md", "force": false}
    - Response: {"success": true, "message": "Processing started", "job_id": "uuid"}
    - Status: 202 Accepted (async processing)
  
  GET /api/youtube/queue
    - Get current processing queue status
    - Response: {"queued": 2, "processing": "note.md", "metrics": {...}}
  
  POST /api/youtube/batch (Future)
    - Batch process multiple notes
    - Request: {"notes": ["path1.md", "path2.md"]}
```

**Integration Point**: Wire into existing `http_server.py` Flask app

### **Phase 2: Daemon HTTP Server Enhancement**

**Modify**: `development/src/automation/daemon.py`

```python
def start(self):
    # Existing startup...
    
    # Start HTTP server in background thread
    if self._config.http_server.enabled:
        from .http_server import create_app
        app = create_app(self)
        
        http_thread = threading.Thread(
            target=lambda: app.run(
                host=self._config.http_server.host,
                port=self._config.http_server.port
            ),
            daemon=True
        )
        http_thread.start()
```

**Config**: `development/daemon_config.yaml`

```yaml
http_server:
  enabled: true
  host: 127.0.0.1
  port: 8080
```

### **Phase 3: Templater Integration**

**New File**: `.obsidian/scripts/trigger_youtube_processing.js`

```javascript
async function triggerYouTubeProcessing(tp) {
    const notePath = tp.file.path(true);
    const apiUrl = 'http://localhost:8080/api/youtube/process';
    
    try {
        new Notice(`🎥 Processing ${tp.file.title}...`);
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({note_path: notePath})
        });
        
        const result = await response.json();
        result.success 
            ? new Notice(`✅ ${result.message}`)
            : new Notice(`❌ ${result.error}`);
    } catch (error) {
        new Notice(`❌ Daemon not running: ${error.message}`);
    }
    
    return '';
}

module.exports = triggerYouTubeProcessing;
```

**Template Update**: YouTube note template

```markdown
---
type: literature
source: youtube
url: <% tp.system.clipboard() %>
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
ai_processed: false
---

# <% tp.system.prompt("Video Title") %>

## Why I'm Saving This
<% tp.system.prompt("What interests you about this video?") %>

<%*
// Automatic API trigger after template creation
await tp.user.trigger_youtube_processing(tp);
%>
```

### **Phase 4: Dashboard Integration**

**Enhance**: `development/src/cli/terminal_dashboard.py`

```python
def create_youtube_queue_table(health_data):
    """Show YouTube processing queue in dashboard"""
    youtube = health_data.get('handlers', {}).get('youtube', {})
    
    table = Table(title="YouTube Processing Queue")
    # Show: Current processing, Queued items, Recent completions
```

---

## 📋 Implementation Phases

### **Phase 1: API Foundation** (2 hours)
**Goal**: Working REST API for YouTube processing

- [ ] Create `youtube_api.py` with routes
  - POST `/api/youtube/process`
  - GET `/api/youtube/queue`
- [ ] Add route registration to `http_server.py`
- [ ] Update daemon config with `http_server` section
- [ ] Enhance daemon startup to run HTTP server
- [ ] Write API endpoint tests
- [ ] Test with `curl` commands

**Success Criteria**:
```bash
curl -X POST http://localhost:8080/api/youtube/process \
  -H "Content-Type: application/json" \
  -d '{"note_path": "/path/to/test.md"}'

# Returns: {"success": true, "message": "Processing started"}
```

### **Phase 2: Templater Integration** (1 hour)
**Goal**: Automatic processing on template creation

- [ ] Create `.obsidian/scripts/trigger_youtube_processing.js`
- [ ] Update YouTube template with Templater hook
- [ ] Test template → API call flow
- [ ] Add error handling for offline daemon
- [ ] Document Templater setup for distribution

**Success Criteria**:
- Create note from template → See "🎥 Processing..." notification
- Note enhanced with quotes within 30 seconds
- Works offline (graceful degradation with notification)

### **Phase 3: Dashboard Enhancement** (1 hour)
**Goal**: Real-time queue visibility

- [ ] Add queue status to YouTube handler
- [ ] Create queue table in terminal dashboard
- [ ] Add processing metrics display
- [ ] Show current/queued/completed counts
- [ ] Real-time updates (1s refresh)

**Success Criteria**:
```
YouTube Processing Queue
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Processing: ai-tutorial.md
⏳ Queued: podcast-notes.md
✅ Recent: 12 videos (93% success)
```

### **Phase 4: Testing & Documentation** (30 min)
**Goal**: Production-ready reliability

- [ ] Integration tests (API → Handler → Processing)
- [ ] Error handling tests (invalid paths, daemon offline)
- [ ] Performance tests (concurrent requests)
- [ ] Update DASHBOARD-README.md
- [ ] Create API-REFERENCE.md
- [ ] Add troubleshooting guide

---

## 🧪 Testing Strategy

### **Unit Tests**
```python
# tests/unit/test_youtube_api.py

def test_process_endpoint_triggers_handler():
    """POST /api/youtube/process calls YouTubeFeatureHandler"""
    
def test_process_endpoint_validates_path():
    """Returns 404 for non-existent notes"""
    
def test_queue_endpoint_returns_metrics():
    """GET /api/youtube/queue shows handler stats"""
```

### **Integration Tests**
```python
# tests/integration/test_youtube_api_integration.py

def test_end_to_end_processing():
    """API call → Handler → Transcript → AI → Note update"""
    
def test_templater_workflow_simulation():
    """Simulates Templater calling API on note creation"""
```

### **Manual Testing Checklist**
- [ ] Create note from template → See processing notification
- [ ] Dashboard shows queued item
- [ ] Dashboard shows processing status
- [ ] Quotes appear in note within 30s
- [ ] `ai_processed: true` set in frontmatter
- [ ] Multiple rapid template creations don't crash
- [ ] Daemon offline → graceful error notification

---

## 📊 Success Criteria

### **Functional**
- ✅ Template creation triggers processing automatically
- ✅ API accepts external processing requests
- ✅ Dashboard shows real-time queue status
- ✅ Processing completes within 30 seconds
- ✅ Graceful error handling when daemon offline

### **Performance**
- ✅ API response time: <100ms (202 Accepted)
- ✅ Processing time: <30s (transcript fetch + AI quotes)
- ✅ Dashboard refresh: 1s interval
- ✅ Support 10+ concurrent template creations

### **User Experience**
- ✅ Zero manual steps after template creation
- ✅ Clear notifications at each stage
- ✅ Non-blocking workflow (async processing)
- ✅ Visible queue status in dashboard
- ✅ Informative error messages

---

## 🔗 Related Files

### **Core Processing** (Already Built)
- `development/src/ai/youtube_transcript_fetcher.py` - Transcript fetching
- `development/src/ai/youtube_quote_extractor.py` - AI quote extraction
- `development/src/automation/feature_handlers.py` - YouTubeFeatureHandler

### **Infrastructure** (Already Built)
- `development/src/automation/daemon.py` - Main daemon orchestrator
- `development/src/automation/http_server.py` - HTTP monitoring server
- `development/src/cli/terminal_dashboard.py` - Live monitoring dashboard

### **New Files** (To Build)
- `development/src/automation/youtube_api.py` - REST API routes
- `.obsidian/scripts/trigger_youtube_processing.js` - Templater hook
- `tests/unit/test_youtube_api.py` - API unit tests
- `Projects/ACTIVE/API-REFERENCE.md` - API documentation

### **Configuration**
- `development/daemon_config.yaml` - Add `http_server` section
- `.obsidian/templates/YouTube.md` - Update with Templater hook

---

## 🚀 Future Enhancements (Post-MVP)

### **Phase 5: Advanced Features** (Future)
- Batch processing endpoint (`/api/youtube/batch`)
- Processing priority queue
- Retry failed processing jobs
- Processing history/analytics
- Webhook callbacks on completion

### **Phase 6: External Integrations** (Future)
- Mobile app (Swift/Kotlin)
- Browser extension (Chrome/Firefox)
- Zapier/IFTTT webhooks
- Alfred workflow
- Raycast extension

### **Phase 7: Enhanced Dashboard** (Future)
- Web-based dashboard (React)
- Processing analytics graphs
- Manual retry buttons
- Bulk operations UI
- Export processing logs

---

## ⚠️ Known Constraints

### **Technical**
- HTTP server must be enabled in daemon config
- Daemon must be running for API access
- Templater requires Obsidian desktop (no mobile)
- CORS limited to localhost (security)

### **Operational**
- API accessible only on localhost (127.0.0.1)
- No authentication (local-only access)
- Single daemon instance per vault
- Processing queue is in-memory (not persistent)

### **Dependencies**
- Templater plugin (Obsidian)
- Daemon with HTTP server enabled
- Flask with CORS support
- Rich library for dashboard

---

## 📝 Decision Log

### **Why REST API vs Direct File Watcher?**
- **Decision**: Build REST API layer
- **Rationale**: 
  - Enables external tool integration (Templater, mobile, web)
  - Explicit user control vs implicit file saves
  - Foundation for future features (webhooks, batch processing)
  - Separates concerns (Obsidian ↔ Processing)
- **Trade-off**: Additional complexity, but high reusability

### **Why Templater Hook vs Manual Trigger?**
- **Decision**: Automatic Templater hook
- **Rationale**:
  - Zero user friction (automatic on template creation)
  - Natural workflow continuation
  - Non-blocking (async processing)
  - Users already provide context during template prompts
- **Trade-off**: Requires Templater setup, but acceptable for power users

### **Why Async Processing (202 Accepted)?**
- **Decision**: API returns immediately, processes in background
- **Rationale**:
  - Non-blocking user experience
  - Template creation completes instantly
  - Users continue working while processing happens
  - Dashboard provides visibility into queue
- **Trade-off**: No immediate feedback on completion, but notifications solve this

---

## 📅 Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: API Foundation | 2 hours | None (uses existing handlers) |
| Phase 2: Templater Integration | 1 hour | Phase 1 complete |
| Phase 3: Dashboard Enhancement | 1 hour | Phase 1 complete |
| Phase 4: Testing & Docs | 30 min | Phases 1-3 complete |
| **Total** | **4.5 hours** | - |

**Recommended Approach**: 
1. Start with Phase 1 (API) - test with `curl` before Templater
2. Verify API works independently
3. Add Templater integration
4. Enhance dashboard last (nice-to-have)

---

## 🎯 Next Actions

1. **Review this manifest** - confirm scope and approach
2. **Create feature branch**: `feat/youtube-api-trigger-system`
3. **Start Phase 1**: Build API endpoint
4. **Test with curl**: Verify API before Templater
5. **Iterate**: Phase 2 → 3 → 4

---

**Last Updated**: 2025-10-17  
**Status**: 🟡 Ready for implementation  
**Owner**: @thaddius  
**Epic**: YouTube Processing Automation
