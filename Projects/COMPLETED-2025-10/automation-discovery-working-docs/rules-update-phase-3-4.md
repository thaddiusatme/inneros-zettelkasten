# Rules Update: Phase 3 & 4 Requirements

> **Purpose**: Text to manually add to `.windsurf/rules/updated-development-workflow.md`  
> **Date**: 2025-10-06  
> **Action**: Copy sections below into the rules file

---

## 📝 Instructions

Add the following sections to `.windsurf/rules/updated-development-workflow.md`:

### 1. Update TDD Methodology Section (after line 23)

**ADD AFTER** the line `- Integration testing with existing AI workflows`:

```markdown
- **Phase 3 & 4 Mandatory**: All features must include Automation (Phase 3) and Monitoring (Phase 4)
- **Reference Workflow**: See `.windsurf/workflows/complete-feature-development.md` for 4-phase methodology
```

---

### 2. Add New Section: 4-Phase Feature Development (after line 157)

**INSERT NEW SECTION** after "Integration-First Development":

```markdown
### 4-Phase Feature Development (MANDATORY)

**All new features must complete 4 phases to be production-ready:**

#### Phase 1: Core Engine (AI/Processing Logic)
- TDD implementation with RED → GREEN → REFACTOR
- Integration with existing AI infrastructure
- Performance benchmarks met
- Architectural constraints maintained (<500 LOC, <20 methods)

#### Phase 2: CLI Integration (Manual Trigger)
- CLI command added with rich interactive interface
- Export functionality (JSON/CSV/Markdown)
- Integration tests with real data
- Usage documentation

#### Phase 3: Automation Layer (Self-Running) **← MANDATORY**
- **Event-driven** OR **scheduled** automation implemented
- No manual trigger required for typical usage
- Background daemon integration
- User notification system
- Tests validate automatic execution

**Automation Options**:
- File watchers (OneDrive, Inbox) for event-driven processing
- APScheduler for cron-like scheduling
- Progressive chains (note created → enhance → tag → link)

#### Phase 4: Monitoring & Alerts (Observability) **← MANDATORY**
- Performance metrics collected (time, throughput, success rate)
- Error tracking with structured logging
- Health checks detect failures
- Alert system notifies user of issues
- Recovery strategies implemented

**Monitoring Requirements**:
- Processing time (p50, p95, p99)
- Success/error rates
- Health check endpoints
- macOS notifications for critical failures
- Dashboard or reports

**See**: `.windsurf/workflows/complete-feature-development.md` for detailed TDD patterns per phase
```

---

### 3. Update Current Development Patterns (replace lines 210-223)

**REPLACE** the section starting with "### TDD Success Patterns" with:

```markdown
### TDD Success Patterns (Updated October 2025)

- **4-Phase Methodology**: ALL features must include Engine, CLI, Automation, and Monitoring
- **Automation-First**: Phase 3 (Automation) is non-negotiable for production readiness
- **Observability Built-In**: Phase 4 (Monitoring) prevents silent failures and debugging mysteries
- **Utility Extraction**: Modular architecture enables rapid development and reusability
- **Real Data Validation**: Testing with production data proves immediate user value
- **Integration Excellence**: Building on existing infrastructure delivers 80% faster development
- **Architectural Testing**: Prevent god classes through size constraints and regular reviews

**New Feature Checklist**:
1. Review `.windsurf/workflows/complete-feature-development.md` BEFORE starting
2. Plan all 4 phases in project manifest
3. Identify automation trigger (event OR schedule)
4. Define monitoring metrics to collect
5. Confirm architectural constraints won't be violated
```

---

### 4. Update Pre-Development Checklist (after line 238)

**ADD** to the Pre-Development Checklist:

```markdown
- [ ] **Review complete-feature-development workflow** (all 4 phases planned)
- [ ] **Identify automation trigger** (event-driven or scheduled)
- [ ] **Define monitoring metrics** (what will be tracked)
- [ ] **Confirm daemon integration plan** (how feature registers with automation system)
```

---

### 5. Update Completion Checklist (after line 254)

**ADD** to the Completion Checklist:

```markdown
- [ ] **Phase 3 complete**: Feature runs automatically without manual trigger
- [ ] **Phase 4 complete**: Monitoring, alerts, and health checks operational
- [ ] **Daemon integrated**: Feature registered with automation daemon
- [ ] **Automation tested**: Event/schedule triggers validated
- [ ] **Monitoring validated**: Metrics collection and alerting working
```

---

### 6. Update Project Health Indicators (after line 273)

**ADD** to the Project Health Indicators:

```markdown
- **Automation Coverage**: 100% of features have Phase 3 (event or scheduled automation)
- **Monitoring Coverage**: 100% of features have Phase 4 (metrics, alerts, health checks)
- **Daemon Uptime**: >99% (automatic restart on crash)
- **Event Response**: <5 seconds from trigger to processing start
```

---

### 7. Add New Section: Automation & Monitoring Standards (after line 287)

**INSERT NEW SECTION** before "Architectural Health":

```markdown
## 🤖 Automation & Monitoring Standards

### Automation Requirements (Phase 3)
Every feature MUST have at least ONE automation method:

**Event-Driven** (preferred for real-time needs):
- File watchers for OneDrive screenshots
- File watchers for Inbox note creation
- File move triggers for link updates

**Scheduled** (preferred for batch processing):
- Nightly: Fleeting note triage, screenshot processing
- Weekly: Review generation, analytics
- Daily: Inbox enhancement, connection discovery

**Progressive Chains** (for workflow automation):
- Note created → Auto-enhance → Auto-tag → Suggest links
- Screenshot added → OCR → Note creation → Enhancement

### Monitoring Requirements (Phase 4)
Every feature MUST collect:

**Performance Metrics**:
- Processing time per operation
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
- Critical: 3+ consecutive failures
- Warning: Error rate >5% last hour
- Info: Daily/weekly summary reports

### Daemon Integration Pattern

```python
# Every feature must provide this interface:
class FeatureAutomation:
    @property
    def event_triggers(self) -> List[EventTrigger]:
        """Define when feature auto-executes."""
        pass
    
    @property
    def schedule(self) -> Optional[str]:
        """Cron schedule if scheduled."""
        pass
    
    def execute(self, context: dict) -> dict:
        """Execute with monitoring."""
        pass
```

**See**: `Projects/ACTIVE/automation-completion-retrofit-manifest.md` for retrofit roadmap
```

---

### 8. Update See Also References (at end of file)

**ADD** to the "See Also" section at the bottom:

```markdown
- `.windsurf/workflows/complete-feature-development.md` - Mandatory 4-phase methodology
- `Projects/ACTIVE/automation-completion-retrofit-manifest.md` - Retrofit plan for existing features
```

---

## ✅ Validation Checklist

After manually updating the rules file, verify:

- [ ] All 8 new sections added correctly
- [ ] References to new workflow files included
- [ ] Phase 3 & 4 marked as MANDATORY
- [ ] Automation and monitoring requirements clear
- [ ] Code examples for daemon integration provided
- [ ] Pre-development and completion checklists updated

---

## 🎯 Impact

Once these updates are applied to `.windsurf/rules/updated-development-workflow.md`:

1. **All future AI interactions** will enforce 4-phase development
2. **New features** must include automation and monitoring from day 1
3. **Existing features** have clear retrofit path via automation-completion-retrofit-manifest.md
4. **TDD iterations** will automatically include Phase 3 & 4 in planning

**The gap you identified** (features without automation) will be prevented going forward and systematically addressed for existing features.
