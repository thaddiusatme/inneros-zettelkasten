# Lessons Learned — 2026-05-10 — ChatGPT Prompt Template Routing Issue

## What we shipped

We created GitHub issue #112, `[FEATURE] Route ChatGPT prompt template output to Prompts folder`, to track updating `knowledge/Templates/Utility/chatgpt-prompt.md` so Obsidian Templater-generated prompt files move to `knowledge/Prompts` instead of `knowledge/Inbox`. The issue documents the current implementation line `const target = "Inbox/${fname}";`, the desired destination `Prompts/${fname}`, related documentation in `README.md`, and the mirrored fixture at `development/tests/fixtures/templates/Utility/chatgpt-prompt.md`.

## What went well

- Using `code_search` first quickly found the authoritative template, the mirrored fixture, and the README section documenting the current `Inbox/prompt-YYYYMMDD-HHmm.md` behavior.
- Creating a GitHub issue before changing the template preserved the requested work as a tracked feature with acceptance criteria instead of making an unplanned code change.
- The issue body included concrete implementation targets: `knowledge/Templates/Utility/chatgpt-prompt.md`, `README.md`, and `development/tests/fixtures/templates/Utility/chatgpt-prompt.md`.

## What surprised us / went wrong

- The requested project documentation paths are not present in this repository: `docs/architecture/PROJECT_PLAN.md`, `docs/architecture/Project-Manifest.txt`, `docs/contracts/`, `docs/digests/`, and `docs/decisions/`. The repository currently uses nearby but different structures such as `docs/ARCHITECTURE.md`, `docs/adr/`, and `Projects/ACTIVE/` / `Projects/REFERENCE/`.
- The template behavior is duplicated between the production vault template and a test fixture. Any implementation must update both `knowledge/Templates/Utility/chatgpt-prompt.md` and `development/tests/fixtures/templates/Utility/chatgpt-prompt.md` or explicitly document why they diverge.

## What to do differently next time

- Before generating iteration closeout docs, verify the requested documentation paths with `find_by_name` so missing paths can be surfaced before edits begin.
- When changing any Obsidian template under `knowledge/Templates/`, search `development/tests/fixtures/templates/` for a mirrored fixture and update the fixture in the same iteration.
- For template-routing changes, include a runnable grep-based verification command in the issue or PR so reviewers can confirm old destination strings were removed.

## Technical debt or risks introduced

- GitHub issue #112 is created, but the actual template behavior has not been implemented yet. Proper fix: update `knowledge/Templates/Utility/chatgpt-prompt.md`, `development/tests/fixtures/templates/Utility/chatgpt-prompt.md`, and the README template section, then validate no stale `Inbox/${fname}` or `Inbox/prompt-YYYYMMDD-HHmm.md` references remain.
- README.md still documents the current `Inbox/prompt-YYYYMMDD-HHmm.md` behavior until issue #112 is implemented. Proper fix: update that line only when the template target actually changes to `Prompts/${fname}`.
