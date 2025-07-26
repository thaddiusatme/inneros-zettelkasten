---
type: permanent
created: 2025-07-25 20:10
status: active
tags: [project, manifest]
visibility: private
---

# InnerOS Project Manifest (v2)

## Purpose
A single source-of-truth describing the InnerOS Zettelkasten-plus-AI workspace—its philosophy, file conventions, automation stack, and immediate roadmap.

## Guiding Principles
1. **Frictionless capture → insight**: every thought should become a compliant note in <15 s.
2. **Metadata first**: valid YAML drives all automation; pre-commit hooks enforce it.
3. **Incremental AI**: add machine assistance only where it compounds human creativity.
4. **Privacy by default**: all notes default to `visibility: private`; sharing is explicit.
5. **Audit-trail**: never delete knowledge; deprecate or archive with context.

## Directory & Workflow Overview
| Stage | Folder | Key Status Values | Automation |
|-------|--------|------------------|------------|
| Capture | `Inbox/` | `inbox` | Hotkey spawns `Templates/fleeting.md` |
| Triage  | `Fleeting Notes/` | `inbox` → `promoted` | Validator reports promotion candidates |
| Permanent | `Permanent Notes/` | `draft` → `published` | AI tagging, summarisation (Phase-5) |
| Archive | `Archive/` | `archived` | Auto-move via script after 90 d inactivity |

## Current Automation Stack
- **Metadata Validator** (`.automation/scripts/validate_metadata.py`)
- **Link Checker** (`.automation/scripts/link_checker.py`)
- **Changelog Updater** (`.automation/scripts/update_changelog.py`)
- **Pre-commit Hook** (`.automation/hooks/pre_commit`)

## Phase Roadmap
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | YAML standardisation | ✅ Complete |
| 2 | End-to-end workflow validation | ✅ Complete |
| 3 | Git + Changelog discipline | ✅ Complete |
| 4 | Capture friction removal | 🚧 In Progress |
| 5 | AI Tagging & Summaries | 🔜 Next |
| 6 | Multi-user & Sharing | ⏳ Future |

## Near-Term Objectives (Q3-2025)
1. Obsidian hotkeys/macros for instant fleeting, reference, literature notes.
2. Extend test suite to cover all `.automation/scripts` and reach ≥ 80 % coverage.
3. GitHub Actions CI: run validators + tests on every push.
4. Basic AI auto-tagging (local model) POC.
5. Weekly review automation: generate report of `status: inbox` & `promoted` notes.

## Governance
All structural changes (templates, validation rules, hooks) **must** be logged in `Windsurf Project Changelog.md` and linked to a commit. Deprecated docs are moved to `Archive/` with a timestamp suffix.

---
_This manifest supersedes earlier versions (now archived). Update it as the project evolves._
