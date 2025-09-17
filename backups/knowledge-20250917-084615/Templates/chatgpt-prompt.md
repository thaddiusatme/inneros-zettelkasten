---
type: fleeting
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
tags: [prompt, chatgpt, inbox]
visibility: private
---
<%*
/*------------------------------------------------------------------
  ChatGPT Prompt Template — Interactive Setup (fleeting pattern)
  1) Gather context via prompts
  2) Build file name and path
  3) Rename & move to Inbox/
------------------------------------------------------------------*/
// One-time execution guard to avoid double-run after rename/move
if (tp.file.title && tp.file.title.startsWith("prompt-")) {
  tR += "\n<!-- already processed -->\n";
  return;
}

// Single-question mode to minimize interaction

const feature = await tp.system.prompt("Feature / branch name?");
if (!feature) {
  await tp.system.alert("Cancelled – feature/branch is required.");
  return;
}
const brief = "";
const rules = "";
const blocker = "";
const prev = "";
const current = "";
const fileRef = "";
const learnings = "";

/* Filename + path */
const stamp  = tp.date.now("YYYYMMDD-HHmm");
const fname  = `prompt-${stamp}.md`;
const target = `Inbox/${fname}`;

/* Rename & move */
try {
  await tp.file.rename(fname);
  await tp.file.move(target);
} catch (e) {
  await tp.system.alert("Rename/Move failed – " + e.message);
  return;
}

/* Emit body */
tR += `
## The prompt
Let's create a new branch for the next feature: ${feature}.

### P0 — Critical/Unblocker
- Main Task: {MAIN_P0_TASK}
- Acceptance Criteria:
  - {MEASURABLE_OUTCOME_1}
  - {MEASURABLE_OUTCOME_2}

## Next Action (for this session)
- [ ] {NEXT_ACTION}
`;
%>
