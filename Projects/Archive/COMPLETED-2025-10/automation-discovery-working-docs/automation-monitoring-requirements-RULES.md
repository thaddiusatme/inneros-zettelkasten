# Automation & Monitoring Requirements

> **Purpose**: Phase 3 & 4 mandatory requirements for all features  
> **Updated**: 2025-10-06  
> **Companion to**: `updated-development-workflow.md`

---

## 🤖 4-Phase Feature Development (MANDATORY)

**All new features MUST complete 4 phases to be production-ready:**

### Phase 1: Core Engine ✅
- TDD implementation (RED → GREEN → REFACTOR)
- Integration with existing AI infrastructure
- Performance benchmarks met
- Architectural constraints (<500 LOC, <20 methods per class)

### Phase 2: CLI Integration ✅
- CLI command with rich interactive interface
- Export functionality (JSON/CSV/Markdown)
- Integration tests with real data
- Usage documentation

### Phase 3: Automation Layer **← MANDATORY**

**Requirement**: Feature runs WITHOUT manual trigger for typical usage

**Implementation Options** (choose at least one):

**A. Event-Driven** (preferred for real-time):
- File watchers for OneDrive screenshots
- File watchers for Inbox note creation
- File move triggers for link updates

**B. Scheduled** (preferred for batch):
- Nightly: Fleeting note triage, screenshot processing
- Weekly: Review generation, analytics
- Daily: Inbox enhancement, connection discovery

**C. Progressive Chains** (for workflows):
- Note created → Auto-enhance → Auto-tag → Suggest links
- Screenshot added → OCR → Note creation → Enhancement

**Deliverables**:
- Daemon integration code
- Event handler OR scheduler configuration
- User notification system
- Automation tests (event simulation or schedule validation)

**Definition of Done**:
- [ ] Feature executes automatically (no manual CLI trigger needed)
- [ ] Background daemon integrated
- [ ] User receives notifications on completion
- [ ] Tests validate automatic execution
- [ ] Duplicate processing prevented

### Phase 4: Monitoring & Alerts **← MANDATORY**

**Requirement**: Complete observability for production operation

**Must Collect**:

**Performance Metrics**:
- Processing time per operation (p50, p95, p99)
- Throughput (items/hour)
- Success rate percentage
- Memory usage

**Error Tracking**:
- Structured logging with context
- Error rate per hour
- Failure categorization
- Automatic retry attempts

**Health Checks**:
- Feature availability status
- Dependency health (AI service, file system)
- Queue depth monitoring
- Last successful run timestamp

**Alerting**:
- Critical: 3+ consecutive failures → macOS notification
- Warning: Error rate >5% last hour → macOS notification
- Info: Daily/weekly summary reports

**Deliverables**:
- Monitoring module with metrics collection
- Structured logging configuration
- Health check endpoint/function
- Alert/notification system
- Dashboard or report generation

**Definition of Done**:
- [ ] Metrics collected during every execution
- [ ] Errors logged with full context
- [ ] Health check returns accurate status
- [ ] Alerts trigger on failure conditions
- [ ] Recovery strategies implemented

---

## 🎯 Daemon Integration Pattern

Every feature must provide this interface:

```python
# File: development/src/automation/features/[feature_name]_automation.py

class FeatureAutomation:
    """Phase 3 & 4 wrapper for [Feature Name]."""
    
    def __init__(self):
        self.engine = FeatureEngine()  # Phase 1
        self.monitor = FeatureMonitor('feature_name')  # Phase 4
    
    @property
    def event_triggers(self) -> List[EventTrigger]:
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
    def schedule(self) -> Optional[str]:
        """Cron schedule if scheduled execution needed."""
        return None  # or "0 23 * * *" for nightly at 11 PM
    
    def execute(self, context: dict) -> dict:
        """Execute feature with monitoring."""
        with self.monitor.track_execution():
            try:
                # Run Phase 1 engine
                result = self.engine.process(context['file_path'])
                
                # Notify user if valuable
                if result.success:
                    notify(f"[Feature] completed", result.summary)
                
                return {'success': True, 'data': result}
                
            except Exception as e:
                self.monitor.log_error(e)
                return self.monitor.handle_failure(e)
```

---

## 📋 Updated Development Checklists

### Pre-Development Checklist (ADD THESE)
- [ ] **Review complete-feature-development workflow** (all 4 phases planned)
- [ ] **Identify automation trigger** (event-driven, scheduled, or chain)
- [ ] **Define monitoring metrics** (what will be tracked)
- [ ] **Confirm daemon integration plan** (how feature registers)

### Development Validation (ADD THESE)
- [ ] **Phase 3 implemented**: Automation layer complete
- [ ] **Phase 4 implemented**: Monitoring layer complete

### Completion Checklist (ADD THESE)
- [ ] **Phase 3 validated**: Feature runs automatically without manual trigger
- [ ] **Phase 4 validated**: Monitoring, alerts, health checks operational
- [ ] **Daemon integrated**: Feature registered with automation daemon
- [ ] **Automation tested**: Event/schedule triggers working
- [ ] **Monitoring tested**: Metrics collection and alerting working

### Project Health Indicators (ADD THESE)
- **Automation Coverage**: 100% (all features have Phase 3)
- **Monitoring Coverage**: 100% (all features have Phase 4)
- **Daemon Uptime**: >99% (automatic restart on crash)
- **Event Response**: <5 seconds from trigger to processing start

---

## 📚 Reference Documents

**Primary Workflow**:
- `.windsurf/workflows/complete-feature-development.md` - Detailed 4-phase TDD methodology

**Planning & Retrofit**:
- `Projects/ACTIVE/automation-completion-retrofit-manifest.md` - Retrofit roadmap for existing features
- `Projects/ACTIVE/automation-system-implementation-summary.md` - Implementation overview

**Examples**:
- See Sprint 1-4 roadmap in automation-completion-retrofit-manifest.md
- Background daemon architecture and code examples

---

## 🚨 Enforcement

**STOP and refer to this document if**:
- Starting any new feature development
- Feature only has Phase 1 & 2 (Engine + CLI)
- "We'll add automation later" mentioned
- Feature requires manual CLI triggers

**Phase 3 & 4 are NOT optional.** They are core requirements for production-ready features.

---

## 📊 Success Metrics

**Feature-Level**:
- Zero features in production with only Phase 1 & 2
- 100% automation coverage by end of retrofit (5 weeks)
- 100% monitoring coverage by end of retrofit (5 weeks)

**System-Level**:
- 80% reduction in manual workflow triggers
- 90% of notes/screenshots processed within 1 hour
- <1% automation failure rate
- <5s event response time

---

**Version**: 1.0  
**Last Updated**: 2025-10-06  
**Character Count**: ~5,500 (well under 12K limit)
