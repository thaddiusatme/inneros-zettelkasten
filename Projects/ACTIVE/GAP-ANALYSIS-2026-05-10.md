# Gap Analysis — InnerOS Zettelkasten

**Date**: 2026-05-10
**Inputs reviewed**: `README.md`, `Projects/REFERENCE/inneros-manifest-v3.md`, `Projects/ACTIVE/SPRINT-MAKE-IT-USABLE.md`, `Projects/ACTIVE/PROJECT-STATUS-FEB-2026.md`, vault state audit (see `knowledge/CLAUDE.md` §5).
**Verdict**: **Yes, the project has drifted — substantially.** The aspirational docs describe a polished Phase 5/6 system. The vault and repo show a half-cleaned workshop with abandoned cleanup loops.

---

## TL;DR

| Dimension | Doc says | Reality | Gap |
|---|---|---|---|
| **Inbox health** | "Production-ready directory organization, P0+P1 complete" (manifest v3) | 174 files in Inbox, 124 with `status: promoted` stuck in place | ⚠️ Severe |
| **Vault hygiene** | "97% reduction in main directory clutter" (README) | Root has 6 empty `Untitled*.canvas`, 4 loose PNGs, `.bak` files, nested `knowledge/knowledge/`, stray `Users/thaddius/`, `scripts/`, `Test-Inbox/` | ⚠️ Severe |
| **Source of truth** | README points to manifest-v3; manifest points to `windsurfrules-v4` | 4 competing canonical-ish docs (manifest-v3, SPRINT-MAKE-IT-USABLE, PROJECT-STATUS-FEB-2026, rules README) | ⚠️ Moderate |
| **Manifest currency** | "Next review: 2025-09-25" | Today is 2026-05-10 — **~8 months stale** | ⚠️ Severe |
| **Active priorities** | Manifest: Phase 6 multi-user + UI | Reality: Agent RAG + Quality Scoring + housekeeping | ⚠️ Total pivot, undocumented in manifest |
| **README CLI paths** | `python3 src/cli/...`, `python3 quick_demo.py` | Actual paths are `development/src/cli/...`; `quick_demo.py` not at root | ⚠️ Onboarding broken |
| **Test counts** | README: 66/66 → 72/72; Sprint doc: 1,384 | Multiple stale numbers across docs | ⚠️ Cosmetic but signals drift |
| **`Projects/ACTIVE/`** | README says 8 items | 35+ items, many are completed lessons-learned | ⚠️ Moderate |
| **AI Agent RAG** | Not mentioned in manifest | Shipped Jan 2026 per status doc, has its own manifest in ACTIVE | ⚠️ Documented sideways |

---

## 1. What the docs claim

### `README.md` (the public face)
- "Phase 5.4 Complete: Advanced Analytics & Workflow Management"
- "**72/72 tests passing**" / "Real user validation on 212 notes"
- "97% reduction in main directory clutter (35+ files → 1 cleanup plan), crystal clear focus on 8 active priorities"
- CLI examples mostly use `python3 src/cli/...` and `python3 quick_demo.py` (pre-reorganization paths)
- Promotes `inneros analytics`, `inneros workflow`, `inneros enhance` as if these are real binaries

### `Projects/REFERENCE/inneros-manifest-v3.md` (2025-09-18)
- "Major foundational systems are production-ready (Phase 5 complete)"
- "Directory Organization P0+P1: production-ready with backup/rollback"
- "Fleeting Lifecycle (Phase 5.6): health, triage, promotion complete"
- "Focus now shifts to Phase 6 and system integrity issues" (multi-user + Web UI)
- "Active Priorities: Image Linking bug, Reading Intake Pipeline, Phase 6 prep"
- "Next Review: 2025-09-25" — never updated

### `Projects/ACTIVE/SPRINT-MAKE-IT-USABLE.md` (2025-12-01)
- **Explicitly acknowledges the drift** in plain language:
  > "Current State: Powerful infrastructure that sits unused — 1,384 passing tests, 30+ CLI tools, 29 automation modules, Complex documentation across 5+ locations"
  > "Target State: Simple tool you actually use — 2 commands to remember, 1 place for docs, Automation runs without intervention"
- Reports import errors in `connections_demo.py`, untested screenshot/YouTube handlers
- 4-phase plan to fix usability over 2 weeks

### `Projects/ACTIVE/PROJECT-STATUS-FEB-2026.md` (2026-02-03)
- Quietly pivots to a **new** focus: AI Agent RAG (ReAct loop, OpenAI tool-calling), Quality Scoring System, YouTube fixes
- None of this is reflected in manifest-v3

---

## 2. What reality shows (today's audit)

**Vault** (`knowledge/`):
- `Inbox/`: **174 files**, of which **124 have `status: promoted`** but were never moved — the *exact* failure mode the "production-ready" directory organizer was supposed to prevent
- `Permanent Notes/`: **15 `.bak*` files**; multiple notes with frontmatter drift (`type: permanent` paired with `status: inbox`, `tags: [fleeting, inbox]`)
- Vault root: 6 empty `Untitled*.canvas`, 4 loose PNGs, 2 `Home Note.md.bak.*`, stale `.obsidian-backup-20250805-155425/` (408K)
- Phantom dirs: `knowledge/knowledge/` (nested empty duplicate), `Users/thaddius/`, `Test-Inbox/`, `temp_workflow_diagrams/`, `perplexity_outputs_real/`, `scripts/`
- `Home Note.md` still references "broken links output.md" and 2025-07 stub work
- Tag count historically ~698, ~300 problematic (per memory)

**Repo `Projects/ACTIVE/`**:
- 35+ files including many `issue-39-...-lessons-learned.md` items that belong in `COMPLETED-2026-XX/`
- 3 overlapping "what's next" docs (`SPRINT-MAKE-IT-USABLE.md`, `PROJECT-STATUS-FEB-2026.md`, `README-ACTIVE.md`)

**Open GitHub issues**: #104 (daemon health detection broken), #18 (255 test failures in YouTube integration), #28/22 (P2 dashboard/templates), the 3 new housekeeping issues #106/#107/#108.

---

## 3. The drifts, named

### Drift 1 — "Production-ready" vs. operational reality
The directory organizer, fleeting triage CLI, and AI inbox processor are all marked **production-ready** in manifest-v3. Yet 124 stranded promoted-notes in Inbox prove they are not running automatically as part of the daily loop. Either the automation never started, or it started and silently broke (cf. issue #104). **Production-ready ≠ production-running.**

### Drift 2 — Manifest is a snapshot, not a contract
Manifest-v3 is 8 months stale and points to a future (Phase 6 multi-user/UI) that did not happen. Real work pivoted twice: first to "make it usable" (Dec 2025), then to "AI Agent RAG + Quality Scoring" (Feb 2026). Neither pivot was reflected in the canonical manifest.

### Drift 3 — Multiple sources of truth
- README points to `inneros-manifest-v3.md`
- Manifest points to `.windsurf/rules/windsurfrules-v4-concise.md`
- SPRINT-MAKE-IT-USABLE says "consolidate to `Projects/REFERENCE/START-HERE.md`" (which exists but isn't linked from README)
- `.windsurf/rules/README.md` declares its own modular ruleset as authoritative
- `PROJECT-STATUS-FEB-2026.md` describes a different roadmap than any of the above

A new contributor reading the README would land on manifest-v3, miss the Dec pivot, miss the Feb pivot, and form an outdated mental model.

### Drift 4 — README onboarding is broken
- CLI examples use pre-reorganization paths (`src/cli/`) that no longer exist at those locations
- `quick_demo.py` is referenced at repo root but lives elsewhere or was removed
- `inneros analytics` / `inneros workflow` is presented as a binary; reality is `./inneros.sh` wrapper or direct `make` targets
- Test count is wrong on multiple axes

### Drift 5 — Documentation entropy beats curation
`Projects/ACTIVE/` was reduced to 11 items per the sprint doc, but is back to 35+ — lessons-learned files have accumulated without being archived. This is a recurring pattern: cleanup happens in bursts, then drift resumes.

### Drift 6 — The "make it usable" sprint stalled mid-way
Phase 0 of SPRINT-MAKE-IT-USABLE shows ✅ COMPLETE checkboxes. Phase 1 (fix `inneros-status`, fix `inneros-up`, CLI migration) shows mostly empty checkboxes. The pivot to Quality Scoring / Agent RAG happened before the usability work finished — which is *why* automation isn't running today.

---

## 4. Root causes

1. **Manifests are aspirational artifacts, not living contracts.** They get written, then orphaned. No process forces them to track reality.
2. **Production-ready is asserted from test pass-rate, not operational telemetry.** A CLI that passes 12/12 tests but isn't wired into a daemon, or whose daemon silently dies, is not production-running.
3. **No archival discipline for `Projects/ACTIVE/`.** Files are added; nothing forces them out when they're done.
4. **README is treated as marketing copy.** It oversells phase completion and undersells operational caveats.
5. **Multiple personalities of the system** — Zettelkasten tool, AI lab, daemon-ops platform, agent runtime — pull in different doc directions.

---

## 5. Recommended corrective actions

### Immediate (this week)
- [ ] **Mark manifest-v3 as historical**; create `manifest-v4` (or just delete v3 and consolidate into a single living `Projects/REFERENCE/START-HERE.md` that is the README's only target).
- [ ] **Rewrite `README.md` §"Getting Started"** with paths that actually work today. Verify every command in the README by running it.
- [ ] **Pick one "what's next" doc**. Archive the other two. My suggestion: keep `START-HERE.md` as steady-state and `PROJECT-STATUS-<MONTH>.md` as the rolling current-sprint doc.
- [ ] **Run the P0 housekeeping** (issue #106) to bring the vault state in line with the docs' claims.

### Structural (this month)
- [ ] **Operational status page**: a single command (`make status` / `inneros-status`) that reports what's *running*, what's *backlogged*, and what's *broken*. Replace claims like "production-ready" in the manifest with links to live status output.
- [ ] **Archive discipline for `Projects/ACTIVE/`**: anything tagged with a closed issue number or `-lessons-learned` moves to `COMPLETED-<YYYY-MM>/` on a weekly cadence (already a Sprint Phase 4 idea — finish it).
- [ ] **Resume / finish SPRINT-MAKE-IT-USABLE Phase 1** before adding more capability (Agent RAG, Quality Scoring). The current order — build more on top of an unrunnable base — guarantees more drift.
- [ ] **Daemon registry coverage check** in CI: every daemon mentioned in any manifest must appear in `.automation/config/daemon_registry.yaml` and pass health detection (cf. open issue #104).

### Cultural (ongoing)
- [ ] **Define "production-ready"** in one sentence in the rules. Suggestion: *"Has automated tests, is registered as a daemon or scheduled job, and has produced output visible in the last 7 days."*
- [ ] **Quarterly manifest review** (real one, with a date check). If the "next review" date passes without an update, the manifest auto-rolls into `Projects/Archive/`.
- [ ] **README as a tested artifact**: a CI job that greps the README for command examples and tries to run their `--help`. Broken paths fail the build.

---

## 6. Honest scorecard

| Area | Grade | Note |
|---|---|---|
| Capability (code) | A− | The CLIs and automation modules exist and are well-tested |
| Operational reality | C | Capability does not equal running. Inbox state is the proof. |
| Documentation accuracy | C− | Manifests describe a system 6–12 months ago |
| Documentation discoverability | B | `Projects/REFERENCE/` exists, but the README doesn't lead there cleanly |
| Vault hygiene | D+ | Active regression vs. "production-ready" claims |
| Sprint follow-through | C | Make-It-Usable started strong, stalled, was bypassed by new work |
| Recovery path | B+ | Issues #106/#107/#108 + this analysis give a clear next move |

---

## 7. Next decision points for the owner

1. **Do you want to finish SPRINT-MAKE-IT-USABLE first, or merge it into a new sprint?** Recommend: finish it. The Agent RAG and Quality Scoring work will sit unused (same trap) until daily automation actually runs.
2. **Single source of truth — which file?** Recommend: `Projects/REFERENCE/START-HERE.md`. Delete or archive everything else that claims that crown.
3. **Manifest cadence — kill it or fix it?** Recommend: kill the standalone manifest. Replace with (a) a one-page "what is this project" in README, and (b) the rolling status doc. Manifests die from neglect; status docs survive because they're useful daily.
4. **Vault cleanup — when?** Recommend: this week. The 124 stranded inbox files are eroding trust in the entire automation story.

---

*This gap analysis is a snapshot. Re-run when the corrective actions land.*
