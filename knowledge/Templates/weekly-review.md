<%*
await tp.file.move(`Inbox/${tp.file.title}`);

const weekId = tp.date.now("YYYY-[W]WW");
const fileName = `weekly-${weekId}`;
const folder = "Reviews"; // optional — change or remove if you don’t want a folder
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
%>
---
type: weekly
week_id: <% tp.date.now("YYYY-[W]WW") %>
period_start: <% tp.date.now("YYYY-MM-DD", -7) %>
period_end: <% tp.date.now("YYYY-MM-DD") %>
status: promoted
tags: [weekly, review, retrospective, scrum]
visibility: private
---

# Weekly Review — <% tp.date.now("YYYY-[W]WW") %>

## Highlights
- <3 to 5 outcomes, not activities>

## Metrics
- Notes created: <n>
- Orphans before → after: <n> → <n>
- Link density avg: <n>
- Stale notes touched: <n>
- Focus days this week: <n>

## Bridges Created
- [[note-a]] ↔ [[note-b]] why the link matters
- [[note-c]] ↔ [[note-d]]

## What Went Well
- 

## What I Will Improve
- 

## Next Week Goals
- Outcome 1:
- Outcome 2:
- Outcome 3:

## Sprint Reflection
- Did scope match capacity
- Top blocker pattern
- Experiment to try next sprint
