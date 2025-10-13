---
description: Complete 4-phase feature development ensuring automation and monitoring from day 1
---

# Complete Feature Development: 4-Phase Methodology

> **Purpose**: Systematic approach ensuring ALL features include Engine, CLI, Automation, AND Monitoring  
> **Enforcement**: MANDATORY for all new feature development  
> **Updated**: 2025-10-06 (Added Phase 3 & 4 requirements)

---

## 🎯 Core Philosophy

**Building "features" without automation is building incomplete workflows.**

Every feature MUST progress through all 4 phases to be considered production-ready:
1. **Phase 1**: Core Engine (AI/processing logic)
2. **Phase 2**: CLI Integration (manual trigger interface)
3. **Phase 3**: Automation Layer (event-driven or scheduled execution) **← NEW REQUIREMENT**
4. **Phase 4**: Monitoring & Alerts (performance tracking, error handling) **← NEW REQUIREMENT**

---

## 📋 4-Phase Definition of Done

### ✅ Phase 1: Core Engine (AI/Processing Logic)

**Requirements**:
- [ ] TDD with RED → GREEN → REFACTOR cycle
- [ ] Core functionality implemented and tested
- [ ] Integration with existing AI infrastructure (WorkflowManager, etc.)
- [ ] Performance benchmarks met
- [ ] Architectural constraints maintained (<500 LOC, <20 methods per class)

**Deliverables**:
- Core engine class (e.g., `smart_link_engine.py`)
- Comprehensive test suite (unit + integration)
- Performance validation
- Lessons learned documentation

**Example**: Smart Link Management TDD Iteration 1 - LinkSuggestionEngine

---

### ✅ Phase 2: CLI Integration (Manual Trigger)

**Requirements**:
- [ ] CLI command added to existing workflow tools
- [ ] Rich interactive interface with progress reporting
- [ ] Export functionality (JSON/CSV/Markdown)
- [ ] Help text and usage examples
- [ ] Integration tests with real data

**Deliverables**:
- CLI module (e.g., `connections_demo.py`)
- Dedicated CLI (ADR-004, October 2025) or updated existing dedicated CLI
- CLI tests
- Usage documentation

**Example**: Smart Link Management TDD Iteration 2 - CLI Infrastructure

**⚠️ STOP HERE IS NO LONGER ACCEPTABLE**

---

### ✅ Phase 3: Automation Layer (Self-Running Workflows) **← MANDATORY**

**Requirements**:
- [ ] **Event-Driven** OR **Scheduled** automation (at least one)
- [ ] No manual trigger required for typical usage
- [ ] Background daemon integration
- [ ] User notification system
- [ ] Duplicate/redundant processing prevention
- [ ] Tests validate automatic execution

**Implementation Options** (choose one or more):

#### Option A: Event-Driven (File Watchers)
```python
# Example: Auto-process screenshots when added to OneDrive
from watchdog.events import FileSystemEventHandler

class ScreenshotWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(('.png', '.jpg')):
            # Trigger screenshot processing automatically
            process_screenshot(event.src_path)
```

**Use Cases**:
- New screenshots in OneDrive → Auto-OCR processing
- New notes in Inbox → Auto-enhancement
- File moved → Auto-link updates

#### Option B: Scheduled Processing (Cron/APScheduler)
```python
# Example: Nightly fleeting note triage
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=fleeting_triage_workflow,
    trigger='cron',
    hour=23,  # 11 PM every night
    minute=0
)
```

**Use Cases**:
- Nightly fleeting note triage
- Weekly review generation
- Daily inbox processing

#### Option C: Progressive Automation (Event Chain)
```python
# Example: New note → Enhance → Tag → Suggest Links
def on_note_created(note_path):
    # Step 1: Auto-enhance
    quality_score = enhance_note(note_path)
    
    # Step 2: Auto-tag if quality > 0.7
    if quality_score > 0.7:
        tags = auto_tag_note(note_path)
    
    # Step 3: Suggest connections
    if len(tags) >= 3:
        suggest_links(note_path)
    
    # Step 4: Notify user
    notify("Note enhanced and ready for review", note_path)
```

**Use Cases**:
- Note creation → full AI pipeline
- Screenshot → OCR → note → enhancement chain
- Import → triage → promotion workflow

**Deliverables**:
- Automation module (e.g., `smart_link_automation.py`)
- Daemon integration code
- Event handler OR scheduler configuration
- Notification system integration
- Automation tests (event simulation, scheduling validation)
- User configuration options

**Example Target**: Smart Link Management automation would auto-suggest links whenever a new note is created in Inbox with >3 tags

---

### ✅ Phase 4: Monitoring & Alerts (Observability) **← MANDATORY**

**Requirements**:
- [ ] Performance metrics collected (execution time, throughput)
- [ ] Error tracking with structured logging
- [ ] Health checks detect failures
- [ ] Alert system notifies user of issues
- [ ] Recovery strategies implemented
- [ ] Analytics dashboard or reports

**Implementation Components**:

#### A. Performance Monitoring
```python
# Example: Track processing metrics
import structlog
from prometheus_client import Histogram

processing_time = Histogram('feature_processing_seconds', 
                            'Time spent processing',
                            ['feature_name'])

@processing_time.labels('smart_links').time()
def process_smart_links(note_path):
    logger = structlog.get_logger()
    logger.info("processing_started", note=note_path)
    
    result = suggest_links(note_path)
    
    logger.info("processing_completed", 
                note=note_path, 
                suggestions=len(result))
    return result
```

**Metrics to Track**:
- Processing time (p50, p95, p99)
- Throughput (items/hour)
- Success rate
- Memory usage
- AI API latency

#### B. Error Handling & Recovery
```python
# Example: Automatic retry with exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=4, max=10))
def call_ai_api_with_retry(prompt):
    try:
        return ai_client.generate(prompt)
    except APIError as e:
        logger.error("ai_api_failed", error=str(e), attempt=e.attempt)
        raise  # Will retry automatically
```

**Error Scenarios**:
- AI service unavailable → Retry with backoff
- File system errors → Skip and log
- Processing timeout → Queue for later
- Dependency missing → Graceful degradation

#### C. Health Checks
```python
# Example: Feature health endpoint
def check_feature_health():
    health = {
        'status': 'healthy',
        'checks': {
            'ai_service': check_ollama_connection(),
            'file_system': check_inbox_accessible(),
            'queue': check_queue_depth(),
            'recent_errors': get_error_count_last_hour()
        }
    }
    
    if any(not v for v in health['checks'].values()):
        health['status'] = 'degraded'
    
    return health
```

**Health Indicators**:
- AI service connectivity
- File system access
- Processing queue depth
- Recent error rate
- Last successful run

#### D. User Alerts
```python
# Example: macOS notification on failure
def notify_user(title, message, critical=False):
    if critical or error_count > threshold:
        os.system(f"""
            osascript -e 'display notification "{message}" 
            with title "{title}" sound name "Basso"'
        """)
```

**Alert Triggers**:
- Automation failure (3+ consecutive failures)
- High error rate (>5% in last hour)
- Performance degradation (2x slower than baseline)
- Health check failure
- Daily/weekly summary reports

**Deliverables**:
- Monitoring module (e.g., `smart_link_monitoring.py`)
- Structured logging configuration
- Metrics collection integration
- Health check implementation
- Alert/notification system
- Dashboard or report generation
- Monitoring tests

**Example Target**: Smart Link Management monitoring would track: suggestion generation time, connection discovery success rate, link insertion failures, daily suggestions generated

---

## 🚨 Enforcement: When to Add Phase 3 & 4

### For New Features (Greenfield Development)
**Phase 3 & 4 are MANDATORY from the start**

```
TDD Iteration 1: Core Engine (Phase 1)
TDD Iteration 2: CLI Integration (Phase 2)
TDD Iteration 3: Automation Layer (Phase 3) ← REQUIRED
TDD Iteration 4: Monitoring & Alerts (Phase 4) ← REQUIRED
```

**No exceptions.** Feature is not production-ready until all 4 phases complete.

### For Existing Features (Retrofit Projects)
**Use `automation-completion-retrofit-manifest.md`**

Follow the retrofit roadmap:
1. Audit current phase completion
2. Prioritize features (P0, P1, P2)
3. Implement Phase 3 & 4 via TDD iterations
4. Integrate with unified automation daemon

---

## 📊 Phase-Specific TDD Patterns

### Phase 1: Core Engine TDD

**RED Phase**:
```python
def test_engine_processes_valid_input():
    engine = FeatureEngine()
    result = engine.process(valid_input)
    assert result.success
    assert len(result.output) > 0
```

**GREEN Phase**: Minimal implementation to pass tests

**REFACTOR Phase**: Extract utilities, optimize performance

### Phase 2: CLI Integration TDD

**RED Phase**:
```python
def test_cli_executes_feature():
    result = runner.invoke(cli, ['--feature-command', 'input.md'])
    assert result.exit_code == 0
    assert 'Feature completed' in result.output
```

**GREEN Phase**: CLI wrapper around Phase 1 engine

**REFACTOR Phase**: Rich UI, export options, help text

### Phase 3: Automation Layer TDD **← NEW**

**RED Phase**:
```python
def test_feature_triggers_on_file_event():
    # Simulate file creation
    create_test_file('inbox/test.md')
    
    # Wait for event processing
    time.sleep(1)
    
    # Verify automatic processing occurred
    assert feature_was_triggered('inbox/test.md')
    assert notification_sent()
```

**GREEN Phase**: Event handler → CLI execution wrapper

**REFACTOR Phase**: Debouncing, batch processing, notifications

**Critical Tests**:
- [ ] Feature triggers on correct events
- [ ] Duplicate processing prevented
- [ ] User notified of completion
- [ ] Failures handled gracefully
- [ ] Manual override still works

### Phase 4: Monitoring Layer TDD **← NEW**

**RED Phase**:
```python
def test_metrics_collected_during_processing():
    process_feature('test.md')
    
    metrics = get_feature_metrics()
    assert metrics['processing_time'] > 0
    assert metrics['success_count'] == 1
    assert metrics['error_count'] == 0
```

**GREEN Phase**: Add metrics collection to feature

**REFACTOR Phase**: Structured logging, dashboard aggregation

**Critical Tests**:
- [ ] Performance metrics recorded
- [ ] Errors logged with context
- [ ] Health check returns accurate status
- [ ] Alerts trigger on failure
- [ ] Recovery strategies execute

---

## 🎯 Success Criteria Per Phase

### Phase 1 ✅
- [ ] Feature works when called directly
- [ ] All tests pass
- [ ] Performance benchmarks met
- [ ] Architectural constraints maintained

### Phase 2 ✅
- [ ] CLI command functional
- [ ] Manual execution successful
- [ ] Export/formatting options work
- [ ] Help documentation complete

### Phase 3 ✅ **← MANDATORY**
- [ ] Feature runs WITHOUT manual trigger
- [ ] Event OR schedule automation working
- [ ] Background daemon integrated
- [ ] User notifications configured
- [ ] Automatic execution validated by tests

### Phase 4 ✅ **← MANDATORY**
- [ ] Metrics collected during execution
- [ ] Errors logged and tracked
- [ ] Health checks return status
- [ ] Alerts configured for failures
- [ ] Dashboard/reports available

---

## 🔄 Integration with Automation Daemon

### Daemon Architecture

```python
# development/src/automation/daemon.py

class InnerOSAutomationDaemon:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.watchers = []
        self.features = {}
    
    def register_feature(self, feature):
        """Register feature for automation."""
        # Add event watchers
        if feature.event_triggers:
            for trigger in feature.event_triggers:
                self.add_watcher(trigger, feature.execute)
        
        # Add scheduled jobs
        if feature.schedule:
            self.scheduler.add_job(
                feature.execute,
                trigger=feature.schedule
            )
        
        # Add monitoring
        self.features[feature.name] = feature
    
    def start(self):
        """Start daemon with all registered features."""
        self.scheduler.start()
        for watcher in self.watchers:
            watcher.start()
```

### Feature Integration Template

```python
# development/src/automation/features/smart_link_automation.py

class SmartLinkAutomation:
    """Phase 3 & 4 wrapper for Smart Link Management."""
    
    def __init__(self):
        self.engine = LinkSuggestionEngine()  # Phase 1
        self.monitor = FeatureMonitor('smart_links')  # Phase 4
    
    @property
    def event_triggers(self):
        """Define when feature should auto-execute."""
        return [
            FileEventTrigger(
                path='knowledge/Inbox/',
                pattern='*.md',
                event_type='created',
                debounce_seconds=5
            )
        ]
    
    @property
    def schedule(self):
        """Optional: scheduled execution."""
        return None  # Event-driven only
    
    def execute(self, context):
        """Execute feature with monitoring."""
        with self.monitor.track_execution():
            try:
                note_path = context['file_path']
                
                # Run Phase 1 engine
                suggestions = self.engine.suggest_links(note_path)
                
                # Notify user if valuable suggestions found
                if len(suggestions) > 3:
                    notify(f"Found {len(suggestions)} link suggestions",
                           f"Review: {note_path}")
                
                return {'success': True, 'suggestions': len(suggestions)}
                
            except Exception as e:
                self.monitor.log_error(e)
                # Attempt recovery
                return self.monitor.handle_failure(e)
```

---

## 📝 Workflow Checklist: Starting New Feature

### Before Writing Code

- [ ] Review `automation-completion-retrofit-manifest.md` for patterns
- [ ] Check architectural constraints (target class size <500 LOC)
- [ ] Read 2-3 completed TDD lessons learned for patterns
- [ ] Confirm all 4 phases are in project plan
- [ ] Identify automation trigger (event OR schedule)
- [ ] Define monitoring metrics to collect

### Phase 1 (Week 1)
- [ ] RED: Write failing engine tests
- [ ] GREEN: Implement minimal engine
- [ ] REFACTOR: Extract utilities, optimize
- [ ] COMMIT: Document Phase 1 completion

### Phase 2 (Week 1-2)
- [ ] RED: Write failing CLI tests
- [ ] GREEN: Implement CLI wrapper
- [ ] REFACTOR: Add rich UI, export options
- [ ] COMMIT: Document Phase 2 completion

### Phase 3 (Week 2) **← MANDATORY**
- [ ] RED: Write failing automation tests (event simulation)
- [ ] GREEN: Implement event handlers OR scheduler
- [ ] REFACTOR: Add notifications, deduplication
- [ ] INTEGRATE: Register with automation daemon
- [ ] COMMIT: Document Phase 3 completion

### Phase 4 (Week 2-3) **← MANDATORY**
- [ ] RED: Write failing monitoring tests
- [ ] GREEN: Implement metrics collection
- [ ] REFACTOR: Add alerting, health checks
- [ ] DASHBOARD: Create reports/visualization
- [ ] COMMIT: Document Phase 4 completion

### Production Deployment
- [ ] All 66+ tests passing
- [ ] Performance benchmarks validated
- [ ] Daemon integration tested
- [ ] User guide updated
- [ ] Lessons learned documented
- [ ] Feature marked production-ready in ACTIVE/

---

## 🚫 Anti-Patterns to Avoid

### ❌ "We'll add automation later"
**Impact**: Feature never gets automated, manual burden persists

**Fix**: Phase 3 & 4 are non-negotiable from day 1

### ❌ "CLI is good enough"
**Impact**: User must remember to run commands, features underused

**Fix**: Automation is the default; CLI is for overrides

### ❌ "Just cron job it"
**Impact**: No coordination, no monitoring, silent failures

**Fix**: Unified daemon with health monitoring

### ❌ "Monitoring is overkill"
**Impact**: Silent failures, no performance visibility, debugging nightmare

**Fix**: Phase 4 from the start prevents production mysteries

---

## 🎉 Expected Outcomes

### User Experience
- **Before**: "I need to remember to run 5 different commands"
- **After**: "Everything just works automatically"

### Developer Experience
- **Before**: Building features that stop at CLI
- **After**: Building complete self-running workflows

### System Maturity
- **Before**: Advanced toolbox requiring technical expertise
- **After**: Production-grade autonomous knowledge system

---

## 📚 Reference Examples

### Complete 4-Phase Features (Future State)
- Smart Link Management (after automation retrofit)
- Samsung Screenshot OCR (after automation retrofit)
- Weekly Review (upgrade from basic cron)

### Partial Examples (Learn & Complete)
- Current cron jobs (Phase 3 partial)
- Current health monitor (Phase 4 partial)
- WorkflowManager (Phase 1 & 2 only)

---

**Enforcement**: This workflow is now MANDATORY for all new feature development. AI assistant (Cascade) should reference this workflow and ensure all 4 phases are planned before starting Phase 1 development.
