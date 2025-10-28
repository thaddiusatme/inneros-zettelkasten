# Minimal Addition for .windsurf/rules/updated-development-workflow.md

> **Instructions**: Append this section to the END of the existing rules file (after line 295)

---

## 🤖 4-Phase Feature Development (MANDATORY - Added Oct 2025)

**All new features must complete 4 phases:**

### Phase 1: Core Engine ✅ (existing)
TDD implementation, performance benchmarks, architectural constraints (<500 LOC, <20 methods)

### Phase 2: CLI Integration ✅ (existing)
CLI command, export functionality, integration tests, documentation

### Phase 3: Automation Layer **← NEW MANDATORY**
- **Requirement**: Event-driven OR scheduled automation (no manual trigger)
- **Options**: File watchers (OneDrive/Inbox), APScheduler (cron), progressive chains
- **Deliverables**: Daemon integration, user notifications, automated tests
- **See**: `.windsurf/workflows/complete-feature-development.md`

### Phase 4: Monitoring & Alerts **← NEW MANDATORY**
- **Requirement**: Metrics collection, error tracking, health checks, alerting
- **Metrics**: Processing time, success rate, throughput, memory usage
- **Alerts**: macOS notifications for 3+ failures, >5% error rate
- **See**: `.windsurf/workflows/complete-feature-development.md`

---

**Updated Checklists:**

Add to **Pre-Development Checklist** (line 239):
```
- [ ] Review complete-feature-development workflow (plan all 4 phases)
- [ ] Identify automation trigger (event-driven or scheduled)
- [ ] Define monitoring metrics (what will be tracked)
```

Add to **Completion Checklist** (line 255):
```
- [ ] Phase 3 complete: Feature runs automatically without manual trigger
- [ ] Phase 4 complete: Monitoring, alerts, health checks operational
- [ ] Automation tested: Event/schedule triggers validated
```

Add to **Project Health Indicators** (line 273):
```
- **Automation Coverage**: 100% (all features have Phase 3)
- **Monitoring Coverage**: 100% (all features have Phase 4)
```

---

**See Also** (add to line 294):
```
- `.windsurf/workflows/complete-feature-development.md` - Mandatory 4-phase methodology
- `Projects/ACTIVE/automation-completion-retrofit-manifest.md` - Retrofit roadmap
```

---

**Character Count**: ~1,600 (fits easily within 12K limit when added to existing ~9K file)
