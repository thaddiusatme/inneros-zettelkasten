ADR 10
Daily Content Pull Pipeline for PKM using GPT OSS 20B
Status: Accepted
Date: 2025 11 29
Author: Thaddius (InnerOS)
Context: PKM, LLM integration, daily note review
Related ADRs: ADR 1 Seed Summaries, ADR 7 Summarization Limits, ADR 9 LLM Token Discipline

1. Context

InnerOS is evolving into a daily ideation engine that reviews notes created during the day and produces content prompts, idea combinations, and topic suggestions. This workflow must operate reliably on a local GPT OSS 20B model, which has a practical working context of about 12k to 14k tokens per call.

The previous design tried to review many full notes in a single prompt. This caused unstable behavior, quality collapse, and token budget violations.

We need a new design that:
- Lets the owner write 3 to 10 notes per day
- Reviews all of them each daily iteration
- Produces usable content prompts grounded in the notes
- Never exceeds the model’s safe context band
- Supports long term PKM practices like traceability, reversibility, and append only records

2. Decision

We adopt a batch based daily content pull pipeline that separates the iteration from individual LLM calls and uses stored per note representations for safe and repeatable processing.

Key decisions
- Daily iteration = several small LLM calls, not one large call.
  - The once per day review is a pipeline, not a single monolithic prompt.
- Each note maintains a compact "seed representation".
  - Includes:
    - Title
    - Tags
    - seed_summary (3 to 5 bullets)
    - Optional content_hooks
    - last_reviewed_at timestamp
  - Full note bodies are not used in the wide pass.
    - They are only used for narrow, deep tasks.
- Daily review is performed in three stages:
  - Stage 1: Summarize and update seed_summary if missing or stale
  - Stage 2: Batch review summaries to produce hooks per note
  - Stage 3: Combine all summaries and hooks into a "Content Pull" synthesis note
- Token budgeting is explicit and enforced.
  - Instructions: about 1.5k
  - Seed summaries per batch: about 4k to 6k
  - Output: about 1k
  - Total target: 6.5k to 8.5k tokens per call
- Batching uses token estimation, not fixed count.
  - Notes are grouped based on estimated summary length to avoid exceeding the safe band.
- Daily content output is stored as a first class note.
  - It includes:
    - Date
    - Idea list
    - Which notes each idea draws from
  - This structure keeps the PKM system reversible, interpretable, and evolvable.

3. Rationale

3.1 Alignment with LLM best practices

LLMs perform best with short, consistent representations rather than many full bodies in one call.

A mid sized model like 20B benefits from proper token headroom and does not degrade when kept inside a smaller band.

A pipeline of several short calls is significantly more stable than one very long call.

3.2 Alignment with PKM principles

Notes remain the source of truth.

seed_summary and content_hooks are derived fields that can be regenerated at any time.

Daily content pulls become artifacts for reflection and content creation.

Linking content ideas to their source notes preserves context across the system.

3.3 Operational reliability

Separate stages allow retries and error recovery.

Summaries can be updated incrementally instead of recomputed from scratch daily.

Batching helps avoid silent truncation or unstable outputs.

Logging and token estimation allow safe evolution of prompts.

4. Architecture Overview

Stage 0: Candidate Selection

Select all notes updated or created within the last day.

Stage 1: Summary Assurance

For each candidate note:
- If seed_summary is missing or stale, generate it with a short call.
- Save updated summary.

Stage 2: Batch Review

Group notes into batches where total summary tokens stay under about 5k.

For each batch:
- Provide summaries to the model.
- Get:
  - Refined summaries
  - Content hooks per note
- Write these to the notes along with last_reviewed_at.

Stage 3: Blender Synthesis

Collect all summaries and hooks from the day and generate a:
- Dated "Daily Content Pull" note
- Containing clustered ideas, combinations across notes, and ready to use prompts

5. Consequences

Benefits
- All daily notes are reviewed each iteration.
- Output ideas are consistent and grounded.
- Safe for 20B running locally.
- Easy to debug and easy to extend.
- Maintains PKM integrity and traceability.
- Scales with note volume without requiring a more expensive model.

Drawbacks
- A multi step job is slightly more complex to implement than one giant prompt.
- Requires token estimation utilities.
- Summaries may need occasional refreshes when prompts evolve.

Risks
- If seed_summary becomes too abstract, content quality may degrade.
- If batching is not enforced correctly, token overflow risks return.
- Requires careful prompt editing discipline.

6. Future Work

- Add RAG retrieval so new notes link to relevant older notes automatically
- Track idea usage to refine what types of content suggestions are most effective
- Introduce quality metrics for summaries and hooks
- Consider offloading deep dives to a larger model when needed
