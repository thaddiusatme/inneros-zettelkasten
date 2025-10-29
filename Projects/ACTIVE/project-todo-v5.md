---
type: project-manifest
created: 2025-10-26 15:24
updated: 2025-10-26 15:24
status: active
priority: P0
tags: [project-tracking, priorities, workflow-automation, note-lifecycle, hygiene-bundle]
---

# InnerOS Zettelkasten - Project Todo v5.0

**Last Updated**: 2025-10-26
**Scope**: Entire InnerOS (Solopreneur Edition)
**Previous Version**: `project-todo-v4.md`

---

## 🎯 Product Vision (Unchanged)

**Core Purpose**: Personal knowledge management tool for a solo developer power user
- CLI-first, local files, safety-first automation
- Teachable and shippable: clear docs, one-command dev, small but real tests
- Closed beta for a few power users without breakage or data loss

---

## 🏗️ Architectural Health

**Status**: ✅ Improving — hygiene bundle applied, CI aligned to Makefile, daemon registry corrected

### Stable
- Safety/backup workflows
- Weekly review analytics
- CI-Lite pattern (ruff/black/pyright/pytest via `make test`)

### In-Flux / Next Refactors
- `WorkflowManager` decomposition (ConnectionManager, AnalyticsCoordinator, PromotionEngine)
- Web UI scope and feature flags

---

## ✅ Recently Completed (Oct 26, 2025)

### Repo Hygiene Bundle
- Makefile (`test`, `cov`, `run`, `ui`)
- CI-Lite calls `make test`
- Daemon registry path fixes (3/3 daemons)
- .gitignore tightened (`.automation/metrics/`, cache|logs|tmp, `reports/`)
- Docs skeleton: ARCHITECTURE, HOWTOs (weekly review, inbox)
- ADRs: 0001 provider policy (local-first), 0002 prompt storage (draft)
- Observability HOWTOs: daemon health (uses AutomationStatusCLI), metrics export (`/api/metrics`)
- Intake persisted: `Projects/ACTIVE/PROJECT-INTAKE.md` (13-point, full InnerOS)

Impact: One-command dev, cleaner CI, safer automation visibility, repeatable setup

---

## 🔴 P0: Validate and Ship Hygiene Bundle (This Week)

- [ ] Permissions: `chmod +x` automated scripts
  - [ ] `.automation/scripts/automated_screenshot_import.sh`
  - [ ] `.automation/scripts/health_monitor.sh`
- [ ] Quality gates: `make test` (exit 0)
- [ ] Coverage (optional): `make cov`
- [ ] UI smoke: `python3 web_ui/app.py` → <http://localhost:8081>
- [ ] Branch/PR: `chore/repo-hygiene-bundle` with commit + push
- [ ] Merge to `main` (fast-forward OK or `--no-ff`)
- [ ] Tag `v0.1.0-beta`

Definition of Done
- [ ] Tests pass locally and in CI-Lite
- [ ] No untracked artifacts outside ignored paths
- [ ] Docs discoverable from README (links in a follow-up)

---

## 🟡 P1: Next Priorities (Short, High Leverage)

- [ ] Nightly coverage job (GitHub Actions schedule → `make cov`)
- [ ] CONTRIBUTING.md + PR template + bug report template
- [ ] Open backlog issues (P0/P1/P2) to reflect hygiene plan
- [ ] Link `knowledge-starter-pack/` from README (safe demo vault)
- [ ] Web UI feature flag and DoD note for unfinished pages
- [ ] Remove `workflow_demo.py` and update CLI-REFERENCE (per ADR-004)

---

## 🟡 P1: WorkflowManager Decomposition (Nov 2025)

- [ ] Extract ConnectionManager (~300 LOC)
- [ ] Extract AnalyticsCoordinator (~400 LOC)
- [ ] Extract PromotionEngine (~200 LOC)

Success: Reduced god-class risk; clearer unit boundaries

---

## 🟡 P1: Automation Visibility UX

- [ ] Integrate `AutomationStatusCLI` insights into `./inneros` wrapper or a small TUI
- [ ] Surface daemon health summary in Web UI (read-only)

---

## 🟢 P2: Templates & Evening Screenshots

- [ ] Templater-driven workflow triggers (design + MVP)
- [ ] Extract Evening Screenshots to `evening_screenshots_cli.py` with summary output

---

## 📊 Success Metrics

- Tests: CI-Lite green on PRs; local `make test` < 2 min
- UX: Weekly review runs end-to-end with `--dry-run` + backup; daemon status visible in <5s
- Docs: 2+ HOWTOs discoverable; architecture diagram present
- Release: v0.1.0-beta tagged after PR merge

---

## 🔗 References
- CI: `.github/workflows/ci-lite.yml`
- Docs: `docs/ARCHITECTURE.md`, `docs/HOWTO/*`, `docs/adr/*`
- Observability: `web_ui/app.py` (`/api/metrics`), `development/src/monitoring/*`
- Automation: `.automation/config/daemon_registry.yaml`, `development/src/cli/automation_status_cli.py`
- Intake: `Projects/ACTIVE/PROJECT-INTAKE.md`
