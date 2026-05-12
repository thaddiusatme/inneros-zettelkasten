<%*
const folder   = "Reviews";
const date     = tp.date.now("YYYY-MM-DD");
const sprintId = tp.date.now("YYYY-[W]WW");

/*--- One creation prompt ---*/
const topPriority = await tp.system.prompt("What's the #1 thing that has to happen today?");
if (!topPriority) { return; }

/*--- Rename & move ---*/
let fileName = `daily-${date}`;
if (await app.vault.adapter.exists(`${folder}/${fileName}.md`)) {
  fileName = `daily-${date}-${tp.date.now("HHmm")}`;
}
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);

tR += `---
type: daily
created: ${tp.date.now("YYYY-MM-DD HH:mm")}
status: promoted
tags: [daily, zettelkasten, scrum]
visibility: private
template_id: core-daily
template_version: 2.0.0
sprint_id: ${sprintId}
---

# Daily — ${date}

## Standup
- Yesterday: 
- Today: ${topPriority}
- Blockers: 

## Wins

## Links Added

## Journal

---

## EOD
- Best thing that happened:
- What slowed me down:
- Tomorrow I'll start with:
`;
%>
