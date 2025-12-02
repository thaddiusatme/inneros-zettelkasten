# GPT-OSS-20B Note Feedback Engine Manifest

**Status**: In Progress

**Date**: 2025-12-01 (Updated: 2025-12-02)

**Owner**: InnerOS (Thaddius)

**Related**: ADR-010 Daily Content Pull Pipeline (GPT OSS 20B), AIEnhancementManager, `inneros enhance`, assistant automation suite

---

## 1. Context

- InnerOS already provides:
  - `inneros enhance` for per-note AI feedback using a local model via Ollama (e.g. `llama3:latest`).
  - `AIEnhancementManager` with 3-tier fallback (local LLM → external API → degraded).
  - ADR-010: a daily content pull pipeline explicitly designed around GPT OSS 20B for batch content ideation.
- Desired future state:
  - The same "quality score + suggestions + missing elements" experience you see today, but powered by **GPT-OSS-20B** when deeper reasoning is valuable.
  - A reusable, automation-friendly feedback engine that your AI assistant can call as part of its broader feature suite (not only via manual CLI runs).

---

## 1.1 Progress (Updated 2025-12-02)

### ✅ Completed

| Component | Description | Commit |
|-----------|-------------|--------|
| ADR-010 Stage 0 | `select_daily_pull_candidates()` - 24h recency filter | `a813f139` |
| Token Estimator | `src/utils/token_estimation.py` - shared ADR-11 estimator | `a813f139` |
| JSONL Logging | `log_daily_pull_session()` with `pipeline: "daily-pull"` | `a813f139` |
| TDD Test Suite | 15 tests in `test_adr010_daily_pull_stage0_tdd_1.py` | `a813f139` |

### 🔄 In Progress

- Phase 0: Hardware/Ollama validation for GPT-OSS-20B

### 📋 Next Steps

1. Validate GPT-OSS-20B model loading in Ollama
2. Begin Phase 1: `NoteFeedbackV1` schema implementation
3. Wire feedback adapter to existing `AIEnhancementManager`

---

## 2. Problem Statement

- Current `inneros enhance` is optimized for:
  - Quick, single-note enhancement with a smaller local model.
  - Lightweight tagging and suggestions with modest reasoning depth.
- Gaps for the assistant use case:
  - Some notes (e.g. strategy, economics, multi-step reasoning claims like "AI will solve the US debt crisis") deserve **richer, more reliable feedback** than smaller models consistently provide.
  - There is no explicit, configurable **"use GPT-OSS-20B for feedback"** path:
    - No shared schema for structured feedback objects.
    - No way for the assistant automation suite to request deep reasoning feedback vs cheap fast feedback.
    - No integration yet with ADR-010’s note representations and token discipline.

---

## 3. Goals

### G1 – GPT-20B feedback mode for notes

Provide a GPT-OSS-20B-powered feedback path that:

- Accepts a single note (typically 1–3k tokens, including YAML frontmatter and body).
- Produces a structured feedback object with at least:
  - `quality_score` (0.0–1.0).
  - Dimension scores (clarity, structure, linkage, examples, depth).
  - `missing_elements` (e.g. "examples", "links", "mechanism"), each with a short reason.
  - `suggestions` with concrete, actionable improvements.
- Is invokable from:
  - `inneros enhance` (terminal UX first).
  - The assistant’s automation suite (later phases).

### G2 – Reusable feedback schema (NoteFeedbackV1)

- Define a JSON-serializable schema, tentatively `NoteFeedbackV1`, with fields such as:
  - `quality_score: float`
  - `dimensions: { clarity, structure, links, examples, depth, voice, ... }`
  - `missing_elements: List[{ id, label, reason }]`
  - `suggestions: List[{ kind, description, example_diff? }]`
  - `model: { name, tier, reasoning_effort }`
- Make this schema:
  - Persistent in logs (JSONL under `development/logs/`).
  - Easy to render in terminal (today).
  - Extendable to in-note storage later (frontmatter or inline section).

### G3 – Safe integration with existing stack

- Integrate GPT-OSS-20B feedback with:
  - `AIEnhancementManager` (as a feedback method using a configurable model backend).
  - `WorkflowManager` / CLI (`inneros enhance`) via new flags or modes.
  - The assistant’s future automation flows (e.g. nightly review of high-impact notes).
- Preserve safety and reliability principles:
  - 3-tier fallback remains intact (20B is a new tier/config, not a hard dependency).
  - Config controls which model is used and when.
  - Clear metrics for latency and error handling.

### G4 – Reasonable local operations

- Target environment:
  - Single machine with at least **16 GB VRAM** capable of running GPT-OSS-20B locally.
- Performance/usage assumptions:
  - Multiple **short analysis calls per day**, not continuous heavy generation.
  - Typical note (<1.5k tokens): target **<1s** wall-clock per GPT-20B call.
  - Heavy notes (up to ~3k tokens): target **<2s** per call.

---

## 4. Non-Goals (v1)

- Not replacing all AI usage with GPT-OSS-20B.
- Not focused on long-form generation (posts, essays) – this project is about **analysis and feedback**, not drafting.
- No fine-tuning of GPT-OSS-20B in this iteration (prompt-only usage; fine-tuning is a separate effort).
- No redesign of ADR-010 batching/token estimation – we align conceptually but do not reimplement that work here.
- No immediate in-note mutation (frontmatter/body writes); initial output surface is **terminal + logs only**.

---

## 5. Design Overview

### 5.1 Model and serving choice

- **Primary model**: `gpt-oss-20b` (OpenAI GPT-OSS-20B; Apache 2.0; MoE ~3.6B active, 128k context).
- **Initial serving strategy (Phase 1)**:
  - Use **Ollama** to host GPT-OSS-20B locally, reusing existing `OllamaClient` and local LLM integration patterns.
  - This minimizes new infrastructure and keeps the integration surface small.
- **Future serving option (Phase 2)**:
  - Optionally stand up a dedicated **vLLM** service for GPT-OSS-20B when/if:
    - Batch analysis of many notes becomes common.
    - More fine-grained performance tuning is desired.

### 5.2 Integration points

- **AIEnhancementManager**:
  - Add a GPT-20B-backed feedback method, e.g. `generate_feedback_for_note(note_path, model_config)`.
  - Use this to produce `NoteFeedbackV1` objects from note content.
- **inneros CLI**:
  - Extend `inneros enhance` with:
    - `--feedback-only` (do not modify tags/summary; just print feedback).
    - `--feedback-model {default,gpt-oss-20b}` to select backend.
  - Presentation: keep the existing style (quality score, suggestions, missing elements) but driven by GPT-20B when requested.
- **Assistant automation suite**:
  - Expose a Python-level function or small CLI wrapper the assistant can call as part of automated workflows.
  - Initial usage: on-demand, scripted or scheduled calls against specific notes; later: integration with daily review pipelines.

### 5.3 Prompt and reasoning strategy

- Prompts favor **analysis over generation**:
  - System prompt: "You are a PKM note editor. Evaluate the note according to specific dimensions and output strict JSON matching NoteFeedbackV1."
  - User content: full note text (optional: frontmatter + body), plus explicit instructions for dimensions and missing elements.
- Reasoning effort:
  - Default: medium reasoning effort for reliable multi-dimensional feedback.
  - Configurable: future ability to lower reasoning for fast/cheap mode or increase for particularly complex notes.

---

## 6. Phased Plan (TDD-Oriented)

### Phase 0 – Alignment & scaffolding

- Confirm hardware and Ollama support for GPT-OSS-20B in the InnerOS dev environment.
- Add a short design note linking this manifest to ADR-010 (shared use of GPT-20B and token discipline).

**Acceptance:**
- Documented decision: "GPT-OSS-20B served via Ollama for feedback engine v1".
- Basic manual test that Ollama can load and respond with GPT-OSS-20B on a toy prompt.

---

### Phase 1 – Feedback schema and adapter (backend-agnostic)

- Introduce `NoteFeedbackV1` type (dataclass or TypedDict) with the fields in G2.
- Implement a backend-agnostic adapter:
  - `NoteFeedbackAdapter` that can:
    - Serialize/deserialize `NoteFeedbackV1` to/from JSON.
    - Render a human-readable version (for terminal output).
- Testing:
  - 100% tests for:
    - Required vs optional fields.
    - JSON round-trip.
    - Rendering logic independent of any real model.

**Acceptance:**
- New unit test module (e.g. `test_note_feedback_schema.py`) with all tests passing.
- No dependency on GPT-20B yet – pure schema + formatting.

---

### Phase 2 – GPT-20B integration via Ollama (local prototype)

- Extend `OllamaClient` or add a small wrapper method to:
  - Call GPT-OSS-20B with the analysis prompt.
  - Parse the JSON response into `NoteFeedbackV1`.
- Integrate this into `AIEnhancementManager` as a new method:
  - `generate_feedback_for_note(note_path, model="gpt-oss-20b", fast=False, dry_run=False)`.
- Add tests using:
  - Mocked Ollama responses for stability.
  - Optional integration test flagged/marked for real GPT-20B runs on a dev machine.

**Acceptance:**
- Unit tests pass with mocks (no real GPT-20B required).
- Manual run on 1–3 real notes (including a complex reasoning note) shows:
  - Reasonable `quality_score`.
  - Concrete `missing_elements`.
  - Actionable `suggestions`.
- Latency meets the target envelope on dev hardware.

---

### Phase 3 – CLI and assistant integration (terminal-first)

- Extend `inneros enhance` to expose GPT-20B feedback mode:
  - Add `--feedback-only` and `--feedback-model gpt-oss-20b`.
  - Wire these flags to the new `generate_feedback_for_note` method.
- Implement terminal rendering of `NoteFeedbackV1` that:
  - Mirrors the existing style you saw (quality score, suggestions, missing elements).
  - Uses clear, compact formatting for quick scanning.
- Define a thin Python function/CLI that the assistant can call programmatically as part of its feature suite.

**Acceptance:**
- New CLI tests covering:
  - Flag parsing.
  - Output formatting for success and error paths.
- You can run a single command against any note and see GPT-20B feedback in the terminal.
- Assistant can invoke the same path in an automated workflow (e.g. as part of a scripted daily review), even if still triggered manually.

---

### Phase 4 – In-note feedback storage (future iteration)

- Extend the system to optionally persist feedback into the note itself:
  - Option A: append a `feedback:` block in YAML frontmatter.
  - Option B: append a `## AI Feedback (GPT-OSS-20B)` section at the bottom of the note.
- Ensure all note writes respect existing safety systems:
  - Backups.
  - Dry-run preview.
  - Compatibility with directory organization and link integrity guarantees.

**Acceptance (future):**
- Opt-in flag (e.g. `--apply-feedback`) that writes feedback into the note.
- Tests ensuring repeated runs update/merge feedback safely without corrupting frontmatter.

---

## 7. Open Questions / Future Extensions

- When (and where) to introduce vLLM as a dedicated GPT-20B backend once Ollama-based v1 is stable.
- How to share `NoteFeedbackV1` signals with ADR-010’s daily content pull:
  - E.g. use `quality_score` + `depth` + `links` to prioritize which notes become content seeds.
- Whether to define additional dimensions specifically for assistant behavior (e.g. "promptability" or "idea-density").

This manifest defines a scoped, TDD-friendly path to add GPT-OSS-20B powered note feedback into InnerOS, starting with **terminal-only UX** and evolving toward **assistant-driven automation** and optional in-note persistence.
