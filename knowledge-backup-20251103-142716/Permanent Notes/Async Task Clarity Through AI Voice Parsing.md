**Type**: 📌 Permanent Note  
**Created**: 2025-06-30  
**Tags**: #permanent #llm #workflow #sop #voxer #notion #automation

---

## Core Idea

**Voice-based task intake can be transformed into structured, review-ready actions using an automated LLM pipeline.**  
In Brit’s business, client asks often arrive via voice (Voxer). To manage these fluid, often ambiguous requests, an LLM-driven system listens, transcribes, summarizes, prioritizes, and checks for missing details — then logs everything into Notion with flags for follow-up.

## Why It Matters

Voice input is fast and natural for the sender, but chaotic for the receiver. Without structure, requests get lost, misunderstood, or delayed. By integrating Whisper and GPT in a Make.com pipeline, you can:

- Convert unstructured voice into usable project inputs
    
- Detect gaps in clarity and actionability
    
- Create a searchable Notion archive
    
- Send daily digests for review and planning
    

This system builds clarity, accountability, and async visibility — all from spontaneous voice notes.

## Pipeline Design (Phase One)

### **1. Input Source**

- Voxer (manually uploaded or routed to webhook)
    

### **2. LLM Pipeline Stages**

1. **Transcribe** with Whisper
    
2. **Summarize** in 1–2 sentences
    
3. **Priority Guess**: High, Medium, or Low
    
4. **Gap Check**:
    
    - Is there an **action verb**?
        
    - Is a **date or urgency** specified?
        
    - Is there enough **context** for someone else to take action?
        
5. If any gap exists → Tag as `Needs Clarification`
    

---

### **3. Output Structure: Notion Record**

- **Title**: auto-generated from summary or keywords
    
- **Transcript**: full message (Markdown)
    
- **Summary**
    
- **Priority**: select field
    
- **Status**: defaults to `Inbox`
    
- **Tags**: e.g., `Needs Clarification`
    
- **Source**: `Voxer`
    

---

### **4. Review & Notification**

- **Brit Review View**: filtered Notion view with clarification tags
    
- **Digest Email**: sent daily at 08:00 PT with links to new Notion pages
    

---

## SOP Integration

This workflow is being formalized as the **Task Intake Phase** in Brit’s Support SOP.

## Two-Hour Build Plan

|Step|Task|Time|
|---|---|---|
|1|Create Notion Intake Board|10 min|
|2|Make.com: webhook → Whisper → Notion|25 min|
|3|Add formula flags + Brit Review view|15 min|
|4|Build Daily Digest scenario|10 min|
|5|Record Loom demo walkthrough|20 min|

---

## Links

- Related: [[Whisper + LLM Prompt Engineering]], [[Voice-First Ops for Lean Teams]], [[Support SOP System Map]]
    
- Source: Brit's Support Workflow, June 2025