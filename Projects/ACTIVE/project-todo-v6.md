---
type: project-manifest
created: 2025-10-26 15:34
updated: 2025-10-26 16:05
status: active
priority: P0
tags: [project-tracking, priorities, note-lifecycle, hygiene-bundle, shipping]
---

# InnerOS Zettelkasten - Project Todo v6.0

**Last Updated**: 2025-10-26 16:05 PDT
**Scope**: Entire InnerOS (Solopreneur Edition)
**Current Sprint**: Note Lifecycle P0 → Hygiene Bundle → v0.1.0-beta
**Decision**: Option B - Fix workflow issues first, then ship clean beta
**Previous Version**: `project-todo-v5.md`

---

## 🎯 Product Vision (Solopreneur Edition)

**Core Purpose**: Teachable, shippable personal knowledge management for a solo developer
- One-command dev, safety-first automation, clear docs
- Beta-ready: closed group of 3-5 power users without data loss
- CLI-first with optional web dashboard

---

## 🏗️ Current State

### Hygiene Bundle (95% Complete)

**Completed This Session**:
- ✅ Makefile with one-command dev (`make test`, `make cov`, `make run`, `make ui`)
- ✅ CI-Lite calls `make test` for local/CI alignment
- ✅ Daemon registry path fixes (3/3 daemons: youtube_watcher, screenshot_processor, health_monitor)
- ✅ .gitignore tightened (`.automation/metrics/`, `cache/logs/tmp/`, `reports/`)
- ✅ Docs skeleton:
  - `docs/ARCHITECTURE.md` (Mermaid system diagram)
  - `docs/HOWTO/` (weekly-review, inbox-processing, daemon-health, metrics-export)
  - `docs/adr/` (TEMPLATE, ADR-0001 provider policy, ADR-0002 prompt storage)
  - `docs/prompts/example_tagging_prompt.md`
- ✅ PROJECT-INTAKE.md (13-point, full InnerOS)
- ✅ Permissions: `chmod +x` on 2 daemon scripts
- ✅ Auto-fixed 14,789 code style issues (ruff --fix)

**In Progress**:
- 🟡 Quality gates: 13 real errors remain (E722 bare except, F821 undefined names)
  - `workflow_manager.py`: `dry_run` undefined (lines 315, 318)
  - Type hints: `QualityScore`, `WorkflowIntegrityResult` undefined
  - Bare `except:` clauses need exception types

**Remaining**:
- [ ] Decision: Ship now with known-issues note OR fix 13 errors first (15-30 min)
- [ ] Create branch `chore/repo-hygiene-bundle`
- [ ] Commit + push
- [ ] Open PR
- [ ] Merge to `main`
- [ ] Tag `v0.1.0-beta`

---

## 🔴 P0: Note Lifecycle Completion (From v4 - Restore Workflow Trust)

**Decision**: Option B chosen - Fix 77 orphaned notes before beta
**Rationale**: Beta users need a clean workflow; infrastructure without fixing broken capture pipeline = beta with known bugs
**Est. Time**: ~2 hours total for all PBIs
**Branch**: `fix/note-lifecycle-p0-completion`

### PBI-002: Literature Directory Integration (30 min)
**Status**: 🔴 Not started
**File**: `development/src/utils/note_lifecycle_manager.py`

Tasks:
- [ ] Add `self.literature_dir = base_dir / "Literature Notes"` to `__init__` (~line 25)
- [ ] Update `promote_note()` to handle `type: literature` notes
- [ ] Add directory existence checks and creation
- [ ] Write 3 tests (permanent/literature/fleeting note types)
- [ ] Verify 16/16 tests still passing (no regressions)

### PBI-003: Repair 77 Orphaned Notes (60 min)
**Status**: 🔴 Not started
**File**: `development/scripts/repair_orphaned_notes.py` (new)

Tasks:
- [ ] Write script to find notes with `ai_processed: true` AND `status: inbox`
- [ ] Update YAML frontmatter: `status: promoted`, add `processed_date: YYYY-MM-DD`
- [ ] Implement dry-run mode with preview table (note path, current/proposed status)
- [ ] Create timestamped backup before applying: `.automation/backups/orphaned-notes-repair-YYYYMMDD-HHMMSS/`
- [ ] Execute on 77 orphaned notes
- [ ] Verify zero notes remain with broken state

### PBI-004: Safe File Moves (30 min)
**Status**: 🔴 Not started
**File**: `development/scripts/safe_file_moves.py` (new, uses NoteLifecycleManager)

Tasks:
- [ ] Use `NoteLifecycleManager.promote_note()` for moves
- [ ] Validate frontmatter `type:` field matches destination
- [ ] Update backlinks after moves (preserve zettelkasten integrity)
- [ ] Generate migration report (files moved, errors, rollback instructions)
- [ ] Dry-run validation before execution

**Acceptance Criteria**:
- [ ] All 3 note types (permanent/literature/fleeting) handled in NoteLifecycleManager
- [ ] 77 orphaned notes repaired with correct status and processed_date
- [ ] Zero notes with `ai_processed: true` AND `status: inbox` remain
- [ ] Dry-run shows accurate preview for all operations
- [ ] All tests passing (16+ tests, zero regressions)
- [ ] Knowledge capture pipeline trusted (v4 P0 goal achieved)

---

## 🟡 P1: Complete Hygiene Bundle + Ship Beta (After P0)

### Fix Remaining Lint Errors (15-30 min)
- [ ] Fix 13 lint errors (E722 bare except, F821 undefined names)
  - `workflow_manager.py` line 315, 318: `dry_run` undefined
  - Type hints: `QualityScore`, `WorkflowIntegrityResult`
- [ ] Verify `make test` exits 0

### Ship v0.1.0-beta
- [ ] Create branch `chore/repo-hygiene-bundle-and-lifecycle-fixes`
- [ ] Commit all changes:
  ```
  Repo hygiene bundle + note lifecycle P0 fixes
  
  Note Lifecycle (v4 P0 completion):
  - PBI-002: Literature directory integration
  - PBI-003: Repair 77 orphaned notes (ai_processed + status fix)
  - PBI-004: Safe file moves with backlink updates
  
  Hygiene Bundle:
  - Add Makefile for one-command dev (make test/cov/run/ui)
  - Update CI-Lite to call make test
  - Fix daemon_registry.yaml paths (3/3 daemons)
  - Tighten .gitignore (metrics, cache, logs, tmp, reports)
  - Add docs: ARCHITECTURE, HOWTOs, ADRs, prompts/
  - Persist PROJECT-INTAKE.md (13-point)
  - Auto-fix 14,789 style issues + fix 13 real errors
  - Set daemon script permissions
  ```
- [ ] Push branch
- [ ] Open PR with validation checklist
- [ ] Merge to main
- [ ] Tag `v0.1.0-beta -m "First teachable, shippable cut with clean workflow"`
- [ ] Push tag

---

## 🟡 P1: Post-Beta Immediate (Week 2)

- [ ] Fix 13 lint errors (if shipped with Option A)
- [ ] Nightly coverage job (GitHub Actions schedule → `make cov` at 07:23 UTC)
- [ ] CONTRIBUTING.md + PR template + bug report template
- [ ] Open backlog issues (P0/P1/P2 from hygiene plan)
- [ ] Link `knowledge-starter-pack/` from README
- [ ] Web UI feature flag for unfinished pages + DoD doc
- [ ] Remove `workflow_demo.py` (ADR-004) + update CLI-REFERENCE

---

## 🟡 P1: Automation Visibility UX (Week 3-4)

- [ ] Integrate `AutomationStatusCLI` into `./inneros` wrapper or small TUI
- [ ] Surface daemon health in Web UI (read-only dashboard card)
- [ ] Add daemon start/stop helpers (optional)

---

## 🟡 P1: WorkflowManager Decomposition (November)

- [ ] Extract ConnectionManager (~300 LOC)
- [ ] Extract AnalyticsCoordinator (~400 LOC)
- [ ] Extract PromotionEngine (~200 LOC)

Success: WorkflowManager < 1,500 LOC; clear unit boundaries

---

## 🟢 P2: Templates & Evening Screenshots

- [ ] Design Templater-driven workflow triggers (discovery phase)
- [ ] Extract Evening Screenshots to `evening_screenshots_cli.py` with summary

---

## 📊 Success Metrics (Beta)

- **Tests**: CI-Lite green on PRs; local `make test` < 2 min
- **UX**: Weekly review + inbox processing run end-to-end with `--dry-run` + backup
- **Observability**: Daemon status visible in <5s; metrics endpoint returns JSON
- **Docs**: 4+ HOWTOs discoverable; architecture diagram present
- **Release**: v0.1.0-beta tagged and pushed

---

## 🚀 Immediate Next Actions

1. **Decide**: Ship now (Option A) or fix 13 errors first (Option B)?
2. **Create branch**: `chore/repo-hygiene-bundle`
3. **Commit**: All hygiene bundle changes
4. **Push + PR**: Open with validation checklist
5. **Merge + Tag**: `v0.1.0-beta`

---

## 🔗 Key References

- **Intake**: `Projects/ACTIVE/PROJECT-INTAKE.md`
- **CI**: `.github/workflows/ci-lite.yml`
- **Docs**: `docs/ARCHITECTURE.md`, `docs/HOWTO/*`, `docs/adr/*`
- **Automation**: `.automation/config/daemon_registry.yaml`, `development/src/cli/automation_status_cli.py`
- **Observability**: `web_ui/app.py` (`/api/metrics`), `development/src/monitoring/*`

---

**Version History**:
- v6.0 (Oct 26, 2025 15:34): Hygiene bundle 95% complete; decision point for shipping strategy
- v5.0 (Oct 26, 2025 15:24): Scope confirmed (entire InnerOS); hygiene bundle started
- v4.0 (Oct 22, 2025): October completions; YouTube automation + cleanup system
- v3.0 (Oct 13, 2025): Architectural pivot; testing infrastructure
- Earlier: See v4 for full history

**Archive**: Previous versions in `Projects/ACTIVE/` for historical context
