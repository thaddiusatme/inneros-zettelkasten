<%*
const folder = "Reviews";
const weekId = tp.date.now("YYYY-[W]WW");

/*--- One creation prompt ---*/
const headline = await tp.system.prompt("What's the headline for this week? (one sentence)");
if (!headline) { return; }

/*--- Rename & move ---*/
let fileName = `weekly-${weekId}`;
if (await app.vault.adapter.exists(`${folder}/${fileName}.md`)) {
  fileName = `weekly-${weekId}-${tp.date.now("HHmm")}`;
}
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);

const start = tp.date.now("YYYY-MM-DD", -7);
const end   = tp.date.now("YYYY-MM-DD");

tR += `---
type: weekly
week_id: ${weekId}
period_start: ${start}
period_end: ${end}
status: promoted
tags: [weekly-review, review]
visibility: private
template_id: core-weekly-review
template_version: 2.0.0
---

# Weekly Review — ${weekId}

## Highlights
- ${headline}
- 
- 

## Carry Forward
*What worked that I want to keep doing?*

## Drop or Change
*What cost me time or energy without return?*

## Bridges Created
- [[]] ↔ [[]] — why this connection matters

## Next Week
- Outcome 1:
- Outcome 2:
- Outcome 3:

---

## Sprint Reflection
- Did I work on what mattered, or just what felt urgent?
- What kept showing up as a blocker?
- One experiment for next sprint:
- Notes promoted this week: 
`;
%>
