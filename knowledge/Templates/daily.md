<%*
const date = tp.date.now("YYYY-MM-DD");
const fileName = `daily-${date}`;
const folder = "Reviews";
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
%>
---
type: daily
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: promoted
tags: [daily, zettelkasten, scrum]
visibility: private
sprint_id: <% tp.date.now("YYYY-[W]WW") %>
---

# Daily Note — <% tp.date.now("YYYY-MM-DD") %>

## Focus
- <1 to 3 bullets for today’s single theme>

## Standup
- Yesterday: 
- Today: 
- Blockers: 

## Links Added
- [[note-id-or-title]] short why it matters

## Wins
- <fast wins and tiny proofs>

## Next
- <top 3 actions, smallest viable steps>

## Journal
- <freeform>

## EOD Micro Retro
- What moved the needle:
- What felt hard:
- What to change tomorrow:
