---
created: 2025-10-06 16:42
type: fleeting
status: inbox
visibility: private
tags: [ai-assisted, ai-assisted-note-taking, ai-assisted-writing, ai-processing, artificial-intelligence,
  automation, content-enhancement, fleeting]
quality_score: 0.85
ai_processed: '2025-10-12T20:44:02.112936'
---
```mermaid

sequenceDiagram

actor User

participant Templater

participant Bridge as TemplaterBridge

participant Queue as ProcessingQueue

participant Processor as YouTubeProcessor

participant Enhancer as NoteEnhancer

participant File as Note File

participant Ollama as Ollama LLM

User->>Templater: Enter YouTube URL

Templater->>Templater: Fetch metadata (oEmbed)

User->>Templater: Enter "Why saving this"

Templater->>File: Create note with metadata

Note over Templater,File: ✅ Phase 1: Note Created (3-5 seconds)

Templater->>Bridge: trigger_processing(note_path, url)

Bridge->>Queue: add_to_queue(note_path, video_id)

Queue-->>Bridge: job_id, position in queue

Bridge-->>Templater: trigger_id

Templater->>User: Show notification<br/>"Processing in background..."

Note over User,Templater: User continues working

Queue->>Processor: process_next_job()

Processor->>Processor: Fetch transcript (YouTube API)

Processor->>Ollama: Extract quotes with context

Note over Processor,Ollama: ⏱️ Phase 2: AI Processing (30-60s)

Ollama-->>Processor: 7 extracted quotes

Processor->>Enhancer: enhance_note(quotes_data)

Enhancer->>File: Read current content

File-->>Enhancer: Note structure

Enhancer->>Enhancer: Parse & insert quotes

Enhancer->>File: Write enhanced content

Enhancer->>File: Update frontmatter

Note over Enhancer,File: ✅ Phase 3: Enhancement (1-2s)

Enhancer-->>Processor: Enhancement complete

Processor-->>Queue: update_status(completed)

Queue-->>Bridge: job_completed(trigger_id)

Bridge->>User: Show notification<br/>"Note enhanced with 7 quotes"

User->>File: Open enhanced note

File-->>User: Complete note with AI quotes

Note over User,File: ✅ Total Time: 35-70 seconds

```
<!--
NOTE: This file uses a static date for validation. For new notes, use:
created: 2025-10-06 16:42
-->

## Thought  
Write the idea that just popped into your head.

## Context  
Where did this come from? (Article, conversation, reflection, etc.)

## Next Step  
- [ ] Convert to permanent note?
