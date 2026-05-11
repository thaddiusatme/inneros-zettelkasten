
**Why it matters**  
Efficiently organizing fleeting notes into actionable, permanent knowledge assets helps drive clarity and speed in decision making, directly supporting faster execution for 2025 business and revenue goals. This structured triage process ensures key information is not lost and is instantly actionable for any team member or automation.

**Desired outcome**  
- > 90% of actionable fleeting notes are reviewed and promoted within 24 hours  
- Reduced information loss from scattered note-taking  
- Consistent, reusable workflow for note promotion across all projects

**Key requirements**  
- Clearly defined triage criteria and template  
- Action-oriented drafting guidelines  
- Seamless tagging for downstream automation  
- Usable in Markdown for interoperability

**Open questions / research**  
- Are additional triage criteria needed for specific teams?  
- What automation options exist for this triage in current note apps?  
- Can feedback loops improve template adoption and output quality?

**Next actions**  
1. Implement template in primary notes app (e.g. Obsidian, Notion)  
2. Pilot triage workflow with recent fleeting notes  
3. Collect feedback from core team after 2 weeks  
4. Share workflow template with wider team via documentation  
5. Review automation opportunities post-pilot

## Tag recommendations  
#project #active #knowledge_management #automation #template #triage #evergreen #10k_mrr_goal

# Prompt
**Copy‑and‑paste prompt template**

> **System / role**  
> You are a knowledge‑management assistant helping me triage fleeting notes. Follow the steps exactly.
> 
> **User input**
> 
> ```
> {PASTE FLEETING NOTE HERE}  
> ```
> 
> **Step‑by‑step instructions**
> 
> 1. **Evergreen test** – Fill the table below with Yes or No and a short note.  
>     | Criterion | Yes/No | Note |  
>     | Strategic fit with my 2025 goals | | |  
>     | Unique or insightful idea | | |  
>     | Concrete next actions present | | |  
>     | Reusable reference value | | |
>     
> 2. **Decision** – If at least three cells are Yes, say “Promote to permanent note,” otherwise “Keep as fleeting” and stop.
>     
> 3. **If promoted, draft this structure**
>     
>     1. **Title** – concise, action oriented.
>         
>     2. **Why it matters** – 2 to 3 sentences linking to revenue or audience objectives.
>         
>     3. **Desired outcome** – bullet list of measurable results.
>         
>     4. **Key requirements** – bullet list of must‑haves.
>         
>     5. **Open questions / research** – bullet list.
>         
>     6. **Next actions** – 3 to 5 atomic tasks.
>         
> 4. **Tag recommendations** – Return 5 to 8 tags in one line, mixing:
>     
>     - project or status (`#project`, `#active`)
>         
>     - channel or format (`#threads`, `#instagram`)
>         
>     - function (`#news_curation`, `#automation`)
>         
>     - tool or tech (`#claude`, `#make_com`)
>         
>     - strategic link (`#10k_mrr_goal`)
>         
> 5. Output everything in Markdown, no extra commentary, no em dashes.
>     

> **Expected output example**
> 
> ```markdown
> ## Evergreen test  
> | Criterion | Yes/No | Note |  
> | Strategic fit with my 2025 goals | Yes | Helps content scaling for Threads |  
> | Unique or insightful idea | Yes | Identifies gap in news flow |  
> | Concrete next actions present | Yes | Needs sourcing and template work |  
> | Reusable reference value | Yes | Can guide future content bots |  
> 
> **Decision**  
> Promote to permanent note
> 
> ## Permanent note draft
> **Title**  
> Claude News Bot → Threads and IG Carousel
> **Why it matters**  
> ...
> ...
> ## Tag recommendations  
> #project #active #news_curation #automation #threads #instagram #claude
> ```