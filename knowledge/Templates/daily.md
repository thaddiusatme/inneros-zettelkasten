---
type: daily
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: promoted
tags: [daily, zettelkasten, scrum]
visibility: private
sprint_id: <% tp.date.now("YYYY-[W]WW") %>
---
<%*
const folder = "Reviews";
try { await app.vault.createFolder(folder); } catch(e) { /* ignore if exists */ }

const date = tp.date.now("YYYY-MM-DD");
let fileName = `daily-${date}`;
let target = `${folder}/${fileName}.md`;
if (await app.vault.adapter.exists(target)) {
  fileName = `daily-${date}-${tp.date.now("HHmm")}`;
}
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
%>

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
