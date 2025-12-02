# Sprint: Make InnerOS Usable

> **Goal**: Transform InnerOS from a development project into a daily-use tool  
> **Created**: 2025-12-01  
> **Target Completion**: 2 weeks  
> **Success Criteria**: You use InnerOS daily without thinking about it

---

## 🎯 The Gap We're Closing

**Current State**: Powerful infrastructure that sits unused
- 1,384 passing tests
- 30+ CLI tools
- 29 automation modules
- Complex documentation across 5+ locations

**Target State**: Simple tool you actually use
- 2 commands to remember: `inneros-up`, `inneros-status`
- 1 place for docs: `Projects/REFERENCE/`
- Automation runs without intervention
- You know it's working without debugging

---

## 📋 Sprint Plan (4 Phases)

### Phase 0: Discovery & Alignment (Day 1)
**Goal**: Understand what exists and align documentation

#### Step 0.1: Codebase Discovery Audit ✅ COMPLETE
- [x] Inventory all CLI entry points (48 files found)
- [x] Test which automation handlers actually work
- [x] Identify broken/deprecated code paths
- [x] Document in `Projects/ACTIVE/DISCOVERY-AUDIT.md`

**Discovery Results**:
```bash
# Handler Status (2025-12-01):
- [x] Status CLI: ✅ Works - shows 3 handlers
- [x] Weekly review: ✅ Works - found 55 notes to review
- [x] Fleeting CLI: ✅ Works - 80 notes, 68% critical backlog
- [ ] Screenshot handler: ⚠️ Untested (needs OneDrive path)
- [ ] Smart Link handler: ❌ Import error (connections_demo.py broken)
- [ ] YouTube handler: ⚠️ Untested
```

**Key Findings**:
- CLIs work but require `--vault knowledge` flag
- Makefile now has: `make up`, `make down`, `make status`, `make review`, `make fleeting`
- 3 CLIs have import errors needing fixes

#### Step 0.2: Documentation Alignment ✅ COMPLETE
- [x] Archive stale docs (moved FEATURE-STATUS.md to Archive/)
- [x] Updated START-HERE.md with new Makefile commands
- [x] Cleaned up Projects/ACTIVE/ (82 → 11 files)
- [x] Created GitHub issues for non-critical bugs (#53, #54)
- [x] Consolidate to single source of truth:
  - **`Projects/REFERENCE/START-HERE.md`** - Daily commands
  - **`Projects/ACTIVE/`** - 11 files, current sprint only
  - **`GitHub Issues`** - 14 open issues tracked

---

### Phase 1: Fix Core Automation (Days 2-5)
**Goal**: One command starts automation, one checks status

#### Step 1.1: Fix `inneros-status` (Issue #50)
- [ ] Verify `inneros_status_cli.py` runs without errors
- [ ] Test output shows all 3 daemons
- [ ] Add to Makefile: `make status`
- [ ] Verify exit codes work (0 = healthy, 1 = unhealthy)

**Test Command**:
```bash
PYTHONPATH=development python3 development/src/cli/inneros_status_cli.py
```

#### Step 1.2: Fix `inneros-up` (Issue #51)
- [ ] Identify what blocks `screenshot_processor` and `health_monitor`
- [ ] Fix startup sequence
- [ ] Add to Makefile: `make up`
- [ ] Test: Run once, check status, verify daemons running

**Target Makefile Additions**:
```makefile
up:
	PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py start

down:
	PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py stop

status:
	PYTHONPATH=development python3 development/src/cli/inneros_status_cli.py
```

#### Step 1.3: Migrate Automation Scripts to CLIs (Issue #39)
- [ ] Identify scripts using wrong argument patterns
- [ ] Fix CLI syntax mismatches (Issue #47)
- [ ] Validate with integration tests

---

### Phase 2: End-to-End Workflow Validation (Days 6-8)
**Goal**: Verify real workflows work without manual intervention

#### Step 2.1: Screenshot Workflow Test
```bash
# 1. Drop a screenshot in OneDrive folder
# 2. Wait 60 seconds
# 3. Check: New note created in knowledge/Inbox/?
# 4. Check: OCR text extracted?
```
- [ ] Test passes
- [ ] Document any failures in DISCOVERY-AUDIT.md

#### Step 2.2: Smart Link Workflow Test
```bash
# 1. Create a new note in knowledge/Inbox/
# 2. Wait for automation
# 3. Check: Link suggestions generated?
```
- [ ] Test passes
- [ ] Document any failures

#### Step 2.3: YouTube Workflow Test
```bash
# 1. Add a YouTube URL to a note
# 2. Run YouTube CLI
# 3. Check: Quotes extracted?
# Note: May be blocked by IP ban
```
- [ ] Test passes OR document IP ban status
- [ ] If blocked, skip for now

#### Step 2.4: Weekly Review Workflow Test
```bash
PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py weekly-review
```
- [ ] Test runs without error
- [ ] Output shows actionable recommendations
- [ ] Export works

---

### Phase 3: User Documentation (Days 9-10)
**Goal**: Create the "just tell me how to use it" doc

#### Step 3.1: Create `Projects/REFERENCE/DAILY-WORKFLOW.md`
Simple 1-page guide:
```markdown
# InnerOS Daily Workflow

## Starting Your Day
make up          # Start automation
make status      # Verify healthy

## During the Day
- Drop screenshots → auto-processed
- Create notes → auto-linked
- Add YouTube URLs → run `make youtube` when ready

## Weekly Review
make review      # Get promotion recommendations
```

#### Step 3.2: Update Makefile with User Commands
```makefile
# User commands (what you use daily)
up:      ...
down:    ...
status:  ...
review:  ...
youtube: ...

# Dev commands (for development only)
test:    ...
lint:    ...
```

#### Step 3.3: Cleanup `Projects/REFERENCE/`
- [ ] Archive stale docs
- [ ] Ensure START-HERE.md → DAILY-WORKFLOW.md flow
- [ ] Remove deprecated references

---

### Phase 4: Validation & Handoff (Days 11-14)
**Goal**: You're actually using it

#### Step 4.1: Daily Use Test (3 days)
- [ ] Day 1: Run `make up`, use normally, run `make status` at end
- [ ] Day 2: Check notes created, links suggested, status healthy
- [ ] Day 3: Run weekly review, verify recommendations make sense

#### Step 4.2: Document Issues Found
- [ ] Create GitHub issues for any problems
- [ ] Update DISCOVERY-AUDIT.md with learnings

#### Step 4.3: Sprint Retrospective
- [ ] What worked?
- [ ] What's still broken?
- [ ] What's the next priority?

---

## 📊 Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Commands to remember | 2 | `make up`, `make status` |
| Daily startup time | <10 seconds | Time from terminal to "healthy" |
| Weekly review time | <5 minutes | Time from command to decisions |
| Broken workflows | 0 | End-to-end tests pass |
| Documentation locations | 1 | Everything in `Projects/REFERENCE/` |

---

## 🚫 Out of Scope (Explicitly Deferred)

- [ ] Web UI improvements (Issue #28)
- [ ] YouTube test failures (Issue #18, 255 failures)
- [ ] WorkflowManager decomposition (Issue #19)
- [ ] New features

**Focus**: Make what exists work, don't add new things.

---

## 📁 Artifacts to Create

1. **`Projects/ACTIVE/DISCOVERY-AUDIT.md`** - What works, what's broken
2. **`Projects/REFERENCE/DAILY-WORKFLOW.md`** - 1-page user guide
3. **Updated Makefile** - User-friendly commands
4. **GitHub Issues** - For any blockers found

---

## 🔗 Related Issues

- [#50](https://github.com/thaddiusatme/inneros-zettelkasten/issues/50) - Automation CLI and status UX epic
- [#51](https://github.com/thaddiusatme/inneros-zettelkasten/issues/51) - Make inneros-up default profile healthy
- [#39](https://github.com/thaddiusatme/inneros-zettelkasten/issues/39) - Migrate automation scripts to CLIs
- [#47](https://github.com/thaddiusatme/inneros-zettelkasten/issues/47) - CLI syntax mismatch bug
- [#20](https://github.com/thaddiusatme/inneros-zettelkasten/issues/20) - Automation visibility UX

---

**Next Action**: Start Phase 0.1 - Run discovery audit to understand what actually works.

---

*Created: 2025-12-01 | Status: Ready to Start*
