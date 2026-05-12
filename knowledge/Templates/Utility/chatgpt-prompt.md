---
type: fleeting
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
tags: [prompt, chatgpt, inbox]
visibility: private
template_id: util-chatgpt-prompt
template_version: 1.0.0
---
<%*
/* ------------------------------------------------------------------
   LLM Prompt Template — Categorized, Slugged, Outcome-Aware
   ------------------------------------------------------------------ */

// Guard: if we're already in a Prompts/ subfolder, skip setup.
if (tp.file.folder(true).startsWith("Prompts/")) {
  return;
}

// --- Step 1: Category ---
const categories = ["dev", "content", "research", "one-off"];
const category = await tp.system.suggester(
  categories,
  categories,
  false,
  "What kind of prompt?"
);
if (!category) { return; }

// --- Step 2: Topic (becomes slug + H1) ---
const topic = await tp.system.prompt("What's this prompt about?");
if (!topic) { await tp.system.alert("Cancelled."); return; }

// --- Slugify ---
const slug = topic
  .toLowerCase()
  .replace(/[^\w\s-]/g, "")    // strip punctuation
  .replace(/\s+/g, "-")        // spaces to hyphens
  .replace(/-+/g, "-")         // collapse runs
  .slice(0, 50);               // hard cap

const date = tp.date.now("YYYY-MM-DD");
const fname = `${slug}-${date}`;
const target = `Prompts/${category}/${fname}`;

// --- Rename + move ---
try {
  await tp.file.rename(fname);
  await tp.file.move(target);
} catch (e) {
  await tp.system.alert("Rename/Move failed: " + e.message);
  return;
}

// --- Body templates per category ---
const bodies = {
  dev: `## The prompt

Let's create a new branch for the next feature: ${topic}.

### P0 — Critical/Unblocker
- Main task: 
- Acceptance criteria:
  - 
  - 

### Next action (this session)
- `,

  content: `## The prompt

Topic: ${topic}

- Platform: 
- Audience: 
- Hook angle: 
- Format (reel, thread, post): 
- CTA: `,

  research: `## The prompt

Question: ${topic}

- Why I'm asking: 
- Sources to check: 
- Output shape I want: 
- Decision this informs: `,

  "one-off": `## The prompt

${topic}`
};

// --- Emit ---
tR += `---
created: ${date}
category: ${category}
status: draft
model: 
project: 
source: 
rating: 
tags: [prompt, ${category}]
---

# ${topic}

${bodies[category]}

## Result
*Fill in after running the prompt.*

- Output artifact: 
- Rating (1-5): 
- What worked: 
- What didn't: 
- Lesson: 
`;
%>