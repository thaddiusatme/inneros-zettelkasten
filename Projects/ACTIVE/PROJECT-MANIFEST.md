# InnerOS — Project Manifest (Canonical)

**Purpose**: Single source of truth for the AI assistant and for current execution.  
**Audience**: You (now) → future contributors/users (later).  
**Last Updated**: 2025-12-22

---

## Product vision (1 paragraph)

InnerOS is a local-first, automation-driven knowledge operating system for Obsidian/Zettelkasten workflows. It aims to make capture, triage, linking, and promotion of notes safe, repeatable, and trustworthy—moving beyond “notes + plugins” toward an automation stack with strong safety guarantees (backup/dry-run/rollback), clear CLI workflows, and observable system health.

---

## Current state (what works today)

### Stable / useful now

- `make review` runs weekly review in preview mode with actionable recommendations.
- `make fleeting` runs fleeting health reporting against `knowledge/`.
- Dedicated CLIs exist (ADR-004 direction) and core flows generally work when `--vault knowledge` is provided.
- CI-lite / pre-commit quality gates and CLI logging/JSON contract work are in place.

### Known friction / blockers

- **Usability gap**: no single obvious daily command for inbox processing (new issue #77).
- **Output trust gap**: tag junk/prompt artifacts appearing in outputs (new issue #75).
- **Entry-point drift**: `inneros` wrapper needs routing to the dedicated CLIs (new issue #78; #76 is duplicate).
- **Automation reliability**: `inneros-up` default profile needs to be consistently healthy (Issue #51).

---

## Daily workflow (what you should do)

### Daily

- `make inbox` (to be added; Issue #77)
- `make status` (optional; check health)

### Weekly

- `make review`

---

## Roadmap (execution order)

### P0 (Make it usable in 1–2 weeks)

- **#77**: Add `make inbox` / `make inbox-safe` Make targets for Inbox processing.
- **#75**: Tag sanitization and normalization to prevent prompt artifacts.

### P1 (Make it consistent and less confusing)

- **#78**: Route `inneros` wrapper workflow commands to dedicated ADR-004 CLIs.
- **#51**: Harden `inneros-up` default profile reliability.

### P2 (Make it shareable)

- Complete vault config migration phases (reduce hidden path assumptions).
- Retire legacy `workflow_demo.py` paths.
- Consolidate user docs into `Projects/REFERENCE/` and ensure starter-pack parity.

---

## Canonical references

- Current sprint plan: `Projects/ACTIVE/SPRINT-MAKE-IT-USABLE.md`
- Discovery baseline: `Projects/ACTIVE/DISCOVERY-AUDIT.md`
- Project intake (high-level map): `Projects/ACTIVE/PROJECT-INTAKE.md`

---

## AI assistant focus contract
When context is limited, prioritize:

- This manifest
- The sprint plan
- Discovery audit
- Open GitHub issues tagged P0/P1

Avoid pulling in historical lessons learned unless debugging a related subsystem.
