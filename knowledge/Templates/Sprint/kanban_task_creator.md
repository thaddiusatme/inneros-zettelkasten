<%*
/*------------------------------------------------------------------
  1. Capture Task Details
------------------------------------------------------------------*/
const title = await tp.system.prompt("Task Title");
if (!title) { new Notice("Cancelled: No title provided."); return; }

const swimlanes = ["🟢 Revenue", "🔵 Audience", "⚙️ Systems"];
const swimlane = await tp.system.suggester(swimlanes, swimlanes, false, "Select Swimlane");
if (!swimlane) { new Notice("Cancelled: No swimlane selected."); return; }

const sprintId = await tp.system.prompt("Sprint ID", "Sprint 1");
if (!sprintId) { new Notice("Cancelled: No sprint ID provided."); return; }

const columns = ["Backlog", "To Do", "In Progress", "Done"];
const status = await tp.system.suggester(columns, columns, false, "Select Column") || "Backlog";

const dod = await tp.system.prompt("Definition of Done (1-2 lines)");

/*------------------------------------------------------------------
  2. Build File Name & Path
------------------------------------------------------------------*/
const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
// Assuming "Projects" is the root for sprints
const targetFolder = `Projects/${sprintId}/Tasks`;
const targetPath = `${targetFolder}/${slug}`;

/*------------------------------------------------------------------
  3. Move File
------------------------------------------------------------------*/
/*------------------------------------------------------------------
  3. Move File & Update Board
------------------------------------------------------------------*/
try {
  await tp.file.move(targetPath);
  
  // Board filename must match exactly — update this if your board is named differently
  const boardPath = `Projects/${sprintId}/Sprint Board.md`;
  const boardFile = tp.file.find_tfile(boardPath);
  
  if (boardFile) {
    let boardContent = await app.vault.read(boardFile);
    const header = `## ${status}`;
    const taskLink = `- [ ] [[${slug}]]`;
    
    if (boardContent.includes(header)) {
      // Insert after the header
      const newContent = boardContent.replace(header, `${header}\n\n${taskLink}`);
      await app.vault.modify(boardFile, newContent);
      new Notice(`Added [[${slug}]] to ${status} in ${boardPath}`);
    } else {
      new Notice(`Header "${header}" not found in ${boardPath}. Task created but not added to board.`);
    }
  } else {
    new Notice(`Board file not found at ${boardPath}`);
  }

} catch (e) {
  console.error("Failed to move file or update board:", e);
  new Notice(`Error: ${e.message}`);
}
%>---
type: task
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: <% status %>
priority: Medium
swimlane: <% swimlane %>
sprint: <% sprintId %>
tags: [task, <% swimlane.split(" ")[1].toLowerCase() %>]
---
# <% title %>

## Description


<%* if (dod) { -%>
## Definition of Done
- [ ] <% dod %>
<%* } -%>

## Acceptance Criteria
- [ ] 
