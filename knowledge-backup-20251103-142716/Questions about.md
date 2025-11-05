Cadence and periods

- What is your sprint length (1 or 2 weeks)? 
  lets do 1 week sprints, so weekly and sprints are probably goingt o have overlapping points
- When do sprints start/end (day/time, timezone)?
  Lets say a Sprint ends on a Tuesday and Starts on a Wednesday
- When should weekly reviews run (e.g., Sunday evening, Monday morning)?
  Sun-Mon
- Do you want daily notes created every day or only on workdays?
  everyday.

Structure and locations

- Preferred directories?
    - Daily: 
        
        ```
        knowledge/Reviews/Daily/
        ```
        
    - Weekly: 
        
        ```
        knowledge/Reviews/Weekly/
        ```
        
    - Sprint: 
        
        ```
        knowledge/Reviews/Sprints/
        ```
        
- Keep sprint “Review” and “Retrospective” as separate notes or a combined single doc?
  lets make them seperate BUT the workflow to be the same

Naming and IDs

- File/title conventions:
    - Daily: 
        
        ```
        daily-YYYY-MM-DD.md
        ```
        
    - Weekly: 
        
        ```
        weekly-YYYY-Www.md
        ```
        
         (ISO week)
    - Sprint: 
        
        ```
        sprint-YYYY-Www.md
        ```
        
         or date-range?
- Align sprint IDs to Phase (e.g., Phase 5.5.6) or calendar (ISO weeks)?
  SPrint IDs are cool, lets go off of sequential
- OK to use emoji in titles but ASCII-only filenames?
  yes

YAML schema (per type)

- Daily: fields like 
    
    date, 
    
    ```
    focus
    ```
    
    , 
    
    ```
    wins
    ```
    
    , 
    
    ```
    blockers
    ```
    
    , 
    
    ```
    next
    ```
    
    , 
    
    ```
    links_added
    ```
    
    ?
- Weekly: 
    
    ```
    week_id
    ```
    
    , 
    
    ```
    period_start/end
    ```
    
    , 
    
    ```
    highlights
    ```
    
    , 
    
    metrics, 
    
    ```
    orphans_before/after
    ```
    
    , 
    
    ```
    bridges_created
    ```
    
    , 
    
    ```
    next_week_goals
    ```
    
    ?
- Sprint Review: 
    
    ```
    sprint_id
    ```
    
    , 
    
    ```
    goals
    ```
    
    , 
    
    ```
    outcomes
    ```
    
    , 
    
    ```
    deliverables
    ```
    
    , 
    
    ```
    evidence/links
    ```
    
    ?
- Sprint Retro: 
    
    ```
    went_well
    ```
    
    , 
    
    ```
    to_improve
    ```
    
    , 
    
    ```
    risks
    ```
    
    , 
    
    ```
    experiments
    ```
    
    , 
    
    ```
    actions_owner_due
    ```
    
    ?
- Any required tags (e.g., 
    
    ```
    type: daily|weekly|sprint-review|retro
    ```
    
    ) and status lifecycle?

Automation and CLI

- Do you want commands to auto-generate templates and prefill metrics?
    - ```
        --daily-review
        ```
        
        , 
        
        ```
        --weekly-review
        ```
        
        , 
        
        ```
        --sprint-review
        ```
        
        , 
        
        ```
        --sprint-retro
        ```
        
- Should we auto-create the next period’s note on a schedule, or on-demand only?
- Should CLI open the created note in your editor and commit to git?

Metrics to include

- Pull from enhanced metrics: total notes, orphaned count, stale, avg links/note.
- Add connectivity deltas (orphans reduced vs last period), bridges created, MOCs updated?
- Any additional KPIs (time spent, tasks completed, shipped features)?

Linking rules

- Where should these notes link to by default (MOCs: Projects, AI & Prompting, Career & Entrepreneurship; SOPs; Phase/Project pages)?
  I think they should be linked if their subject/theme relates, not every one should be linked
- Should daily/weekly auto-embed a “See also” section for newly linked notes?
  yes!

Scope/exclusions

- Should Content Pipeline/Idea Backlog remain excluded from weekly/sprint metrics, or included in separate sections?
  i think referencing them will be important as a part of our weekly 'matienence' keeping the lights on work
- Any sensitive areas to exclude from public summaries?
  nope

Templates and UX

- Want me to create templates for all four types with checklists and minimal sections?
  sure
- Tone/style: keep the same minimalist, calm urgency aesthetic?
  same

Governance and archival

- Where do action items from weekly/sprint retro get tracked long-term (stay in note, or sync to 
    
    Projects/project-todo-v2.md)?
- Archival policy: roll up monthly/quarterly summaries? Public-facing summary needed?
  naw

---
Below is the feedbakc on the fields from a person familiar wtih my org

---
Awesome. Here is a tight, MVP-friendly setup you can drop into your workflow today. I am leaning toward the smallest set that still gives you clear visibility across Pharmacy Scraper, content work, and coaching tasks.

# Core principles for this MVP

- Fewer fields, filled daily. Add depth later.
    
- ISO dates and stable IDs for easy querying.
    
- One status field per note type.
    
- Evidence links where it matters, not everywhere.
    

# Recommended fields and notes

## Daily note

**Purpose**: plan focus, capture progress, unblock tomorrow.

- `type`: daily
    
- `date`: YYYY-MM-DD
    
- `focus`: 1 to 3 items only
    
- `wins`: quick bullets
    
- `blockers`: include owner or dependency if known
    
- `next`: what you will start next working session
    
- `links_added`: list of URLs or note IDs you created or touched
    
- `status`: open or closed
    

**MVP tip**: cap `focus` at 3 to enforce priority.

## Weekly review

**Purpose**: roll up outcomes and leading indicators.

- `type`: weekly
    
- `week_id`: YYYY-Www (example 2025-W33)
    
- `period_start` and `period_end`: YYYY-MM-DD
    
- `highlights`: bullets
    
- `metrics`: keep to 3 to 5. Suggested starter set:
    
    - `deep_work_hours`
        
    - `content_published` (count)
        
    - `leads_created` or `intros_booked`
        
    - `pipeline_runs` for Pharmacy Scraper
        
    - `defects_found` or `incidents`
        
- `orphans_before` and `orphans_after`: count of notes without links in your ZK
    
- `bridges_created`: count of new links between notes
    
- `next_week_goals`: 3 items or fewer
    
- `status`: drafted or published
    

**MVP tip**: compute `orphans_*` weekly only.

## Sprint review

**Purpose**: accountability on sprint promise vs delivery.

- `type`: sprint-review
    
- `sprint_id`: short slug, example S-2025-08A
    
- `goals`: the sprint goal as one sentence
    
- `outcomes`: what actually happened in bullets
    
- `deliverables`: list of artifacts shipped
    
- `evidence_links`: PRs, issues, docs, screenshots
    
- `scope_change`: optional short list if anything major shifted
    
- `status`: complete
    

**MVP tip**: if an item has no evidence link, call it out.

## Sprint retrospective

**Purpose**: learn quickly and create one or two process bets.

- `type`: retro
    
- `sprint_id`
    
- `went_well`: bullets
    
- `to_improve`: bullets
    
- `risks`: top 1 to 3
    
- `experiments`: small trials to run next sprint
    
- `actions_owner_due`: table-like bullets, example `Add libpostal canary | You | 2025-08-15`
    
- `status`: planned or logged
    

**MVP tip**: do not carry more than 3 experiments at once.

# Status lifecycle

- Daily: open then closed same day
    
- Weekly: drafted then published on completion
    
- Sprint review: complete only
    
- Retro: planned when drafted during review, logged after the meeting
    

# Example YAML templates

**Daily**

```yaml
type: daily
date: 2025-08-13
focus:
  - Finalize normalization tests for phone and address
  - Record 1 newsletter clip
  - Prep Mustapha outreach list v1
wins:
  - Fixed flaky dedup integration test
blockers:
  - Waiting on API key increase request to Apify
next:
  - Write failing tests for usaddress and phonenumbers
links_added:
  - pr: https://github.com/.../pull/123
  - note: zk://pharmacy-normalization-plan
status: closed
```

**Weekly**

```yaml
type: weekly
week_id: 2025-W33
period_start: 2025-08-11
period_end: 2025-08-17
highlights:
  - Pharmacy Scraper v2.1.0 classification stable on WA and OR
  - Shot two short-form videos for AI Humble Servant
metrics:
  deep_work_hours: 14
  content_published: 3
  leads_created: 4
  pipeline_runs: 6
  defects_found: 1
orphans_before: 18
orphans_after: 12
bridges_created: 9
next_week_goals:
  - Finish robust normalization tests
  - Deliver sample prospect list to Mustapha
  - Publish newsletter issue
status: published
```

**Sprint review**

```yaml
type: sprint-review
sprint_id: S-2025-08A
goals: Ship stable normalization and produce first buyer list sample
outcomes:
  - Address normalization behind flag with tests
  - First pass of buyer list for PNW groceries
deliverables:
  - docs/SCHEMA.md updates
  - csv/buyer_list_v1.csv
evidence_links:
  - https://github.com/.../pull/130
  - zk://mustapha-buyer-list-notes
scope_change:
  - Deferred international parsing to next sprint
status: complete
```

**Sprint retro**

```yaml
type: retro
sprint_id: S-2025-08A
went_well:
  - Clear slice of scope
  - Fast PR reviews
to_improve:
  - Too much context switching on content days
risks:
  - Budget overrun on API if retries spike
experiments:
  - Set WIP limit of 2 for daily focus this sprint
  - Add budget canary that alerts at 60 percent of weekly cap
actions_owner_due:
  - Add WIP limit to daily template | You | 2025-08-14
  - Create budget alert script | You | 2025-08-15
status: logged
```

# Tags and minimal taxonomy

- Required `type` as shown above
    
- Optional `area`: product, content, ops
    
- Optional `project`: pharmacy-scraper, ai-humble-servant, client-clarity-compass
    

# Automation and CLI recommendations

**Commands**

- `notes new --daily-review` creates a daily file from template
    
- `notes new --weekly-review` creates a weekly file with week_id prefilled
    
- `notes new --sprint-review S-2025-08A` creates review with sprint_id
    
- `notes new --sprint-retro S-2025-08A` creates retro with sprint_id
    

**Prefill behavior**

- Dates and week_id calculated automatically
    
- `metrics` left blank by default for MVP, you can prefill from a simple CSV later
    

**Creation timing**

- MVP: on-demand only
    
- Optional later: auto-create weekly every Monday at 08:00 America/Los_Angeles
    

**Editor and git**

- Yes for both. Recommended default behavior:
    
    - Create file under `notes/<type>/<year>/...`
        
    - Open with `$EDITOR`
        
    - On save, auto-run `git add` and create a conventional commit
        
        - Daily: `chore(notes): daily 2025-08-13`
            
        - Weekly: `docs(review): weekly 2025-W33`
            
        - Sprint review: `docs(review): sprint S-2025-08A`
            
        - Retro: `docs(retro): sprint S-2025-08A`
            

**File naming**

- Daily: `notes/daily/2025/2025-08-13.md`
    
- Weekly: `notes/weekly/2025/2025-W33.md`
    
- Sprint review: `notes/sprint-review/S-2025-08A.md`
    
- Retro: `notes/retro/S-2025-08A.md`
    

# Quick setup checklist

1. Add these four templates to your repo
    
2. Add a tiny CLI or Make target that copies templates and fills date fields
    
3. Adopt the status lifecycle
    
4. Track the 3 to 5 weekly metrics listed above for two sprints before changing them
    
5. Keep daily `focus` at 3 items
    

If you want, I can draft a small Python or Bash CLI that implements `notes new` with the prefill rules and git commit flow.