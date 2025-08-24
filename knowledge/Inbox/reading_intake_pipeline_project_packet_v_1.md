---
created: '2025-08-14'
type: permanent
status: inbox
tags: [analytics, automation, cli-integration, import-adapters, intake-pipeline, intake-processing,
  migration-rollout, normalization]
ai_processed: '2025-08-23T14:20:44.757658'
---

# Document 1: Project Charter and Success Metrics

## Problem Statement
Your saved articles, bookmarks, and social posts are scattered across apps. Processing them into Fleeting and Literature notes is inconsistent and time consuming. We will standardize intake and transform saved items into Obsidian notes that flow into weekly review and Permanent Notes.

## Goals
- Single intake for all reading sources
- Fast triage that generates Fleeting notes with minimal friction
- Clear upgrade path from Fleeting to Literature to Permanent notes
- Automatic linking to MOCs and visibility in the Home Note
- Local first and privacy by default

## Non Goals
- Full content scraping of paywalled sources
- Building a full feed reader
- Public sharing or multi user collaboration in this phase

## Users and Stakeholders
- Primary user: You
- Secondary stakeholders: Future collaborators or clients who adopt the system

## Scope
- Normalize saved items into a common schema
- Create Fleeting notes automatically in knowledge/Inbox
- Provide an upgrade path to Literature notes with claims and quotes
- Weekly review automation promotes candidates to Permanent Notes and links to MOCs

## Constraints
- Obsidian vault structure must remain intact
- All processing runs locally

## Dependencies
- Obsidian and current vault
- Python CLI utilities for Inbox processing and weekly review

## Assumptions
- You will run the import step prior to daily triage
- You will maintain basic tagging discipline for topics

## Risks and Mitigations
- Import variance across platforms. Mitigation: small adapters that map to one schema.
- Note sprawl. Mitigation: quality bar and weekly pruning.
- Broken links. Mitigation: unit tests for link creation and a monthly link check script.

## Success Metrics
- Intake to Fleeting conversion time per item under 30 seconds
- 70 percent of Literature notes contain at least two links and one claim
- At least five Permanent Notes promoted per week during the first month
- Error rate under 1 percent on importer jobs

## Milestones and Dates
- Sprint 0 setup: Aug 11 to Aug 15, 2025
- MVP intake and Fleeting notes: Aug 18, 2025
- Literature upgrade flow: Aug 22, 2025
- Weekly review promotion and linking: Aug 29, 2025

## Definitions
- Definition of Ready: User story has a use case, acceptance criteria, and test notes
- Definition of Done: Story passes tests, updates docs and templates, and is visible in Obsidian

---

# Document 2: Product Requirements Document

## Product Overview
A reading intake pipeline that transforms saved items into standardized Obsidian notes, feeding daily triage and weekly review.

## Personas and Jobs to be Done
- Creator researcher: “When I save an article or post, I want it to appear in Obsidian with just enough context so I can decide if it deserves deeper processing.”

## Epics, User Stories, Acceptance Criteria

### Epic A: Intake and Normalization
1. As a user, I can import a CSV or JSON of saved items so each row becomes a Fleeting note in knowledge/Inbox.
   - Acceptance: For a sample file with 50 items, 50 notes are created with title, url, source, saved_at, type, topics.
2. As a user, I can tag imported items with topics so I can filter during triage.
   - Acceptance: Topics are preserved as YAML arrays and are searchable in Obsidian.

### Epic B: Fleeting Notes and Triage
1. As a user, I can open the Inbox and see one Fleeting note per saved item with a 3 bullet prompt for why it matters.
   - Acceptance: Notes have front matter, 3 bullet scaffold, and a checkbox to upgrade or discard.
2. As a user, I can discard low value items quickly.
   - Acceptance: A CLI flag archives selected notes into knowledge/Archive.

### Epic C: Literature Upgrade
1. As a user, I can convert a Fleeting note to a Literature note template that captures claims, quotes, and my take.
   - Acceptance: Upgrade preserves source metadata and inserts sections for claims, quotes with page or timestamp, and connections.
2. As a user, I can add at least two links to related notes or MOCs.
   - Acceptance: CLI validates presence of two wiki links before status moves from draft to ready.

### Epic D: Weekly Review and Promotion
1. As a user, I can run a weekly review that proposes Literature notes to promote to Permanent Notes.
   - Acceptance: The weekly review lists candidates that meet quality thresholds and offers a one click promotion that moves files to knowledge/Permanent Notes and updates links_out.
2. As a user, I can see recent promotions in my Home Note and relevant MOCs.
   - Acceptance: Home Note has a Recent Promotions section updated in the run. Each promoted note is added to at least one MOC.

### Epic E: Import Adapters
1. Bookmarks HTML import
2. Threads or Twitter bookmarks JSON import
3. YouTube playlist import using exported list
4. RSS or newsletter list import via CSV export
   - Acceptance: Each adapter maps fields to the common schema and passes unit tests with sample fixtures.

## Non Functional Requirements
- Local first. No network calls required for processing.
- Import of 200 items completes in under 60 seconds on your hardware.
- Templates render correctly with your Obsidian configuration.

## Initial Backlog
- A1: Common schema and validation
- A2: CSV and JSON parser
- B1: Fleeting note generator
- C1: Literature upgrade script
- D1: Weekly review integration with promotions
- E1 to E4: Import adapters
- QA1: Unit tests and link checker

---

# Document 3: Technical Implementation Plan

## Architecture
- Importer adapters parse external exports into a normalized record
- Normalizer writes Markdown files using the Fleeting template into knowledge/Inbox
- Upgrade script transforms Fleeting to Literature notes in place
- Weekly review script ranks and promotes candidates to Permanent Notes and updates Home Note and MOCs

## Data Schema
```json
{
  "url": "https://example.com/post",
  "title": "Post title",
  "source": "Website or app",
  "saved_at": "2025-08-09T10:15:00Z",
  "published_at": "2025-08-07",
  "type": "article",
  "topics": ["ai", "workflows"],
  "author": "Author Name",
  "duration": 540,
  "summary_clip": "Optional excerpt",
  "collection": "Reading List A"
}
```

## File Naming and Routing
- Fleeting: FN {date} {slug}.md
- Literature: LN {author_or_source} - {slug}.md
- Permanent: PN {concept}.md
- Routing: New notes to knowledge/Inbox. Archive low value notes to knowledge/Archive.

## Templates
### Fleeting front matter
```markdown
---
note_type: fleeting
status: inbox
source:
  url: {{url}}
  title: {{title}}
  author: {{author}}
  published_at: {{published_at}}
captured_at: {{date:YYYY-MM-DD}}
topics: [{{topics}}]
visibility: private
---
```

### Literature front matter
```markdown
---
note_type: literature
status: draft
source:
  url: {{url}}
  title: {{title}}
  author: {{author}}
  published_at: {{published_at}}
captured_at: {{date:YYYY-MM-DD}}
topics: [{{topics}}]
links_out: []
claims: []
visibility: private
---
```

## CLI Integration
- Inbox processing: python3 ../development/src/cli/workflow_demo.py . --process-inbox
- Weekly review: python3 ../development/src/cli/workflow_demo.py . --weekly-review
- Analytics: python3 ../development/src/cli/analytics_demo.py . --interactive

## Testing Plan
- Unit tests for schema validation and adapter mappings
- Golden file tests for Fleeting and Literature templates
- Performance test: 200 item import under 60 seconds
- Link integrity test: verify at least two links for promoted notes and update to MOCs

## Observability and Metrics
- Log import counts, failures, and processing duration
- Emit a simple CSV summary for each run to support analytics_demo.py

## Migration and Rollout
- Create Templates in knowledge/Templates
- Dry run import with 20 sample items
- Enable Inbox processing in daily routine
- Schedule weekly review on Fridays

## Risks and Rollbacks
- If template changes break Obsidian rendering, revert to last known good templates
- If import creates bad files, move generated notes to Archive and reimport after fix

## Open Questions
- Which importer to prioritize first
- Minimum quality score for promotion to Permanent Notes

