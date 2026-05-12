<%*
/*--- 1. Capture the thought ---*/
const rawThought = await tp.system.prompt("What do you want to remember? (say it as a full thought)");
if (!rawThought) { return; }

/*--- 2. Thought type ---*/
const thoughtTypes = ["Realization", "Opportunity", "Problem / Tension", "Question to explore"];
const thoughtType = await tp.system.suggester(
  thoughtTypes, thoughtTypes, true, "What kind of thought is this?"
);
if (!thoughtType) { return; }

/*--- 3. Category ---*/
const categoryLabels = ["AHS / Business", "Content", "Technical / Dev", "Other"];
const category = await tp.system.suggester(
  categoryLabels, categoryLabels, true, "What area does this belong to?"
);
if (!category) { return; }

/*--- Tags ---*/
const tagMap = {
  "AHS / Business":  ["fleeting", "inbox", "ahs", "business"],
  "Content":         ["fleeting", "inbox", "content", "ideas"],
  "Technical / Dev": ["fleeting", "inbox", "technical", "dev"],
  "Other":           ["fleeting", "inbox"],
};
const tags = tagMap[category] || ["fleeting", "inbox"];

/*--- File name & move ---*/
const slug  = rawThought.toLowerCase()
                        .replace(/[^a-z0-9]+/g, "-")
                        .replace(/(^-|-$)/g, "")
                        .split("-").slice(0, 8).join("-");
const stamp = tp.date.now("YYYYMMDD-HHmm");
const fname = `fleeting-${stamp}-${slug}`;

try {
  await tp.file.rename(fname);
  await tp.file.move(`Inbox/${fname}`);
} catch (e) {
  await tp.system.alert("Move failed – " + e.message);
  return;
}

/*--- Note content ---*/
tR += `---
type: fleeting
created: ${tp.date.now("YYYY-MM-DD HH:mm")}
status: inbox
tags: [${tags.join(", ")}]
category: ${category}
thought_type: ${thoughtType}
source: keyboard
visibility: private
template_id: core-fleeting
template_version: 1.3.0
---

${rawThought}

*${thoughtType}*

---
- [ ] Promote to permanent note?
`;
%>
